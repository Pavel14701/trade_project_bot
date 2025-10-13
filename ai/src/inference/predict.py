# src/ai/inference/predict.py

from typing import Protocol, Any, Optional, Dict, runtime_checkable
import pandas as pd
import torch
import numpy as np
import numpy.typing as npt

from preprocess.schema_infer import SchemaInfer
from inference.utils import to_tensor, calibrated_sigmoid


# --- Protocols ---

class ColumnTokenizer(Protocol):
    """
    Interface for tokenizing a single row of tabular data.

    Implementations must convert a pandas Series into a tokenized tensor
    suitable for model input.

    Parameters:
        row (pd.Series): Input row containing raw features.
        device (torch.device): Target device for tensor allocation.

    Returns:
        torch.Tensor: Tokenized representation of the input row.
    """
    def tokenize(self, row: pd.Series[Any], device: torch.device) -> torch.Tensor: ...


class FeatureAdapter(Protocol):
    """
    Interface for transforming raw input features.

    Implementations must apply preprocessing logic to a DataFrame,
    such as normalization, encoding, or feature engineering.

    Parameters:
        df (pd.DataFrame): Raw input dataframe.

    Returns:
        pd.DataFrame: Transformed dataframe ready for schema inference.
    """
    def transform(self, df: pd.DataFrame) -> pd.DataFrame: ...


@runtime_checkable
class AttentionModel(Protocol):
    """
    Optional interface for models that support attention masking.

    Implementations must generate a boolean attention mask for categorical input,
    compatible with PyTorch Transformer modules.

    Parameters:
        x_cat (torch.Tensor): Categorical input tensor of shape [B, C].

    Returns:
        torch.Tensor: Boolean mask of shape [B, 1 + 1 + C], where True indicates padding.
    """
    def generate_attention_mask(self, x_cat: torch.Tensor) -> torch.Tensor: ...


# --- Predictor ---

class Predictor:
    """
    Inference wrapper for tabular models with optional attention and thresholding.

    Applies feature transformation, schema inference, tokenization, and model prediction.
    Supports per-asset thresholding and calibrated sigmoid output.

    Parameters:
        model (torch.nn.Module): Trained model for inference.
        schema (SchemaInfer): Schema transformer for splitting numeric and categorical features.
        feature_adapter (FeatureAdapter): Preprocessing adapter for raw input.
        device (torch.device): Target device for model execution.
        thresholds (Optional[Dict[str, float]]): Per-asset decision thresholds.
        alpha (float): Scaling factor for calibrated sigmoid.
    """
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
        """
        Runs model inference on a batch of tabular data.

        Applies feature adaptation, schema transformation, tokenization, and model forward pass.
        If the model supports attention masking, it is applied automatically.
        Outputs prediction probabilities and binary actions based on thresholds.

        Parameters:
            df (pd.DataFrame): Input dataframe containing raw features and optional asset_id.

        Returns:
            pd.DataFrame: Output dataframe with added columns:
                - "pred": model probability scores
                - "action": binary decisions based on thresholds
        """
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
