import torch
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from typing import Callable, Optional
from preprocess.schema_infer import SchemaInfer
from inference.utils import to_tensor, pad_batch

class TabularDataset(Dataset):
    def __init__(self, df: pd.DataFrame, schema: SchemaInfer) -> None:
        self.df = df.reset_index(drop=True)
        self.schema = schema

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> pd.DataFrame:
        return self.df.iloc[[idx]]  # preserve DataFrame shape

def collate_fn(
    batch: list[pd.DataFrame],
    schema: SchemaInfer,
    device: torch.device
) -> dict[str, torch.Tensor]:
    df = pd.concat(batch, axis=0).reset_index(drop=True)
    num, cat = schema.transform(df)
    x_num, x_cat = to_tensor(num, cat, device=device)
    y = torch.tensor(df["target"].values, dtype=torch.float32, device=device)
    return {"x_num": x_num, "x_cat": x_cat, "target": y}


def create_dataloader(
    df: pd.DataFrame,
    schema: SchemaInfer,
    batch_size: int,
    device: torch.device,
    shuffle: bool = True
) -> DataLoader:
    dataset = TabularDataset(df, schema)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        collate_fn=lambda b: collate_fn(b, schema, device)
    )
