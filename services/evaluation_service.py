"""
Evaluation metrics service for CineSense.
Loads, formats, and serves verified offline benchmark metrics,
confusion matrices, ROC curves, and model comparison data.
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

EVALUATION_PATH = os.path.join("models", "evaluation_summary.json")
TOP_FEATURES_PATH = os.path.join("models", "top_features.json")
TEST_PREDICTIONS_PATH = os.path.join("data", "test_predictions.csv")


def load_evaluation_summary() -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Load the persisted evaluation metrics computed on the test set."""
    if not os.path.exists(EVALUATION_PATH):
        return None, (
            "Evaluation summary not found at 'models/evaluation_summary.json'. "
            "Please run 'python scripts/train_models.py' to fit the models and generate benchmark metrics."
        )
    try:
        with open(EVALUATION_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data, None
    except Exception as exc:
        return None, f"Failed to parse evaluation metrics: {str(exc)}"


def get_available_models_meta() -> Dict[str, Dict[str, Any]]:
    """Return dictionary of models and their availability status."""
    summary, err = load_evaluation_summary()
    if not summary or "models" not in summary:
        return {}
    return summary["models"]


def get_comparison_dataframe() -> Optional[pd.DataFrame]:
    """Return a tabular DataFrame comparing all available models on key metrics."""
    summary, err = load_evaluation_summary()
    if not summary or "models" not in summary:
        return None

    rows = []
    for model_key, details in summary["models"].items():
        if details.get("status") == "available" and "accuracy" in details:
            rows.append({
                "Model": details.get("name", model_key),
                "Accuracy (%)": round(details["accuracy"] * 100, 2),
                "Precision (%)": round(details["precision"] * 100, 2),
                "Recall (%)": round(details["recall"] * 100, 2),
                "F1-Score (%)": round(details["f1"] * 100, 2),
                "ROC-AUC": round(details["roc_auc"], 4),
                "Feature Extraction": details.get("feature_extractor", "N/A"),
            })

    if not rows:
        return None

    df = pd.DataFrame(rows)
    return df


def get_formatted_comparison_dataframe(comp_df: Optional[pd.DataFrame] = None) -> Optional[pd.DataFrame]:
    """
    Format comparison dataframe with '▲' marking the highest/best value in each numeric column.
    Scored on 10,000 held-out reviews. A triangle marks the best value in each column.
    """
    if comp_df is None:
        comp_df = get_comparison_dataframe()
    if comp_df is None or comp_df.empty:
        return None

    df_display = comp_df.copy()
    metric_cols = ["Accuracy (%)", "Precision (%)", "Recall (%)", "F1-Score (%)", "ROC-AUC"]
    for col in metric_cols:
        if col in df_display.columns:
            max_val = df_display[col].max()
            df_display[col] = df_display[col].apply(
                lambda v: f"▲ {v:.2f}%" if "ROC" not in col and v == max_val
                else (f"▲ {v:.4f}" if "ROC" in col and v == max_val
                else (f"{v:.2f}%" if "ROC" not in col else f"{v:.4f}"))
            )
    return df_display


def get_model_confusion_matrix(model_key: str) -> Optional[List[List[int]]]:
    """Retrieve the 2x2 confusion matrix [[TN, FP], [FN, TP]] for a model."""
    summary, _ = load_evaluation_summary()
    if not summary or "models" not in summary:
        return None
    model_data = summary["models"].get(model_key)
    if not model_data or "confusion_matrix" not in model_data:
        return None
    return model_data["confusion_matrix"]


def get_model_roc_curve(model_key: str) -> Optional[Dict[str, Any]]:
    """Retrieve the ROC curve data {fpr, tpr, auc} for a model."""
    summary, _ = load_evaluation_summary()
    if not summary or "models" not in summary:
        return None
    model_data = summary["models"].get(model_key)
    if not model_data or "roc_curve" not in model_data:
        return None
    return model_data["roc_curve"]


def load_top_predictive_features() -> Tuple[Optional[Dict[str, List[Dict[str, Any]]]], Optional[str]]:
    """Load top positive and negative vocabulary features from Logistic Regression."""
    if not os.path.exists(TOP_FEATURES_PATH):
        return None, "Predictive feature weights not found."
    try:
        with open(TOP_FEATURES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data, None
    except Exception as exc:
        return None, f"Failed to load predictive features: {str(exc)}"


def load_test_predictions() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Load precomputed model predictions on the 10,000 test split from data/test_predictions.csv.
    Returns None and an actionable prompt message if the file is missing.
    """
    if not os.path.exists(TEST_PREDICTIONS_PATH):
        return None, (
            "Test predictions dataset 'data/test_predictions.csv' is missing. "
            "Please generate it by running: python scripts/export_predictions.py"
        )
    try:
        df = pd.read_csv(TEST_PREDICTIONS_PATH)
        required_cols = {"review_id", "text", "label", "lr_pred", "nb_pred", "lstm_pred"}
        if not required_cols.issubset(set(df.columns)):
            return None, f"Missing required columns in test_predictions.csv: {required_cols - set(df.columns)}"
        return df, None
    except Exception as exc:
        return None, f"Failed to read test predictions CSV: {str(exc)}"


def compute_failure_patterns(df: pd.DataFrame, model_key: str = "all") -> Dict[str, Any]:
    """
    Compute verified empirical error rates across specific linguistic failure patterns:
    - Negation constructs: 'not', 'never', 'no', \"n't\"
    - Contrastive transitions: 'but', 'however'
    - High-length reviews: > 500 words
    """
    total = len(df)
    if total == 0:
        return {"patterns": [], "overall_error_rate": 0.0}

    # Determine error mask based on selected model
    if model_key == "logistic_regression" or model_key == "lr":
        err_mask = df["lr_pred"] != df["label"]
    elif model_key == "naive_bayes" or model_key == "nb":
        err_mask = df["nb_pred"] != df["label"]
    elif model_key == "bilstm" or model_key == "lstm":
        err_mask = df["lstm_pred"] != df["label"]
    else:  # "all" - any model misclassified
        err_mask = (df["lr_pred"] != df["label"]) | (df["nb_pred"] != df["label"]) | (df["lstm_pred"] != df["label"])

    overall_error_rate = float(round(err_mask.mean() * 100, 2))

    # Pattern masks (non-capturing groups to prevent regex user warnings)
    neg_mask = df["text"].astype(str).str.contains(r"\b(?:not|never|no|n't)\b", case=False, regex=True)
    but_mask = df["text"].astype(str).str.contains(r"\b(?:but|however)\b", case=False, regex=True)
    long_mask = df["text"].astype(str).apply(lambda t: len(t.split()) > 500)

    patterns = [
        {
            "pattern": "Negation ('not', 'never', 'no', 'n\\'t')",
            "count": int(neg_mask.sum()),
            "errors": int((err_mask & neg_mask).sum()),
            "error_rate": float(round((err_mask[neg_mask].mean() * 100), 2)) if neg_mask.sum() > 0 else 0.0,
        },
        {
            "pattern": "Contrastive ('but', 'however')",
            "count": int(but_mask.sum()),
            "errors": int((err_mask & but_mask).sum()),
            "error_rate": float(round((err_mask[but_mask].mean() * 100), 2)) if but_mask.sum() > 0 else 0.0,
        },
        {
            "pattern": "High word count (> 500 words)",
            "count": int(long_mask.sum()),
            "errors": int((err_mask & long_mask).sum()),
            "error_rate": float(round((err_mask[long_mask].mean() * 100), 2)) if long_mask.sum() > 0 else 0.0,
        },
    ]

    return {
        "patterns": patterns,
        "overall_error_rate": overall_error_rate,
        "total_evaluated": total,
    }


