# src/ai/inference/utils.py

import torch
import pandas as pd
import numpy as np
import numpy.typing as npt
from typing import Tuple, cast

def to_tensor(
    num: pd.DataFrame,
    cat: pd.DataFrame,
    device: torch.device = torch.device("cuda")
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Converts numeric and categorical DataFrames into device-aware PyTorch tensors.

    Assumes numeric values are float32 and categorical values are int64.
    Raises an error if either input is empty.

    Parameters:
        num (pd.DataFrame): Numeric features.
        cat (pd.DataFrame): Categorical features.
        device (torch.device): Target device for tensor allocation.

    Returns:
        Tuple[torch.Tensor, torch.Tensor]: (x_num, x_cat) tensors on the specified device.
    """
    if num.empty or cat.empty:
        raise ValueError("Empty input to to_tensor")

    # Явная типизация массивов
    num_array = cast(npt.NDArray[np.float32], num.values) # type: ignore[reportUnknownMemberType]
    cat_array = cast(npt.NDArray[np.int64], cat.values) # type: ignore[reportUnknownMemberType]
    num_tensor = torch.from_numpy(num_array).to(device=device) # type: ignore[reportUnknownMemberType]
    cat_tensor = torch.from_numpy(cat_array).to(device=device) # type: ignore[reportUnknownMemberType]

    return num_tensor, cat_tensor

def calibrated_sigmoid(
    x: torch.Tensor, 
    alpha: float = 1.0
) -> torch.Tensor:
    """
    Applies a calibrated sigmoid transformation to the input tensor.

    Useful for scaling logits in binary classification or decision models.

    Parameters:
        x (torch.Tensor): Input logits.
        alpha (float): Scaling factor for calibration.

    Returns:
        torch.Tensor: Sigmoid-transformed probabilities.
    """
    return 1 / (1 + torch.exp(-alpha * x))

def pad_batch(
    tensors: list[torch.Tensor], 
    pad_value: float = 0.0
) -> torch.Tensor:
    """
    Pads a list of variable-length tensors into a uniform batch.

    Uses PyTorch's pad_sequence with batch-first layout.

    Parameters:
        tensors (list[torch.Tensor]): List of tensors to pad.
        pad_value (float): Value used for padding.

    Returns:
        torch.Tensor: Padded tensor of shape [B, T, D] or [B, T].
    """
    from torch.nn.utils.rnn import pad_sequence
    return pad_sequence(tensors, batch_first=True, padding_value=pad_value)
