import torch
import random
import numpy as np
from torch import Tensor
from typing import Dict

def set_seed(seed: int) -> None:
    """
    Sets global random seed for reproducibility.

    Applies the seed to Python's `random`, NumPy, and PyTorch (CPU and CUDA).

    Parameters:
        seed (int): Seed value to apply.
    """
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def compute_metrics(
    preds: Tensor, 
    targets: Tensor
) -> Dict[str, float]:
    """
    Computes binary classification accuracy.

    Thresholds predictions at 0.5 and compares against ground truth labels.

    Parameters:
        preds (Tensor): Predicted probabilities or logits of shape [B].
        targets (Tensor): Ground truth binary labels of shape [B].

    Returns:
        Dict[str, float]: Dictionary with key "accuracy".
    """
    preds_bin = (preds > 0.5).int()
    targets_bin = targets.int()
    correct = (preds_bin == targets_bin).sum().item()
    total = targets.numel()
    accuracy = correct / total
    return {"accuracy": accuracy}

def move_to_device(
    batch: dict[str, Tensor], 
    device: torch.device
) -> dict[str, Tensor]:
    """
    Moves all tensors in a batch dictionary to the specified device.

    Parameters:
        batch (dict[str, Tensor]): Dictionary of named tensors.
        device (torch.device): Target device (e.g., "cuda" or "cpu").

    Returns:
        dict[str, Tensor]: Dictionary with tensors moved to the target device.
    """
    return {k: v.to(device) for k, v in batch.items()}
