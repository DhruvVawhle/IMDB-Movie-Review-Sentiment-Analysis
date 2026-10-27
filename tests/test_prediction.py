"""
Unit tests for CineSense prediction service and inference workflows.
"""

import pytest
from services.prediction_service import (
    compare_all_models,
    get_available_models_list,
    is_model_available,
    load_artifacts,
    predict_sentiment,
    validate_review_input,
)


def test_validate_review_input():
    # Valid
    valid, err = validate_review_input("This film was quite magnificent.")
    assert valid is True
    assert err is None

    # Blank / Whitespace
    valid, err = validate_review_input("   ")
    assert valid is False
    assert "empty" in err.lower()

    # None
    valid, err = validate_review_input(None)
    assert valid is False

    # No alphabetic characters
    valid, err = validate_review_input("12345 67890 !@#$%^&*()")
    assert valid is False
    assert "no alphabetic words" in err.lower()

    # Overly long text
    valid, err = validate_review_input("a" * 16000)
    assert valid is False
    assert "exceeds" in err.lower()


def test_models_availability():
    models = get_available_models_list()
    assert len(models) >= 2
    # Logistic Regression and Naive Bayes should be available
    assert is_model_available("logistic_regression") is True
    assert is_model_available("naive_bayes") is True


def test_predict_sentiment_positive():
    text = "An absolutely mesmerizing and flawless masterpiece with superb acting and brilliant pacing."
    res = predict_sentiment(text, model_key="logistic_regression")
    assert res["success"] is True
    assert res["label"] == "POSITIVE"
    assert res["is_positive"] is True
    assert 0.0 <= res["positive_probability"] <= 1.0
    assert res["positive_probability"] > 0.60
    assert res["confidence"] >= 0.50
    assert "calibration_explanation" in res


def test_predict_sentiment_negative():
    text = "A complete waste of time. Horrible acting, terrible script, and utterly boring plot."
    res = predict_sentiment(text, model_key="logistic_regression")
    assert res["success"] is True
    assert res["label"] == "NEGATIVE"
    assert res["is_positive"] is False
    assert res["positive_probability"] < 0.40
    assert res["negative_probability"] > 0.60


def test_naive_bayes_inference():
    text = "Fantastic storyline and great music throughout the movie."
    res = predict_sentiment(text, model_key="naive_bayes")
    assert res["success"] is True
    assert res["label"] == "POSITIVE"
    assert 0.0 <= res["positive_probability"] <= 1.0


def test_compare_all_models():
    text = "One of the best movies of the year, definitely recommended."
    comp = compare_all_models(text)
    assert comp["success"] is True
    assert "results" in comp
    assert "logistic_regression" in comp["results"]
    assert "naive_bayes" in comp["results"]
    lr_res = comp["results"]["logistic_regression"]
    assert lr_res["label"] in ("POSITIVE", "NEGATIVE")

