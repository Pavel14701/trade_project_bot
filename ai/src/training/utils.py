import torch
import random
import numpy as np
from torch import Tensor
from typing import Dict

def set_seed(seed: int) -> None:
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def compute_metrics(preds: Tensor, targets: Tensor) -> Dict[str, float]:
    preds_bin = (preds > 0.5).int()
    targets_bin = targets.int()
    correct = (preds_bin == targets_bin).sum().item()
    total = targets.numel()
    accuracy = correct / total
    return {"accuracy": accuracy}

def move_to_device(batch: dict[str, Tensor], device: torch.device) -> dict[str, Tensor]:
    return {k: v.to(device) for k, v in batch.items()}
