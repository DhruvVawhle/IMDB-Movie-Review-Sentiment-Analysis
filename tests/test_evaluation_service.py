"""
Unit tests for CineSense evaluation service and metrics integrity.
"""

import pytest
from services.evaluation_service import (
    get_available_models_meta,
    get_comparison_dataframe,
    get_model_confusion_matrix,
    get_model_roc_curve,
    load_evaluation_summary,
    load_top_predictive_features,
)


def test_load_evaluation_summary():
    summary, err = load_evaluation_summary()
    assert err is None
    assert summary is not None
    assert summary["test_sample_size"] == 10000
    assert "models" in summary
    assert "logistic_regression" in summary["models"]
    assert "naive_bayes" in summary["models"]


def test_comparison_dataframe():
    df = get_comparison_dataframe()
    assert df is not None
    assert "Model" in df.columns
    assert "Accuracy (%)" in df.columns
    assert "Precision (%)" in df.columns
    assert "Recall (%)" in df.columns
    assert "F1-Score (%)" in df.columns
    assert "ROC-AUC" in df.columns
    # Check that accuracy is greater than 80%
    for acc in df["Accuracy (%)"]:
        assert acc >= 80.0


def test_confusion_matrix_shape_and_counts():
    cm = get_model_confusion_matrix("logistic_regression")
    assert cm is not None
    assert len(cm) == 2
    assert len(cm[0]) == 2
    assert len(cm[1]) == 2
    total_test_samples = cm[0][0] + cm[0][1] + cm[1][0] + cm[1][1]
    assert total_test_samples == 10000


def test_roc_curve_properties():
    roc = get_model_roc_curve("logistic_regression")
    assert roc is not None
    assert "fpr" in roc
    assert "tpr" in roc
    assert "auc" in roc
    assert 0.85 <= roc["auc"] <= 1.0
    assert len(roc["fpr"]) == len(roc["tpr"])
    assert min(roc["fpr"]) >= 0.0
    assert max(roc["fpr"]) <= 1.0


def test_top_predictive_features():
    feats, err = load_top_predictive_features()
    assert err is None
    assert feats is not None
    assert "positive" in feats
    assert "negative" in feats
    assert len(feats["positive"]) > 0
    assert len(feats["negative"]) > 0
    # Positives should have positive weights, negatives should have negative weights
    assert feats["positive"][0]["weight"] > 0
    assert feats["negative"][0]["weight"] < 0

