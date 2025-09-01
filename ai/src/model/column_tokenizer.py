import torch
import torch.nn as nn
import pandas as pd
from typing import List, Mapping, Union


class FiLM(nn.Module):
    def __init__(self, d_model: int) -> None:
        super().__init__() #type: ignore
        self.net = nn.Sequential(
            nn.Linear(d_model, 2 * d_model),
            nn.GELU(),
            nn.Linear(2 * d_model, 2 * d_model)
        )

    def forward(self, context: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
        gamma, beta = self.net(context).chunk(2, dim=-1)
        return gamma * x + beta


class ColumnTokenizer(nn.Module):
    def __init__(
        self,
        num_col_names: List[str],
        cat_col_names: List[str],
        cat_cardinalities: List[int],
        asset_vocab: List[str],
        d_model: int
    ) -> None:
        super().__init__() #type: ignore 
        self.d_model = d_model
        self.num_proj = nn.Linear(1, d_model)
        self.num_norm = nn.LayerNorm(d_model)
        self.num_col_emb = nn.Embedding(len(num_col_names), d_model)
        self.film = FiLM(d_model)

        self.cat_embeddings = nn.ModuleList([
            nn.Embedding(card, d_model) for card in cat_cardinalities
        ])
        self.asset_embedding = nn.Embedding(len(asset_vocab), d_model)
        self.cls_token = nn.Parameter(torch.zeros(1, 1, d_model))

        self.num_col_ids = {name: i for i, name in enumerate(num_col_names)}
        self.cat_col_names = cat_col_names
        self.asset_vocab = {name: i for i, name in enumerate(asset_vocab)}

    def tokenize(self, row: Mapping[str, Union[str, float, int]], device: torch.device) -> torch.Tensor:
        num_tokens: List[torch.Tensor] = []
        for col_name in self.num_col_ids:
            val = row.get(col_name, 0.0)
            val_tensor = torch.tensor([[val if pd.notna(val) else 0.0]], dtype=torch.float32, device=device)
            proj = self.num_norm(self.num_proj(val_tensor))
            col_idx = torch.tensor([self.num_col_ids[col_name]], device=device)
            col_emb = self.num_col_emb(col_idx)
            token = self.film(col_emb, proj)
            num_tokens.append(token)
        cat_tokens: List[torch.Tensor] = []
        for i, name in enumerate(self.cat_col_names):
            val = row.get(name, 0)
            val_tensor = torch.tensor([val], dtype=torch.long, device=device)
            cat_tokens.append(self.cat_embeddings[i](val_tensor))
        asset_idx = torch.tensor([self.asset_vocab.get(str(row["asset_id"]), 0)], device=device)
        asset_token = self.asset_embedding(asset_idx)
        cls = self.cls_token.to(device)
        all_tokens = torch.cat([cls] + num_tokens + cat_tokens + [asset_token], dim=1)
        return all_tokens.squeeze(0)

    def tokenize_batch(self, df: pd.DataFrame, device: torch.device) -> torch.Tensor:
        return torch.stack([self.tokenize(row, device) for _, row in df.iterrows()]) #type: ignore
