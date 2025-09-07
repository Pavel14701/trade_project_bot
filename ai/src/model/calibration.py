import torch
import torch.nn as nn
import torch.optim as optim
from typing import Optional

class TemperatureScaler(nn.Module):
    def __init__(self) -> None:
        super().__init__() # type: ignore
        self.log_temp = nn.Parameter(torch.zeros(()))

    def forward(self, logits: torch.Tensor) -> torch.Tensor:
        temp = torch.exp(self.log_temp) + 1e-6
        return logits / temp

def fit_temperature_scaler(
    logits: torch.Tensor,
    targets: torch.Tensor,
    max_iter: int = 500,
    device: torch.device = torch.device("cuda"),
    verbose: bool = False,
    class_weights: Optional[torch.Tensor] = None
) -> TemperatureScaler:
    assert logits.ndim == 2 and logits.size(1) > 1, "Expected [B, C] logits"
    assert targets.ndim == 1, "Expected [B] targets"
    logits, targets = logits.to(device), targets.to(device)
    scaler = TemperatureScaler().to(device)
    scaler.eval()
    optimizer = optim.LBFGS([scaler.log_temp], lr=0.05, max_iter=max_iter)
    loss_fn = nn.CrossEntropyLoss(weight=class_weights.to(device) if class_weights is not None else None)
    def closure() -> torch.Tensor:
        optimizer.zero_grad()
        loss = loss_fn(scaler(logits), targets)
        loss.backward()
        return loss
    optimizer.step(closure) # type: ignore
    if verbose:
        temp = torch.exp(scaler.log_temp).item()
        print(f"[TempScaler] Final temperature: {temp:.4f}")
    return scaler


class PlattCalibrator(nn.Module):
    def __init__(self) -> None:
        super().__init__() # type: ignore
        self.a = nn.Parameter(torch.tensor(1.0))
        self.b = nn.Parameter(torch.tensor(0.0))

    def forward(self, p: torch.Tensor) -> torch.Tensor:
        eps = 1e-6
        p_clamped = p.clamp(eps, 1 - eps)
        logit = torch.log(p_clamped) - torch.log1p(-p_clamped)
        return torch.sigmoid(self.a * logit + self.b)

    def forward_logits(self, logits: torch.Tensor) -> torch.Tensor:
        return torch.sigmoid(self.a * logits + self.b)


def fit_platt_scaler(
    p: torch.Tensor,
    y: torch.Tensor,
    lr: float = 0.05,
    steps: int = 1000,
    device: torch.device = torch.device("cuda"),
    verbose: bool = False,
    early_stop: int = 20
) -> PlattCalibrator:
    p, y = p.to(device), y.to(device)
    model = PlattCalibrator().to(device)
    model.eval()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.BCELoss()
    best_loss = float("inf")
    wait = 0
    for _ in range(steps):
        optimizer.zero_grad()
        p_cal = model(p)
        loss = loss_fn(p_cal, y.float())
        loss.backward()
        optimizer.step() # type: ignore
        if loss.item() < best_loss:
            best_loss = loss.item()
            wait = 0
        else:
            wait += 1
            if wait >= early_stop:
                break
    if verbose:
        print(f"[Platt] Final a: {model.a.item():.4f}, b: {model.b.item():.4f}, loss: {best_loss:.4f}")
    return model


def fit_batch_temperature_scalers(
    logits_list: list[torch.Tensor],
    targets_list: list[torch.Tensor],
    device: torch.device = torch.device("cuda")
) -> list[TemperatureScaler]:
    return [fit_temperature_scaler(l, t, device=device) for l, t in zip(logits_list, targets_list)]
