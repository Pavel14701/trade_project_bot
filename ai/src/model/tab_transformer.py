import torch
import torch.nn as nn
from typing import Optional

class TokenDropout(nn.Module):
    def __init__(self, p: float = 0.1):
        super().__init__() # type: ignore
        self.p = p

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if not self.training or self.p == 0.0:
            return x
        mask = torch.rand_like(x[:, :, 0]) < self.p
        x[mask] = 0.0
        return x

class TabTransformer(nn.Module):
    def __init__(
        self,
        num_features: int,
        cat_cardinalities: list[int],
        d_model: int = 128,
        nhead: int = 4,
        num_layers: int = 4,
        ff_dim: int = 256,
        dropout: float = 0.1,
        num_classes: int = 1,
        padding_idx: int = 0,
        token_dropout: float = 0.1
    ) -> None:
        super().__init__() # type: ignore
        self.d_model = d_model
        self.padding_idx = padding_idx

        # Embedding for categorical features
        self.cat_embeddings = nn.ModuleList([
            nn.Embedding(card + 1, d_model, padding_idx=padding_idx)
            for card in cat_cardinalities
        ])

        # Projection for numerical features
        self.num_proj = nn.Linear(num_features, d_model)

        # Learnable [CLS] token
        self.cls_token = nn.Parameter(torch.randn(1, 1, d_model))

        # Normalization
        self.input_norm = nn.LayerNorm(d_model)
        self.output_norm = nn.LayerNorm(d_model)

        # Token dropout
        self.token_dropout = TokenDropout(p=token_dropout)

        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=ff_dim,
            dropout=dropout,
            batch_first=True,
            norm_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        # Output head
        self.head = nn.Sequential(
            nn.Linear(d_model, ff_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(ff_dim, num_classes)
        )

    def generate_attention_mask(self, x_cat: torch.Tensor) -> torch.Tensor:
        pad_mask = (x_cat == self.padding_idx)  # [B, C]
        cls_mask = torch.zeros(x_cat.size(0), 1, dtype=torch.bool, device=x_cat.device)
        num_mask = torch.zeros(x_cat.size(0), 1, dtype=torch.bool, device=x_cat.device)
        full_mask = torch.cat([cls_mask, num_mask, pad_mask], dim=1)
        return ~full_mask  # Transformer expects True for keep

    def forward(
        self,
        x_num: torch.Tensor,
        x_cat: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        # Embed categorical features
        cat_embeds = [emb(x_cat[:, i]) for i, emb in enumerate(self.cat_embeddings)]
        cat_stack = torch.stack(cat_embeds, dim=1)  # [B, C, D]

        # Project numerical features
        num_proj = self.num_proj(x_num).unsqueeze(1)  # [B, 1, D]

        # Combine with CLS token
        cls = self.cls_token.expand(x_num.size(0), -1, -1)  # [B, 1, D]
        tokens = torch.cat([cls, num_proj, cat_stack], dim=1)  # [B, 1+1+C, D]

        # Normalize + dropout
        tokens = self.input_norm(tokens)
        tokens = self.token_dropout(tokens)

        # Encode
        encoded = self.encoder(tokens, src_key_padding_mask=attention_mask)

        # Use CLS token
        cls_out = self.output_norm(encoded[:, 0])
        return self.head(cls_out)
