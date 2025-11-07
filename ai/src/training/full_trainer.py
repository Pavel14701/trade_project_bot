from typing import Any, cast

import joblib
import pandas as pd
import torch
from model.calibration import fit_platt_scaler, fit_temperature_scaler
from model.column_tokenizer import ColumnTokenizer
from model.heads import SuccessHead
from model.tab_transformer import TabTransformer
from preprocess.adapters.feature_adapter import FeatureAdapter
from preprocess.adapters.labeling_adapter import LabelingAdapter
from preprocess.schema_infer import SchemaInfer
from torch import nn, optim

from ai.src.data_providers.base import BaseProvider
from training.fine_tune import freeze_layers, load_checkpoint, replace_head
from training.utils import compute_metrics, set_seed


class FullTrainer:
    """
    End-to-end training pipeline for tabular models using tokenized input.

    This class handles data loading, preprocessing, schema inference, tokenization,
    model initialization, training, calibration, and artifact saving.

    It uses ColumnTokenizer to convert tabular rows into token sequences,
    and feeds them into TabTransformer with a SuccessHead for binary classification.

    Attributes:
        cfg (dict[str, Any]): Configuration dictionary loaded from YAML.
        device (torch.device): Target device for training and inference.
        df (pd.DataFrame): Raw input dataframe.
        schema (SchemaInfer): Inferred schema for feature transformation.
        tokenizer (ColumnTokenizer): Tokenizer for converting rows to token sequences.
        x_num (Tensor): Numeric token slice for training.
        x_cat (Tensor): Categorical token slice for training.
        y_train (Tensor): Target labels for training.
        x_num_val (Tensor): Numeric token slice for validation.
        x_cat_val (Tensor): Categorical token slice for validation.
        y_val (Tensor): Target labels for validation.
        model (TabTransformer): Transformer-based encoder for tabular data.
        head (SuccessHead): Output head for binary classification.
        optimizer (Optimizer): Optimizer for model parameters.
        loss_fn (Callable): Loss function used during training.
    """
    def __init__(self, cfg: dict[str, Any]) -> None:
        """
        Initializes the FullTrainer with configuration and prepares all components.

        This includes loading data, applying feature adaptation and labeling,
        inferring schema, tokenizing input, splitting into train/val sets,
        initializing model and head, and optionally loading 
          checkpoints or freezing layers.

        Args:
            cfg (dict[str, Any]): Configuration dictionary 
              containing all pipeline parameters.
        """
        self.cfg = cfg
        set_seed(cfg.get("seed", 42))
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # 1. Load data
        self.df = self._load_data()
        # 2. Feature adaptation
        self.df["sl_pct"] = cfg["labeling"]["sl_pct"]
        self.df["tp_pct"] = cfg["labeling"]["tp_pct"]
        self.adapter = FeatureAdapter(
            num_cols=cfg["features"]["numeric"],
            asset_col=cfg["features"]["asset_col"],
            window=cfg["features"]["window"]
        )
        df_scaled = self.adapter.transform(self.df)
        # 3. Labeling
        labeler = LabelingAdapter(
            asset_col=cfg["features"]["asset_col"],
            lag_bars=cfg["labeling"]["lag_bars"],
            horizon_bars=cfg["labeling"]["horizon_bars"]
        )
        df_labeled = labeler.label(df_scaled).dropna(subset=["success"])
        df_labeled["target"] = df_labeled["success"].astype(float)
        # 4. Schema + tokenizer
        self.schema = SchemaInfer().fit(df_labeled)
        joblib.dump(self.schema, cfg["artifacts"]["schema_path"])
        self.tokenizer = ColumnTokenizer(
            num_col_names=self.schema.num_cols,
            cat_col_names=self.schema.cat_cols,
            cat_cardinalities=[len(
                self.schema.cat_vocabs[c]
            ) + 1 for c in self.schema.cat_cols],
            asset_vocab=df_labeled["asset_id"].unique().tolist(),
            d_model=cfg["model"]["d_model"]
        )
        # 5. Tokenize and split
        tokens = self.tokenizer(df_labeled)  # [B, T, D]
        split = int(0.8 * len(tokens))
        self.x_num = tokens[:split, 1 : 1 + len(self.schema.num_cols), :]
        self.x_cat = tokens[:split, 1 + len(self.schema.num_cols) : -1, :]
        self.y_train = torch.tensor(
            df_labeled["target"].values[:split], 
            dtype=torch.float32, 
            device=self.device
        )
        self.x_num_val = tokens[split:, 1 : 1 + len(self.schema.num_cols), :]
        self.x_cat_val = tokens[split:, 1 + len(self.schema.num_cols) : -1, :]
        self.y_val = torch.tensor(
            df_labeled["target"].values[split:], 
            dtype=torch.float32, 
            device=self.device
        )
        # 6. Model
        self.model = TabTransformer(
            num_features=len(self.schema.num_cols),
            cat_cardinalities=[
                len(
                    self.schema.cat_vocabs[c]
                ) + 1 for c in self.schema.cat_cols
            ],
            d_model=cfg["model"]["d_model"],
            nhead=cfg["model"]["nhead"],
            num_layers=cfg["model"]["num_layers"],
            ff_dim=cfg["model"]["ff_dim"],
            dropout=cfg["model"]["dropout"],
            num_classes=1
        ).to(self.device)
        # 7. Head + optimizer
        self.head = SuccessHead(cfg["model"]["d_model"]).to(self.device)
        self.model = cast(TabTransformer, replace_head(self.model, self.head))
        self.optimizer = optim.Adam(self.model.parameters(), lr=cfg["training"]["lr"])
        self.loss_fn = nn.BCELoss()
        # 8. Optional: load checkpoint or freeze layers
        if "checkpoint_init" in cfg:
            self.model = cast(
                TabTransformer, 
                load_checkpoint(self.model, cfg["checkpoint_init"])
            )
        if "fine_tune" in cfg and "freeze" in cfg["fine_tune"]:
            freeze_layers(self.model, cfg["fine_tune"]["freeze"])

    def _load_data(self) -> pd.DataFrame:
        """
        Loads raw data from the configured provider (ClickHouse or QuestDB).

        Fetches data for each symbol over the specified time range and concatenates
        into a single dataframe sorted by timestamp.

        Returns:
            pd.DataFrame: Combined and sorted dataframe with raw features.
        """
        provider: BaseProvider
        if self.cfg["provider"]["type"] == "clickhouse":
            from data_providers.clickhouse_provider import ClickHouseProvider
            provider = ClickHouseProvider(**self.cfg["provider"])
        else:
            from data_providers.questdb_provider import QuestDBProvider
            provider = QuestDBProvider(self.cfg["provider"]["host"])
        dfs = [
            provider.fetch(
                s,
                self.cfg["start"],
                self.cfg["end"]
            ) for s in self.cfg["symbols"]
        ]
        return pd.concat(dfs).sort_values("timestamp").reset_index(drop=True)

    def train(self) -> None:
        """
        Runs the training loop over the tokenized input.

        Performs forward pass, computes loss, backpropagates gradients,
        and updates model parameters. After training, evaluates on validation set
        and prints metrics. Then triggers calibration and saves all artifacts.
        """
        for epoch in range(self.cfg["training"]["epochs"]):
            self.model.train()
            self.optimizer.zero_grad()
            logits = self.model(self.x_num, self.x_cat).squeeze()
            loss = self.loss_fn(torch.sigmoid(logits), self.y_train)
            loss.backward()
            self.optimizer.step()
            print(f"Epoch {epoch + 1}: train loss = {loss.item():.4f}")
        self.model.eval()
        with torch.no_grad():
            logits_val = self.model(self.x_num_val, self.x_cat_val).squeeze()
            preds = torch.sigmoid(logits_val)
            metrics = compute_metrics(preds, self.y_val)
            print("Validation metrics:", metrics)
        self._calibrate_and_save(logits_val)

    def _calibrate_and_save(self, logits: torch.Tensor) -> None:
        """
        Applies temperature scaling and Platt calibration to validation logits.

        Saves the calibrated scalers along with the trained model and schema.

        Args:
            logits (Tensor): Raw logits from the validation set of shape [B].
        """
        temp_scaler = fit_temperature_scaler(
            logits.unsqueeze(1), 
            self.y_val, 
            verbose=True
        )
        probs = torch.sigmoid(temp_scaler(logits.unsqueeze(1)))
        platt = fit_platt_scaler(probs, self.y_val, verbose=True)
        torch.save(self.model.state_dict(), self.cfg["artifacts"]["checkpoint_path"])
        joblib.dump(temp_scaler, self.cfg["artifacts"]["temp_scaler_path"])
        joblib.dump(platt, self.cfg["artifacts"]["platt_path"])
        print("Training complete. Artifacts saved.")