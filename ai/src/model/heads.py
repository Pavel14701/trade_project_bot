import torch
import torch.nn as nn
from typing import Literal

class BaseHead(nn.Module):
    """
    Generic output head for tabular models.

    Applies layer normalization, dropout, and a final linear projection.
    Supports both regression and classification tasks depending on output dimension.

    Parameters:
        d_model (int): Input feature dimension.
        out_dim (int): Output dimension (e.g., 1 for binary, >1 for multi-class).
        dropout (float): Dropout rate applied before the final layer.
    """
    def __init__(self, d_model: int, out_dim: int, dropout: float = 0.1) -> None:
        super().__init__() # type: ignore
        self.head = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Dropout(dropout),
            nn.Linear(d_model, out_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Applies the output head to the input tensor.

        If the output dimension is 1, squeezes the last dimension for compatibility
        with binary loss functions. This avoids collapsing the batch dimension when
        batch size is 1, ensuring consistent output shape.

        Parameters:
            x (torch.Tensor): Input tensor of shape [B, D].

        Returns:
            torch.Tensor: Output tensor of shape [B] or [B, out_dim].
        """
        out = self.head(x)
        return out.squeeze(-1) if out.shape[-1] == 1 else out



class SignalHead(BaseHead):
    """
    Multi-class classification head for signal prediction.

    Projects input features to 3 output classes (e.g., buy/hold/sell).

    Parameters:
        d_model (int): Input feature dimension.
        dropout (float): Dropout rate.
    """
    def __init__(self, d_model: int, dropout: float = 0.1) -> None:
        super().__init__(d_model, out_dim=3, dropout=dropout)

class SuccessHead(BaseHead):
    """
    Binary classification head for success prediction.

    Projects input features to a single output logit.

    Parameters:
        d_model (int): Input feature dimension.
        dropout (float): Dropout rate.
    """
    def __init__(self, d_model: int, dropout: float = 0.1) -> None:
        super().__init__(d_model, out_dim=1, dropout=dropout)

class MultiTaskHead(nn.Module):
    """
    Composite head for multi-task learning.

    Routes input through either the signal or success head depending on the task.
    Useful for shared encoders with task-specific output logic.

    Parameters:
        d_model (int): Input feature dimension.
        dropout (float): Dropout rate shared across both heads.
    """
    def __init__(self, d_model: int, dropout: float = 0.1) -> None:
        super().__init__() # type: ignore
        self.signal = SignalHead(d_model, dropout)
        self.success = SuccessHead(d_model, dropout)

    def forward(
        self, 
        x: torch.Tensor, 
        task: Literal["signal", "success"]
    ) -> torch.Tensor:
        """
        Applies the appropriate output head based on the task name.

        Parameters:
            x (torch.Tensor): Input tensor of shape [B, D].
            task (Literal["signal", "success"]): Task identifier.

        Returns:
            torch.Tensor: Output tensor from the selected head.

        Raises:
            ValueError: If an unknown task name is provided.
        """
        if task == "signal":
            return self.signal(x)
        elif task == "success":
            return self.success(x)
        else:
            raise ValueError(f"Unknown task: {task}")
