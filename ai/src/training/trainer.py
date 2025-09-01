import torch
from torch.nn import Module
from torch.optim import Optimizer
from typing import Callable, Optional
from inference.utils import calibrated_sigmoid

class Trainer:
    def __init__(
        self,
        model: Module,
        optimizer: Optimizer,
        loss_fn: Callable[[torch.Tensor, torch.Tensor], torch.Tensor],
        device: torch.device,
        alpha: float = 1.0
    ) -> None:
        self.model = model.to(device)
        self.optimizer = optimizer
        self.loss_fn = loss_fn
        self.device = device
        self.alpha = alpha

    def train_epoch(self, dataloader, targets: torch.Tensor) -> float:
        self.model.train()
        total_loss = 0.0

        for batch_idx, batch in enumerate(dataloader):
            x_num = batch["x_num"]
            x_cat = batch["x_cat"]

            self.optimizer.zero_grad()
            logits = self.model(x_num, x_cat)
            probs = calibrated_sigmoid(logits.squeeze(), alpha=self.alpha)
            loss = self.loss_fn(probs, targets[batch_idx * len(probs):(batch_idx + 1) * len(probs)])
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()

        return total_loss / len(dataloader)

    def evaluate(self, dataloader, targets: torch.Tensor) -> torch.Tensor:
        self.model.eval()
        all_preds = []

        with torch.no_grad():
            for batch in dataloader:
                x_num = batch["x_num"]
                x_cat = batch["x_cat"]
                logits = self.model(x_num, x_cat)
                probs = calibrated_sigmoid(logits.squeeze(), alpha=self.alpha)
                all_preds.append(probs.cpu())

        return torch.cat(all_preds, dim=0)
