from typing import TypedDict, Callable, Optional, Any
import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from model.column_tokenizer import ColumnTokenizer

class Sample(TypedDict):
    """
    Typed representation of a single training sample.

    Fields:
        tokens (torch.Tensor): Tokenized representation of the input row.
        asset_id (str): Identifier of the asset (e.g., "AAPL", "BTC-USD").
        label (int): Target label for supervised learning.
    """
    tokens: torch.Tensor
    asset_id: str
    label: int

class MultiAssetDataset(Dataset[Sample]):
    """
    Dataset wrapper for multi-asset tabular data.

    Applies optional row-level transformations and tokenizes each row using a ColumnTokenizer.
    Returns structured samples compatible with downstream training pipelines.

    Parameters:
        df (pd.DataFrame): Input dataframe containing asset_id, label, and feature columns.
        tokenizer (ColumnTokenizer): Tokenizer used to convert rows into token tensors.
        device (torch.device): Target device for tensor allocation.
        transform (Optional[Callable]): Optional row-wise transformation applied before tokenization.
    """
    def __init__(
        self,
        df: pd.DataFrame,
        tokenizer: ColumnTokenizer,
        device: torch.device = torch.device("cpu"),
        transform: Optional[Callable[[pd.Series[Any]], pd.Series[Any]]] = None
    ):
        self.df = df.reset_index(drop=True)
        self.tokenizer = tokenizer
        self.device = device
        self.transform = transform

    def __len__(self) -> int:
        """
        Returns the number of samples in the dataset.

        Returns:
            int: Total number of rows in the input dataframe.
        """
        return len(self.df)

    def __getitem__(self, idx: int) -> Sample:
        """
        Retrieves and tokenizes a single row from the dataset.

        Applies optional transformation, tokenizes the row, and returns a structured sample.

        Parameters:
            idx (int): Row index.

        Returns:
            Sample: Dictionary containing tokens, asset_id, and label.
        """
        row: pd.Series[Any] = self.df.iloc[idx] # type: ignore[reportUnknownVariableType]
        if self.transform:
            row = self.transform(row)
        tokens = self.tokenizer.tokenize(row, device=self.device) # type: ignore[reportUnknownVariableType]
        asset_id = row["asset_id"]
        label = int(row["label"])
        return {
            "tokens": tokens,
            "asset_id": asset_id,
            "label": label
        }

def collate_fn(batch: list[Sample]) -> dict[str, torch.Tensor | list[str]]:
    """
    Collates a batch of samples into tensors for model input.

    Stacks token tensors, converts labels to a tensor, and preserves asset IDs as a list.

    Parameters:
        batch (list[Sample]): List of individual samples.

    Returns:
        dict[str, torch.Tensor | list[str]]: Batched tokens, labels, and asset_ids.
    """
    tokens = torch.stack([b["tokens"] for b in batch])
    labels = torch.tensor([b["label"] for b in batch], dtype=torch.long)
    asset_ids = [b["asset_id"] for b in batch]
    return {
        "tokens": tokens,
        "labels": labels,
        "asset_ids": asset_ids
    }

def build_dataloader(
    df: pd.DataFrame,
    tokenizer: ColumnTokenizer,
    batch_size: int = 64,
    shuffle: bool = True,
    num_workers: int = 0,
    transform: Optional[Callable[[pd.Series[Any]], pd.Series[Any]]] = None,
    device: torch.device = torch.device("cuda")
) -> DataLoader[Sample]:
    """
    Constructs a DataLoader for multi-asset tabular data.

    Wraps the dataframe in a MultiAssetDataset, applies tokenization and optional transformation,
    and returns a DataLoader with appropriate batching and collation.

    Parameters:
        df (pd.DataFrame): Input dataframe.
        tokenizer (ColumnTokenizer): Tokenizer for row-level tokenization.
        batch_size (int): Number of samples per batch.
        shuffle (bool): Whether to shuffle the dataset.
        num_workers (int): Number of subprocesses for data loading.
        transform (Optional[Callable]): Optional row-wise transformation.
        device (torch.device): Target device for tensor allocation.

    Returns:
        DataLoader[Sample]: Configured PyTorch DataLoader.
    """
    dataset = MultiAssetDataset(df, tokenizer, device=device, transform=transform)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        collate_fn=collate_fn,
        pin_memory=(device.type == "cuda")
    )
