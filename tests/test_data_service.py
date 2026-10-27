"""
Unit tests for CineSense dataset loading and exploration service.
"""

import os
import pandas as pd
import pytest
from services.data_service import (
    filter_dataset,
    get_dataset_statistics,
    load_imdb_dataset,
    resolve_dataset_path,
    validate_dataset_schema,
)


def test_resolve_dataset_path():
    path = resolve_dataset_path()
    assert path is not None
    assert os.path.exists(path)


def test_validate_dataset_schema():
    valid_df = pd.DataFrame({"review": ["Good film"], "sentiment": ["positive"]})
    valid, msg = validate_dataset_schema(valid_df)
    assert valid is True

    invalid_df = pd.DataFrame({"text": ["Good film"], "score": [5]})
    valid, msg = validate_dataset_schema(invalid_df)
    assert valid is False
    assert "Missing required column" in msg


def test_load_imdb_dataset_subset():
    df, err = load_imdb_dataset(limit=20)
    assert err is None
    assert df is not None
    assert len(df) == 20
    assert "review" in df.columns
    assert "sentiment" in df.columns
    assert "sentiment_clean" in df.columns
    assert "word_count" in df.columns


def test_get_dataset_statistics():
    stats = get_dataset_statistics()
    assert stats["available"] is True
    assert stats["total_samples"] == 50000
    assert stats["positive_count"] == 25000
    assert stats["negative_count"] == 25000
    assert stats["avg_word_count"] > 100
    assert stats["median_word_count"] > 100


def test_filter_dataset():
    sample_df = pd.DataFrame({
        "review": [
            "A magnificent masterpiece by Christopher Nolan",
            "Terrible awful disaster of a film",
            "Decent average movie with okay pacing",
        ],
        "sentiment_clean": ["positive", "negative", "positive"],
        "word_count": [6, 5, 6],
    })

    # Filter positive
    pos_filtered = filter_dataset(sample_df, sentiment_filter="positive")
    assert len(pos_filtered) == 2

    # Search keyword
    nolan_filtered = filter_dataset(sample_df, search_query="Nolan")
    assert len(nolan_filtered) == 1
    assert "Christopher Nolan" in nolan_filtered.iloc[0]["review"]

    # Filter word count
    len_filtered = filter_dataset(sample_df, min_words=6)
    assert len(len_filtered) == 2

