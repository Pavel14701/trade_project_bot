from typing import Protocol, Any, Optional, Dict, runtime_checkable
import pandas as pd
import torch
import numpy as np
import numpy.typing as npt

from preprocess.schema_infer import SchemaInfer
from inference.utils import to_tensor, calibrated_sigmoid


# --- Protocols ---

class ColumnTokenizer(Protocol):
    def tokenize(self, row: pd.Series[Any], device: torch.device) -> torch.Tensor: ...


class FeatureAdapter(Protocol):
    def transform(self, df: pd.DataFrame) -> pd.DataFrame: ...


@runtime_checkable
class AttentionModel(Protocol):
    def generate_attention_mask(self, x_cat: torch.Tensor) -> torch.Tensor: ...


# --- Predictor ---

class Predictor:
    def __init__(
        self,
        model: torch.nn.Module,
        schema: SchemaInfer,
        feature_adapter: FeatureAdapter,
        device: torch.device = torch.device("cuda"),
        thresholds: Optional[Dict[str, float]] = None,
        alpha: float = 1.0
    ) -> None:
        self.model = model.to(device)
        self.schema = schema
        self.feature_adapter = feature_adapter
        self.device = device
        self.thresholds = thresholds or {}
        self.alpha = alpha

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        # Feature transformation
        df_feat = self.feature_adapter.transform(df)
        num, cat = self.schema.transform(df_feat)
        x_num, x_cat = to_tensor(num, cat, device=self.device)

        # Attention mask if supported
        attention_mask: Optional[torch.Tensor] = None
        if isinstance(self.model, AttentionModel):
            attention_mask = self.model.generate_attention_mask(x_cat)

        # Inference
        self.model.eval()
        with torch.no_grad():
            logits = (
                self.model(x_num, x_cat, attention_mask)
                if attention_mask is not None
                else self.model(x_num, x_cat)
            )
            probs_tensor: torch.Tensor = calibrated_sigmoid(logits.squeeze(), alpha=self.alpha)
            probs: npt.NDArray[np.float32] = probs_tensor.cpu().numpy() # type: ignore[reportUnknownVariableType]

        # Output construction
        out = df.copy()
        out["pred"] = probs

        if "asset_id" in df.columns:
            asset_ids: pd.Series[str] = df["asset_id"].astype(str)
            thresholds_tensor = torch.tensor([
                self.thresholds.get(asset, 0.5) for asset in asset_ids
            ], device=probs_tensor.device)
            actions = (probs_tensor > thresholds_tensor).int().cpu().numpy() # type: ignore[reportUnknownVariableType]
            out["action"] = actions
        else:
            out["action"] = (probs > 0.5).astype(int)

        return out
