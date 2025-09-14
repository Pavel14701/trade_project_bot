# src/ai/model/calibration.py

import torch
import torch.nn as nn
import torch.optim as optim
from typing import Optional

class TemperatureScaler(nn.Module):
    """
    Module for temperature scaling of logits.

    Learns a single scalar temperature parameter to calibrate model confidence
    by dividing logits before applying softmax or sigmoid.

    Attributes:
        log_temp (nn.Parameter): Logarithm of the temperature value.
    """
    def __init__(self) -> None:
        super().__init__() # type: ignore
        self.log_temp = nn.Parameter(torch.zeros(()))

    def forward(self, logits: torch.Tensor) -> torch.Tensor:
        """
        Applies temperature scaling to input logits.

        Parameters:
            logits (torch.Tensor): Raw model logits of shape [B, C].

        Returns:
            torch.Tensor: Scaled logits.
        """
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
    """
    Fits a TemperatureScaler using cross-entropy minimization.

    Uses LBFGS optimization to learn a temperature parameter that improves
    calibration of predicted probabilities.

    Parameters:
        logits (torch.Tensor): Logits of shape [B, C].
        targets (torch.Tensor): Ground truth labels of shape [B].
        max_iter (int): Maximum number of LBFGS iterations.
        device (torch.device): Device for computation.
        verbose (bool): If True, prints final temperature.
        class_weights (Optional[torch.Tensor]): Optional class weights for loss.

    Returns:
        TemperatureScaler: Fitted temperature scaling module.
    """
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
    """
    Module for Platt scaling of probabilities or logits.

    Learns a linear transformation in logit space to calibrate binary predictions.

    Attributes:
        a (nn.Parameter): Slope parameter.
        b (nn.Parameter): Bias parameter.
    """
    def __init__(self) -> None:
        super().__init__() # type: ignore
        self.a = nn.Parameter(torch.tensor(1.0))
        self.b = nn.Parameter(torch.tensor(0.0))

    def forward(self, p: torch.Tensor) -> torch.Tensor:
        """
        Applies Platt scaling to input probabilities.

        Converts probabilities to logits, applies affine transformation,
        and returns calibrated probabilities.

        Parameters:
            p (torch.Tensor): Input probabilities in [0, 1].

        Returns:
            torch.Tensor: Calibrated probabilities.
        """
        eps = 1e-6
        p_clamped = p.clamp(eps, 1 - eps)
        logit = torch.log(p_clamped) - torch.log1p(-p_clamped)
        return torch.sigmoid(self.a * logit + self.b)

    def forward_logits(self, logits: torch.Tensor) -> torch.Tensor:
        """
        Applies Platt scaling directly to logits.

        Parameters:
            logits (torch.Tensor): Raw logits.

        Returns:
            torch.Tensor: Calibrated probabilities.
        """
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
    """
    Fits a PlattCalibrator using binary cross-entropy loss.

    Optimizes parameters to improve calibration of predicted probabilities.

    Parameters:
        p (torch.Tensor): Input probabilities of shape [B].
        y (torch.Tensor): Ground truth binary labels of shape [B].
        lr (float): Learning rate.
        steps (int): Maximum number of optimization steps.
        device (torch.device): Device for computation.
        verbose (bool): If True, prints final parameters and loss.
        early_stop (int): Number of steps without improvement before stopping.

    Returns:
        PlattCalibrator: Fitted calibration module.
    """
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
    """
    Fits temperature scalers independently for each batch.

    Useful for per-asset or per-class calibration in multi-head setups.

    Parameters:
        logits_list (list[torch.Tensor]): List of logits tensors.
        targets_list (list[torch.Tensor]): List of corresponding label tensors.
        device (torch.device): Device for computation.

    Returns:
        list[TemperatureScaler]: List of fitted scalers.
    """
    return [fit_temperature_scaler(l, t, device=device) for l, t in zip(logits_list, targets_list)]
