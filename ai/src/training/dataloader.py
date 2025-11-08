import pandas as pd
import torch
from inference.utils import to_tensor
from preprocess.schema_infer import SchemaInfer
from torch.utils.data import DataLoader, Dataset


class TabularDataset(Dataset):
    """
    Dataset wrapper for row-wise tabular inference.

    Stores a dataframe and returns individual rows as single-row DataFrames
    to preserve schema and column types during batching.

    Parameters:
        df (pd.DataFrame): Input dataframe containing features and targets.
        schema (SchemaInfer): Fitted schema used for feature transformation.
    """
    def __init__(self, df: pd.DataFrame, schema: SchemaInfer) -> None:
        self.df = df.reset_index(drop=True)
        self.schema = schema

    def __len__(self) -> int:
        """
        Returns the number of samples in the dataset.

        Returns:
            int: Total number of rows in the dataframe.
        """
        return len(self.df)

    def __getitem__(self, idx: int) -> pd.DataFrame:
        """
        Retrieves a single row as a one-row DataFrame.

        Preserves column types and structure for downstream batching.

        Parameters:
            idx (int): Row index.

        Returns:
            pd.DataFrame: Single-row dataframe.
        """
        return self.df.iloc[[idx]]  # preserve DataFrame shape


def collate_fn(
    batch: list[pd.DataFrame],
    schema: SchemaInfer,
    device: torch.device
) -> dict[str, torch.Tensor]:
    """
    Collates a batch of single-row DataFrames into model-ready tensors.

    Applies schema transformation and converts numeric and categorical features
    to device-aware tensors. Extracts target column as float tensor.

    Parameters:
        batch (list[pd.DataFrame]): List of single-row DataFrames.
        schema (SchemaInfer): Fitted schema for feature transformation.
        device (torch.device): Target device for tensor allocation.

    Returns:
        dict[str, torch.Tensor]: Dictionary with keys:
            - "x_num": numeric tensor [B, F]
            - "x_cat": categorical tensor [B, C]
            - "target": target tensor [B]
    """
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
    """
    Creates a PyTorch DataLoader for tabular inference.

    Wraps the dataframe in a TabularDataset and applies a schema-aware
    collate function to produce model-ready batches.

    Parameters:
        df (pd.DataFrame): Input dataframe.
        schema (SchemaInfer): Fitted schema for feature transformation.
        batch_size (int): Number of samples per batch.
        device (torch.device): Target device for tensor allocation.
        shuffle (bool): Whether to shuffle the dataset.

    Returns:
        DataLoader: Configured PyTorch DataLoader.
    """
    dataset = TabularDataset(df, schema)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        collate_fn=lambda b: collate_fn(b, schema, device)
    )
