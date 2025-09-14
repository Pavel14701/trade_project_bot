# src/ai/model/column_tokenizer.py

import torch
import torch.nn as nn
import pandas as pd
from typing import List, Mapping, Union


class FiLM(nn.Module):
    """
    Feature-wise Linear Modulation (FiLM) layer.

    Applies learned affine transformations to input features conditioned on context.
    Used to inject column-specific embeddings into projected numeric values.

    Parameters:
        d_model (int): Dimensionality of the token space.
    """
    def __init__(self, d_model: int) -> None:
        super().__init__() # type: ignore
        self.net = nn.Sequential(
            nn.Linear(d_model, 2 * d_model),
            nn.GELU(),
            nn.Linear(2 * d_model, 2 * d_model)
        )

    def forward(
        self, 
        context: torch.Tensor, 
        x: torch.Tensor
    ) -> torch.Tensor:
        """
        Applies FiLM modulation to input tensor.

        Splits the output of the conditioning network into gamma and beta,
        then applies element-wise affine transformation.

        Parameters:
            context (torch.Tensor): Conditioning tensor of shape [B, 1, D].
            x (torch.Tensor): Input tensor to modulate of shape [B, 1, D].

        Returns:
            torch.Tensor: Modulated tensor of shape [B, 1, D].
        """
        gamma, beta = self.net(context).chunk(2, dim=-1)
        return gamma * x + beta


class ColumnTokenizer(nn.Module):
    """
    Tokenizer for tabular data rows.

    Converts a single row of mixed numeric and categorical features into a unified
    token sequence suitable for Transformer-based models. Includes support for
    column-wise embeddings, FiLM modulation, and asset-specific embeddings.

    Parameters:
        num_col_names (List[str]): Names of numeric columns.
        cat_col_names (List[str]): Names of categorical columns.
        cat_cardinalities (List[int]): Cardinalities for each categorical column.
        asset_vocab (List[str]): Known asset identifiers.
        d_model (int): Dimensionality of token embeddings.
    """
    def __init__(
        self,
        num_col_names: List[str],
        cat_col_names: List[str],
        cat_cardinalities: List[int],
        asset_vocab: List[str],
        d_model: int
    ) -> None:
        super().__init__() # type: ignore
        self.d_model = d_model
        self.num_proj = nn.Linear(1, d_model)
        self.num_norm = nn.LayerNorm(d_model)
        self.num_col_emb = nn.Embedding(len(num_col_names), d_model)
        self.film = FiLM(d_model)

        self.cat_embeddings = nn.ModuleList([
            nn.Embedding(card, d_model) for card in cat_cardinalities
        ])

        # Добавляем UNK_ASSET в словарь
        self.asset_vocab = {name: i for i, name in enumerate(asset_vocab)}
        self.unk_asset_idx = len(self.asset_vocab)
        self.asset_vocab["UNK_ASSET"] = self.unk_asset_idx

        self.asset_embedding = nn.Embedding(len(self.asset_vocab), d_model)
        self.cls_token = nn.Parameter(torch.zeros(1, 1, d_model))

        self.num_col_ids = {name: i for i, name in enumerate(num_col_names)}
        self.cat_col_names = cat_col_names

    def tokenize(
        self, 
        row: Mapping[str, Union[str, float, int]], 
        device: torch.device
    ) -> torch.Tensor:
        """
        Tokenizes a single row into a sequence of embeddings.

        Applies FiLM-modulated projections to numeric features, categorical embeddings,
        and asset-specific embedding. Prepends a learnable CLS token.

        Returns:
            torch.Tensor: Token sequence of shape [T, D], where T = 1 + 1 + C + 1.
        """
        num_tokens: List[torch.Tensor] = []
        for col_name in self.num_col_ids:
            val = row.get(col_name, 0.0)
            val_tensor = torch.tensor([[val if pd.notna(val) else 0.0]], dtype=torch.float32, device=device)
            proj = self.num_norm(self.num_proj(val_tensor))
            col_idx = torch.tensor([self.num_col_ids[col_name]], device=device)
            col_emb = self.num_col_emb(col_idx)
            token = self.film(col_emb, proj)
            num_tokens.append(token.view(-1, self.d_model))  # [1, D]
        cat_tokens: List[torch.Tensor] = []
        for i, name in enumerate(self.cat_col_names):
            val = row.get(name, 0)
            val_tensor = torch.tensor([val], dtype=torch.long, device=device)
            cat_tokens.append(self.cat_embeddings[i](val_tensor).view(-1, self.d_model))  # [1, D]
        asset_id_str = str(row.get("asset_id", "UNK_ASSET"))
        asset_idx = torch.tensor(
            [self.asset_vocab.get(asset_id_str, self.unk_asset_idx)],
            device=device
        )
        asset_token = self.asset_embedding(asset_idx).view(-1, self.d_model)  # [1, D]
        cls = self.cls_token.to(device).view(-1, self.d_model)  # [1, D]
        return torch.cat([cls] + num_tokens + cat_tokens + [asset_token], dim=0)  # [T, D]

    def tokenize_batch(
        self, 
        df: pd.DataFrame, 
        device: torch.device
    ) -> torch.Tensor:
        """
        Tokenizes a batch of rows into stacked token sequences.

        Each row is tokenized into [T, D], and stacked into [B, T, D].

        Parameters:
            df (pd.DataFrame): Input dataframe with feature columns.
            device (torch.device): Target device for tensor allocation.

        Returns:
            torch.Tensor: Batched token tensor of shape [B, T, D].
        """
        tokenized = [self.tokenize(row, device) for _, row in df.iterrows()]  # List of [T, D] # type: ignore
        return torch.stack(tokenized, dim=0)  # [B, T, D]
