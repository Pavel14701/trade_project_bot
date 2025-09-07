import torch
import torch.nn as nn
from typing import Literal

class BaseHead(nn.Module):
    def __init__(self, d_model: int, out_dim: int, dropout: float = 0.1) -> None:
        super().__init__() # type: ignore
        self.head = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Dropout(dropout),
            nn.Linear(d_model, out_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(x).squeeze(-1) if self.head[-1].out_features == 1 else self.head(x)

class SignalHead(BaseHead):
    def __init__(self, d_model: int, dropout: float = 0.1) -> None:
        super().__init__(d_model, out_dim=3, dropout=dropout)

class SuccessHead(BaseHead):
    def __init__(self, d_model: int, dropout: float = 0.1) -> None:
        super().__init__(d_model, out_dim=1, dropout=dropout)

class MultiTaskHead(nn.Module):
    def __init__(self, d_model: int, dropout: float = 0.1) -> None:
        super().__init__() # type: ignore
        self.signal = SignalHead(d_model, dropout)
        self.success = SuccessHead(d_model, dropout)

    def forward(self, x: torch.Tensor, task: Literal["signal", "success"]) -> torch.Tensor:
        if task == "signal":
            return self.signal(x)
        elif task == "success":
            return self.success(x)
        else:
            raise ValueError(f"Unknown task: {task}")
