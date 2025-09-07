import pandas as pd
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any


@dataclass(frozen=True)
class Schema:
    num_cols: List[str]
    cat_cols: List[str]
    cat_vocabs: Dict[str, Dict[str, int]]
    cat_unk_idx: Dict[str, int]


class SchemaInfer:
    def __init__(self, max_card: int = 1000, min_freq: int = 1) -> None:
        self.max_card = max_card
        self.min_freq = min_freq
        self._schema: Optional[Schema] = None

    def fit(self, df: pd.DataFrame, exclude: Optional[List[str]] = None) -> "SchemaInfer":
        exclude = exclude or []
        num_cols: List[str] = []
        cat_cols: List[str] = []

        for col in df.columns:
            if col in exclude:
                continue
            if pd.api.types.is_numeric_dtype(df[col].dtype):  # type: ignore[reportUnknownMemberType]
                num_cols.append(col)
            else:
                cat_cols.append(col)

        cat_vocabs: Dict[str, Dict[str, int]] = {}
        cat_unk_idx: Dict[str, int] = {}

        for col in cat_cols:
            vc = df[col].astype("object").value_counts()
            vc = vc[vc >= self.min_freq]
            top = list(vc.index[:self.max_card])  # type: ignore[reportUnknownVariableType]
            vocab = {v: i for i, v in enumerate(top)}  # type: ignore[reportUnknownVariableType]
            cat_vocabs[col] = vocab
            cat_unk_idx[col] = len(vocab)

        self._schema = Schema(
            num_cols=num_cols,
            cat_cols=cat_cols,
            cat_vocabs=cat_vocabs,
            cat_unk_idx=cat_unk_idx
        )
        return self

    def transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        if self._schema is None:
            raise RuntimeError("SchemaInfer must be fit before transform.")

        if missing := [col for col in self._schema.cat_cols if col not in df.columns]:
            raise ValueError(f"Missing categorical columns: {missing}")

        num = df[self._schema.num_cols].copy()
        cat = pd.DataFrame(index=df.index)  # type: ignore[reportUnknownVariableType]

        for col in self._schema.cat_cols:
            vocab = self._schema.cat_vocabs[col]
            unk = self._schema.cat_unk_idx[col]
            cat[col] = df[col].map(vocab).fillna(unk).astype("Int64")  # type: ignore[reportUnknownVariableType]

        return num, cat

    def inverse_transform(self, cat_df: pd.DataFrame) -> pd.DataFrame:
        if self._schema is None:
            raise RuntimeError("SchemaInfer must be fit before inverse_transform.")

        inv = pd.DataFrame(index=cat_df.index) # type: ignore[reportUnknownVariableType]
        for col in self._schema.cat_cols:
            vocab = self._schema.cat_vocabs[col]
            unk = self._schema.cat_unk_idx[col] # type: ignore[reportUnknownVariableType]
            reverse_vocab = {i: v for v, i in vocab.items()}
            inv[col] = cat_df[col].map(reverse_vocab).fillna(f"[UNK_{col}]") # type: ignore[reportUnknownVariableType]
        return inv

    def fit_transform(self, df: pd.DataFrame, exclude: Optional[List[str]] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        return self.fit(df, exclude).transform(df)

    def get_schema(self) -> Schema:
        if self._schema is None:
            raise RuntimeError("SchemaInfer has not been fit yet.")
        return self._schema

    def to_dict(self) -> Dict[str, Any]:
        if self._schema is None:
            raise RuntimeError("SchemaInfer has not been fit yet.")
        return asdict(self._schema)

    def __repr__(self) -> str:
        if self._schema is None:
            return "SchemaInfer(fit=False)"
        return f"SchemaInfer(fit=True, num={len(self._schema.num_cols)}, cat={len(self._schema.cat_cols)})"
