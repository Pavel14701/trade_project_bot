import pandas as pd
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any


@dataclass(frozen=True)
class Schema:
    """
    Immutable schema definition for tabular data.

    Attributes:
        num_cols (List[str]): List of numeric column names.
        cat_cols (List[str]): List of categorical column names.
        cat_vocabs (Dict[str, Dict[str, int]]): Mapping from category values to integer indices per column.
        cat_unk_idx (Dict[str, int]): Reserved index for unknown categorical values per column.
    """
    num_cols: List[str]
    cat_cols: List[str]
    cat_vocabs: Dict[str, Dict[str, int]]
    cat_unk_idx: Dict[str, int]


class SchemaInfer:
    """
    Infers and manages schema for tabular data preprocessing.

    Separates numeric and categorical columns, builds vocabularies for categorical features,
    and provides transformation utilities for model-ready encoding.

    Parameters:
        max_card (int): Maximum number of unique values to keep per categorical column.
        min_freq (int): Minimum frequency required for a categorical value to be included.
        unk_index (int): Reserved index for unknown categorical values.
    """
    def __init__(self, max_card: int = 1000, min_freq: int = 1, unk_index: int = 2**30) -> None:
        self.max_card = max_card
        self.min_freq = min_freq
        self.unk_index = unk_index
        self._schema: Optional[Schema] = None

    def fit(self, df: pd.DataFrame, exclude: Optional[List[str]] = None) -> "SchemaInfer":
        """
        Infers schema from the input dataframe.

        Parameters:
            df (pd.DataFrame): Input dataframe.
            exclude (Optional[List[str]]): Columns to exclude from schema inference.

        Returns:
            SchemaInfer: Self with fitted schema.
        """
        exclude = exclude or []
        # Initial type inference using pandas selectors
        num_cols = [col for col in df.select_dtypes(include=["number"]).columns if col not in exclude]
        cat_cols = [col for col in df.select_dtypes(exclude=["number"]).columns if col not in exclude]
        # Explicitly check object columns for numeric strings
        for col in df.select_dtypes(include=["object"]).columns:
            if col in exclude:
                continue
            non_null = df[col].dropna() # type: ignore
            if len(non_null) > 0 and non_null.apply(lambda x: isinstance(x, str) and x.replace('.', '', 1).isdigit()).all(): # type: ignore
                num_cols.append(col)
                if col in cat_cols:
                    cat_cols.remove(col)
        cat_vocabs: Dict[str, Dict[str, int]] = {}
        cat_unk_idx: Dict[str, int] = {}
        for col in cat_cols:
            vc = df[col].astype("object").value_counts()
            vc = vc[vc >= self.min_freq]
            top = list(vc.index[:self.max_card]) # type: ignore
            vocab = {v: i for i, v in enumerate(top)}
            cat_vocabs[col] = vocab
            cat_unk_idx[col] = self.unk_index  # Reserved index for unknowns
        self._schema = Schema(
            num_cols=num_cols,
            cat_cols=cat_cols,
            cat_vocabs=cat_vocabs,
            cat_unk_idx=cat_unk_idx
        )
        return self

    def transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Transforms input dataframe into numeric and categorical tensors.

        Parameters:
            df (pd.DataFrame): Input dataframe.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: (numeric_df, categorical_df)
        """
        if self._schema is None:
            raise RuntimeError("SchemaInfer must be fit before transform.")
        missing = [col for col in self._schema.cat_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Missing categorical columns: {missing}")
        num = df[self._schema.num_cols].copy()
        cat = pd.DataFrame(index=df.index) # type: ignore
        for col in self._schema.cat_cols:
            vocab = self._schema.cat_vocabs[col]
            unk = self._schema.cat_unk_idx[col]
            cat[col] = df[col].map(vocab).fillna(unk).astype("Int64") # type: ignore
        return num, cat

    def inverse_transform(self, cat_df: pd.DataFrame) -> pd.DataFrame:
        """
        Converts encoded categorical indices back to original string values.

        Parameters:
            cat_df (pd.DataFrame): Dataframe with encoded categorical indices.

        Returns:
            pd.DataFrame: Dataframe with decoded categorical values.
        """
        if self._schema is None:
            raise RuntimeError("SchemaInfer must be fit before inverse_transform.")
        inv = pd.DataFrame(index=cat_df.index) # type: ignore
        for col in self._schema.cat_cols:
            vocab = self._schema.cat_vocabs[col]
            reverse_vocab = {i: v for v, i in vocab.items()}
            inv[col] = cat_df[col].map(reverse_vocab).fillna(f"[UNK_{col}]") # type: ignore
        return inv

    def fit_transform(self, df: pd.DataFrame, exclude: Optional[List[str]] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Fits schema and transforms the input dataframe in one step.

        Parameters:
            df (pd.DataFrame): Input dataframe.
            exclude (Optional[List[str]]): Columns to exclude from schema inference.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: (numeric_df, categorical_df)
        """
        return self.fit(df, exclude).transform(df)

    def get_schema(self) -> Schema:
        """
        Returns the fitted schema.

        Returns:
            Schema: Inferred schema object.
        """
        if self._schema is None:
            raise RuntimeError("SchemaInfer has not been fit yet.")
        return self._schema

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the schema to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary containing schema fields.
        """
        if self._schema is None:
            raise RuntimeError("SchemaInfer has not been fit yet.")
        return asdict(self._schema)

    def __repr__(self) -> str:
        """
        Returns a string representation of the schema state.

        Returns:
            str: "SchemaInfer(fit=False)" if not fitted,
                 otherwise "SchemaInfer(fit=True, num=..., cat=...)".
        """
        if self._schema is None:
            return "SchemaInfer(fit=False)"
        return f"SchemaInfer(fit=True, num={len(self._schema.num_cols)}, cat={len(self._schema.cat_cols)})"
