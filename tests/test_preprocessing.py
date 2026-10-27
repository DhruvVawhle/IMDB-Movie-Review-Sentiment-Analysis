"""
Unit tests for CineSense text preprocessing pipeline.
"""

import pytest
from services.preprocessing import (
    clean_html_and_urls,
    filter_tokens,
    get_pipeline_breakdown,
    normalize_text,
    preprocess_text,
    tokenize_text,
)


def test_clean_html_and_urls():
    raw = "<p>This is a <b>great</b> film! Visit http://example.com for more info.</p>"
    cleaned = clean_html_and_urls(raw)
    assert "<p>" not in cleaned
    assert "<b>" not in cleaned
    assert "http://example.com" not in cleaned
    assert "great" in cleaned
    assert "film" in cleaned


def test_normalize_text():
    raw = "Sensational Acting & 10/10 Direction!!"
    normalized = normalize_text(raw)
    assert normalized == "sensational acting direction"
    assert "10" not in normalized
    assert "!" not in normalized


def test_tokenize_and_filter():
    raw = "the movie was very good and interesting"
    tokens = tokenize_text(raw)
    filtered = filter_tokens(tokens)
    assert "the" not in filtered
    assert "was" not in filtered
    assert "movie" in filtered
    assert "good" in filtered


def test_preprocess_text_pipeline():
    sample = "<b>Outstanding cinematography!</b> I really loved every single moment. https://imdb.com"
    processed = preprocess_text(sample, use_lemma=True)
    assert "outstanding" in processed or "cinematography" in processed
    assert "http" not in processed
    assert "<b>" not in processed


def test_preprocess_empty_and_invalid():
    assert preprocess_text("") == ""
    assert preprocess_text("    ") == ""
    assert preprocess_text(None) == ""
    assert preprocess_text("!!! ??? 12345") == ""


def test_pipeline_breakdown():
    text = "Great movie http://test.com"
    breakdown = get_pipeline_breakdown(text)
    assert breakdown["original"] == text
    assert "http" not in breakdown["html_and_url_cleaned"]
    assert "lemmatized_text" in breakdown
    assert "stemmed_text" in breakdown

