"""
Unit tests for deployment readiness:
1. HTML tag stripping
2. Predict wrapper returning valid probabilities that sum to 1
3. Empty-review error state handling
"""

import numpy as np
import pytest
from services.explainability_service import predict_proba_wrapper
from services.prediction_service import predict_sentiment, validate_review_input
from services.preprocessing import clean_html_and_urls


def test_html_tag_stripping():
    """Verify that HTML tags, line breaks, entities, and URLs are cleanly removed."""
    raw_html = (
        "<p>This film is <b>extraordinary</b>! <br /><br />"
        "Read full review at https://imdb.com/title/12345 &amp; enjoy.</p>"
    )
    cleaned = clean_html_and_urls(raw_html)

    assert "<p>" not in cleaned
    assert "</p>" not in cleaned
    assert "<b>" not in cleaned
    assert "</b>" not in cleaned
    assert "<br />" not in cleaned
    assert "<br>" not in cleaned
    assert "https://imdb.com/title/12345" not in cleaned
    assert "&amp;" not in cleaned
    assert "extraordinary" in cleaned
    assert "enjoy" in cleaned


@pytest.mark.parametrize("model_key", ["logistic_regression", "naive_bayes", "bilstm"])
def test_predict_wrapper_returns_valid_probabilities_sum_to_one(model_key):
    """Verify that predict_proba_wrapper returns probabilities in [0, 1] summing to 1.0."""
    sample_texts = [
        "A magnificent, breathtaking cinematic triumph with sublime performances.",
        "A disastrously boring, tedious, and uninspired waste of time.",
        "Standard popcorn movie, neither amazing nor terrible.",
    ]

    probs = predict_proba_wrapper(sample_texts, model_key=model_key)

    assert isinstance(probs, np.ndarray)
    assert probs.shape == (len(sample_texts), 2)

    # Check bounds
    assert np.all(probs >= 0.0)
    assert np.all(probs <= 1.0)

    # Check that probabilities sum to 1.0 for each review
    row_sums = np.sum(probs, axis=1)
    np.testing.assert_allclose(row_sums, np.ones(len(sample_texts)), atol=1e-5)


def test_empty_review_error_state():
    """Verify that empty or whitespace-only review inputs gracefully return an error state."""
    # Test validator directly
    valid_empty, err_empty = validate_review_input("")
    assert valid_empty is False
    assert err_empty is not None
    assert "empty" in err_empty.lower() or "enter a review" in err_empty.lower()

    valid_spaces, err_spaces = validate_review_input("     \n\t   ")
    assert valid_spaces is False
    assert err_spaces is not None

    # Test predict_sentiment wrapper
    res_empty = predict_sentiment("", model_key="logistic_regression")
    assert res_empty["success"] is False
    assert "error" in res_empty
    assert len(res_empty["error"]) > 0

    res_spaces = predict_sentiment("   ", model_key="logistic_regression")
    assert res_spaces["success"] is False
    assert "error" in res_spaces

