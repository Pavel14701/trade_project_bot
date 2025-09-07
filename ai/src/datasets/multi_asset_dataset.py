from typing import TypedDict, Callable, Optional, Any
import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from model.column_tokenizer import ColumnTokenizer

class Sample(TypedDict):
    tokens: torch.Tensor
    asset_id: str
    label: int

class MultiAssetDataset(Dataset[Sample]):
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
        return len(self.df)

    def __getitem__(self, idx: int) -> Sample:
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
    dataset = MultiAssetDataset(df, tokenizer, device=device, transform=transform)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        collate_fn=collate_fn,
        pin_memory=(device.type == "cuda")
    )
