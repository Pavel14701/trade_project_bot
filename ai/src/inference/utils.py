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
    if num.empty or cat.empty:
        raise ValueError("Empty input to to_tensor")

    # Явная типизация массивов
    num_array = cast(npt.NDArray[np.float32], num.values) # type: ignore[reportUnknownMemberType]
    cat_array = cast(npt.NDArray[np.int64], cat.values) # type: ignore[reportUnknownMemberType]
    num_tensor = torch.from_numpy(num_array).to(device=device) # type: ignore[reportUnknownMemberType]
    cat_tensor = torch.from_numpy(cat_array).to(device=device) # type: ignore[reportUnknownMemberType]

    return num_tensor, cat_tensor

def calibrated_sigmoid(x: torch.Tensor, alpha: float = 1.0) -> torch.Tensor:
    return 1 / (1 + torch.exp(-alpha * x))

def pad_batch(tensors: list[torch.Tensor], pad_value: float = 0.0) -> torch.Tensor:
    from torch.nn.utils.rnn import pad_sequence
    return pad_sequence(tensors, batch_first=True, padding_value=pad_value)
