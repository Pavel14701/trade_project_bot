from typing import Callable

import torch
from inference.utils import calibrated_sigmoid
from torch.nn import Module
from torch.optim import Optimizer


class Trainer:
    """
    Training and evaluation wrapper for tabular models.

    Handles forward passes, loss computation, optimization, and inference.
    Supports calibrated sigmoid output for binary tasks.

    Parameters:
        model (Module): PyTorch model with forward(x_num, x_cat) interface.
        optimizer (Optimizer): Optimizer for model parameters.
        loss_fn (Callable): Loss function accepting (probs, targets).
        device (torch.device): Target device for training and inference.
        alpha (float): Scaling factor for calibrated sigmoid (default: 1.0).
    """
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

    def train_epoch(self, dataloader) -> float:
        """
        Runs one training epoch over the provided dataloader.

        Performs forward pass, computes loss, backpropagates gradients,
        and updates model parameters.

        Parameters:
            dataloader: PyTorch DataLoader yielding batches with keys:
                - "x_num": numeric features
                - "x_cat": categorical features
                - "target": ground truth labels

        Returns:
            float: Average loss over the epoch.
        """
        self.model.train()
        total_loss = 0.0
        for batch in dataloader:
            x_num = batch["x_num"]
            x_cat = batch["x_cat"]
            y_true = batch["target"]
            self.optimizer.zero_grad()
            logits = self.model(x_num, x_cat)
            probs = calibrated_sigmoid(logits.squeeze(), alpha=self.alpha)
            loss = self.loss_fn(probs, y_true)
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()
        return total_loss / len(dataloader)

    def evaluate(self, dataloader, targets: torch.Tensor) -> torch.Tensor:
        """
        Runs model inference over the provided dataloader.

        Applies calibrated sigmoid to logits and returns concatenated predictions.

        Parameters:
            dataloader: PyTorch DataLoader yielding batches with keys:
                - "x_num": numeric features
                - "x_cat": categorical features
            targets (torch.Tensor): Ground truth labels 
              (unused, kept for compatibility).

        Returns:
            torch.Tensor: Concatenated predictions of shape [B].
        """
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
