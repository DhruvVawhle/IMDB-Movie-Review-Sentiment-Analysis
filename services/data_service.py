"""
Dataset loading, validation, and exploration service for CineSense.
Handles cached reads, summary metrics, filtering, and schema validation.
"""

import os
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np

DATASET_CANDIDATE_PATHS = [
    os.path.join("data", "IMDB Dataset.csv"),
    os.path.join("dataset", "IMDB Dataset.csv"),
    os.path.join("dataset", "IMBD Dataset.csv"),
    "IMDB Dataset.csv",
]

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

_CACHED_DF: Optional[pd.DataFrame] = None
_CACHED_STATS: Optional[Dict[str, Any]] = None


def resolve_dataset_path() -> Optional[str]:
    """Search for the IMDB Dataset across known standard locations."""
    for path in DATASET_CANDIDATE_PATHS:
        if os.path.exists(path):
            return os.path.abspath(path)
    return None


def validate_dataset_schema(df: pd.DataFrame) -> Tuple[bool, str]:
    """Ensure required columns and minimum size are present."""
    required_cols = {"review", "sentiment"}
    if not required_cols.issubset(set(df.columns)):
        missing = required_cols - set(df.columns)
        return False, f"Missing required column(s): {', '.join(missing)}"
    if len(df) == 0:
        return False, "Dataset is empty."
    return True, "Schema valid."


def _parse_and_prepare_df(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize sentiment and compute word/character counts cleanly and rapidly."""
    import re
    df["sentiment_clean"] = df["sentiment"].astype(str).str.strip().str.lower()
    df["label"] = df["sentiment_clean"].map({"positive": 1, "negative": 0})

    html_regex = re.compile(r"<[^>]+>")
    reviews = df["review"].astype(str).tolist()
    if "word_count" not in df.columns:
        df["word_count"] = [len(html_regex.sub(" ", r).split()) for r in reviews]
    if "char_count" not in df.columns:
        df["char_count"] = [len(html_regex.sub(" ", r)) for r in reviews]
    return df


def load_imdb_dataset(limit: Optional[int] = None) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Load the IMDB dataset into a pandas DataFrame.
    Caches the dataset in memory so subsequent views and tab switches are instantaneous.
    """
    global _CACHED_DF
    if _CACHED_DF is not None:
        if limit is None:
            return _CACHED_DF.copy(), None
        return _CACHED_DF.head(limit).copy(), None

    dataset_path = resolve_dataset_path()
    if not dataset_path:
        return None, (
            "IMDB Dataset file not found. Expected 'data/IMDB Dataset.csv' or 'dataset/IMDB Dataset.csv'. "
            "Please ensure the Kaggle 50K IMDB dataset is placed in the project 'data/' folder."
        )

    try:
        # If requesting a small subset before full dataset is loaded, load only required rows
        if limit is not None and limit < 5000:
            df_sub = pd.read_csv(dataset_path, nrows=limit)
            valid, msg = validate_dataset_schema(df_sub)
            if not valid:
                return None, msg
            df_sub = _parse_and_prepare_df(df_sub)
            return df_sub, None

        df = pd.read_csv(dataset_path)
        valid, msg = validate_dataset_schema(df)
        if not valid:
            return None, msg

        df = _parse_and_prepare_df(df)
        _CACHED_DF = df

        if limit is None:
            return _CACHED_DF.copy(), None
        return _CACHED_DF.head(limit).copy(), None

    except Exception as exc:
        return None, f"Failed to load dataset: {str(exc)}"


def get_dataset_statistics() -> Dict[str, Any]:
    """Return verified aggregate statistics over the full dataset."""
    global _CACHED_STATS
    if _CACHED_STATS is not None:
        return _CACHED_STATS

    df, err = load_imdb_dataset()
    if df is None:
        return {
            "available": False,
            "error": err,
            "total_samples": 0,
            "positive_count": 0,
            "negative_count": 0,
            "avg_word_count": 0,
            "median_word_count": 0,
            "min_word_count": 0,
            "max_word_count": 0,
        }

    total = len(df)
    counts = df["sentiment_clean"].value_counts().to_dict()
    pos_count = counts.get("positive", 0)
    neg_count = counts.get("negative", 0)

    word_stats = df["word_count"].describe().to_dict()
    pos_stats = df[df["sentiment_clean"] == "positive"]["word_count"].describe().to_dict()
    neg_stats = df[df["sentiment_clean"] == "negative"]["word_count"].describe().to_dict()

    _CACHED_STATS = {
        "available": True,
        "error": None,
        "total_samples": int(total),
        "positive_count": int(pos_count),
        "negative_count": int(neg_count),
        "pos_percentage": round((pos_count / total) * 100, 2) if total else 0,
        "neg_percentage": round((neg_count / total) * 100, 2) if total else 0,
        "avg_word_count": round(word_stats.get("mean", 0), 1),
        "median_word_count": int(word_stats.get("50%", 0)),
        "min_word_count": int(word_stats.get("min", 0)),
        "max_word_count": int(word_stats.get("max", 0)),
        "std_word_count": round(word_stats.get("std", 0), 1),
        "pos_word_mean": round(pos_stats.get("mean", 0), 1),
        "neg_word_mean": round(neg_stats.get("mean", 0), 1),
        "pos_word_median": int(pos_stats.get("50%", 0)),
        "neg_word_median": int(neg_stats.get("50%", 0)),
    }
    return _CACHED_STATS


def filter_dataset(
    df: pd.DataFrame,
    sentiment_filter: str = "all",
    search_query: str = "",
    min_words: int = 0,
    max_words: Optional[int] = None,
) -> pd.DataFrame:
    """Filter dataset by sentiment label, text substring, and length criteria."""
    filtered = df
    if sentiment_filter in ("positive", "negative"):
        filtered = filtered[filtered["sentiment_clean"] == sentiment_filter]

    if search_query and search_query.strip():
        q = search_query.strip().lower()
        filtered = filtered[filtered["review"].str.lower().str.contains(q, na=False, regex=False)]

    if min_words > 0:
        filtered = filtered[filtered["word_count"] >= min_words]
    if max_words is not None:
        filtered = filtered[filtered["word_count"] <= max_words]

    return filtered

