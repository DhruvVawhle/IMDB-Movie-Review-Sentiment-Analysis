"""
Prediction and inference service for CineSense.
Handles lazy artifact loading, input validation, real model inference,
calibrated confidence estimation, and multi-model comparison.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np

from services.preprocessing import clean_html_and_urls, normalize_text, preprocess_text, tokenize_text

# Model artifact paths
LR_MODEL_PATH = os.path.join("models", "logistic_regression.joblib")
TFIDF_PATH = os.path.join("models", "tfidf_vectorizer.joblib")
NB_MODEL_PATH = os.path.join("models", "naive_bayes.joblib")
CV_PATH = os.path.join("models", "count_vectorizer.joblib")
BILSTM_MODEL_PATH = os.path.join("models", "bilstm_model.pt")
BILSTM_VOCAB_PATH = os.path.join("models", "bilstm_vocab.json")

# In-memory cached artifacts
_MODELS_CACHE: Dict[str, Any] = {}

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


def is_model_available(model_key: str) -> bool:
    """Check if all required artifacts for a model exist on disk."""
    if model_key == "logistic_regression":
        return os.path.exists(LR_MODEL_PATH) and os.path.exists(TFIDF_PATH)
    elif model_key == "naive_bayes":
        return os.path.exists(NB_MODEL_PATH) and os.path.exists(CV_PATH)
    elif model_key == "bilstm":
        return os.path.exists(BILSTM_MODEL_PATH) and os.path.exists(BILSTM_VOCAB_PATH)
    return False


def get_available_models_list() -> List[Dict[str, str]]:
    """Return list of models with their availability and descriptions."""
    models = [
        {
            "id": "logistic_regression",
            "name": "Logistic Regression (TF-IDF)",
            "available": is_model_available("logistic_regression"),
            "description": "L2-regularized linear classifier over unigram and bigram TF-IDF representations. Highly interpretable.",
        },
        {
            "id": "naive_bayes",
            "name": "Multinomial Naive Bayes (Bag of Words)",
            "available": is_model_available("naive_bayes"),
            "description": "Probabilistic generative model over word count frequencies with Laplace smoothing (alpha=0.1).",
        },
        {
            "id": "bilstm",
            "name": "Bidirectional LSTM (Neural Sequence)",
            "available": is_model_available("bilstm"),
            "description": "Deep bidirectional recurrent network capturing sequential context and semantic ordering.",
        },
    ]
    return models


def load_artifacts(model_key: str) -> Tuple[Optional[Any], Optional[Any], Optional[str]]:
    """Load model and its paired vectorizer/tokenizer from disk with memory caching."""
    global _MODELS_CACHE
    if model_key in _MODELS_CACHE:
        return _MODELS_CACHE[model_key]["model"], _MODELS_CACHE[model_key]["extractor"], None

    if not is_model_available(model_key):
        return None, None, f"Model artifacts for '{model_key}' are not present on disk."

    try:
        if model_key == "logistic_regression":
            model = joblib.load(LR_MODEL_PATH)
            extractor = joblib.load(TFIDF_PATH)
            _MODELS_CACHE[model_key] = {"model": model, "extractor": extractor}
            return model, extractor, None

        elif model_key == "naive_bayes":
            model = joblib.load(NB_MODEL_PATH)
            extractor = joblib.load(CV_PATH)
            _MODELS_CACHE[model_key] = {"model": model, "extractor": extractor}
            return model, extractor, None

        elif model_key == "bilstm":
            import torch
            import torch.nn as nn

            with open(BILSTM_VOCAB_PATH, "r", encoding="utf-8") as f:
                vocab = json.load(f)

            class PyTorchBiLSTM(nn.Module):
                def __init__(self, vocab_size=20000, embed_dim=64, hidden_dim=64):
                    super().__init__()
                    self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
                    self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
                    self.fc1 = nn.Linear(hidden_dim * 2, 64)
                    self.dropout1 = nn.Dropout(0.4)
                    self.fc2 = nn.Linear(64, 32)
                    self.dropout2 = nn.Dropout(0.3)
                    self.out = nn.Linear(32, 1)
                    self.relu = nn.ReLU()
                    self.sigmoid = nn.Sigmoid()

                def forward(self, x):
                    embeds = self.embedding(x)
                    out, _ = self.lstm(embeds)
                    pooled = torch.max(out, dim=1)[0]
                    h1 = self.relu(self.fc1(pooled))
                    h1 = self.dropout1(h1)
                    h2 = self.relu(self.fc2(h1))
                    h2 = self.dropout2(h2)
                    logits = self.out(h2)
                    return self.sigmoid(logits)

            model = PyTorchBiLSTM(vocab_size=len(vocab))
            model.load_state_dict(torch.load(BILSTM_MODEL_PATH, map_location=torch.device("cpu")))
            model.eval()

            _MODELS_CACHE[model_key] = {"model": model, "extractor": vocab}
            return model, vocab, None

        return None, None, f"Unknown model identifier '{model_key}'."
    except Exception as exc:
        return None, None, f"Failed to load artifacts for {model_key}: {str(exc)}"


if HAS_STREAMLIT:
    @st.cache_resource(show_spinner=False)
    def get_cached_artifacts(model_key: str) -> Tuple[Optional[Any], Optional[Any], Optional[str]]:
        """Wrap existing load_artifacts in @st.cache_resource to ensure single load across sessions."""
        return load_artifacts(model_key)

    @st.cache_resource(show_spinner=False)
    def preload_all_models() -> Dict[str, bool]:
        """Preload all three model artifacts once so the first user interaction has zero disk delay."""
        status = {}
        for key in ["logistic_regression", "naive_bayes", "bilstm"]:
            if is_model_available(key):
                m, _, _ = get_cached_artifacts(key)
                status[key] = m is not None
        return status
else:
    def get_cached_artifacts(model_key: str) -> Tuple[Optional[Any], Optional[Any], Optional[str]]:
        return load_artifacts(model_key)

    def preload_all_models() -> Dict[str, bool]:
        status = {}
        for key in ["logistic_regression", "naive_bayes", "bilstm"]:
            if is_model_available(key):
                m, _, _ = load_artifacts(key)
                status[key] = m is not None
        return status


def validate_review_input(text: str, max_chars: int = 15000) -> Tuple[bool, Optional[str]]:
    """Validate review string before inference."""
    if text is None or not isinstance(text, str):
        return False, "Review input must be a valid text string."
    stripped = text.strip()
    if len(stripped) == 0:
        return False, "Please enter a review to analyze. Empty inputs cannot be evaluated."
    if len(stripped) > max_chars:
        return False, f"Review exceeds maximum allowed length ({len(stripped)} / {max_chars} characters)."
    # Check if there is at least one alphabetical word
    if not re.search(r"[a-zA-Z]", stripped):
        return False, "The review contains no alphabetic words or readable text."
    return True, None


def get_confidence_explanation(model_key: str, positive_prob: float) -> str:
    """Generate educational explanation contrasting predicted probability with calibration."""
    prob_val = round(positive_prob * 100, 1)
    if model_key == "naive_bayes":
        return (
            f"Naive Bayes estimates a {prob_val}% posterior probability. Note: Due to the strong feature independence "
            "assumption in Naive Bayes, probabilities tend to push toward the extremes (0% or 100%) and may not reflect "
            "empirically calibrated frequencies."
        )
    elif model_key == "logistic_regression":
        return (
            f"Logistic Regression predicts a {prob_val}% positive probability. Because it minimizes log-loss (cross-entropy) "
            "on balanced training data, this output directly approximates calibrated posterior odds."
        )
    elif model_key == "bilstm":
        return (
            f"The BiLSTM neural network outputs a {prob_val}% sigmoid activation from global max-pooled sequence features. "
            "It captures temporal phrasing and negation, but deep network outputs may benefit from temperature scaling for perfect calibration."
        )
    return f"Model estimated posterior positive probability: {prob_val}%."


def predict_sentiment(
    text: str,
    model_key: str = "logistic_regression",
) -> Dict[str, Any]:
    """
    Perform real-time sentiment prediction using fitted model artifacts.
    Returns structured prediction metadata.
    """
    valid, err_msg = validate_review_input(text)
    if not valid:
        return {
            "success": False,
            "error": err_msg,
        }

    model, extractor, load_err = get_cached_artifacts(model_key)
    if load_err or model is None:
        return {
            "success": False,
            "error": load_err or f"Model '{model_key}' is unavailable.",
        }

    # Canonical preprocessing
    clean_text = preprocess_text(text)
    if not clean_text.strip():
        return {
            "success": False,
            "error": "After removing stopwords and non-alphabetical characters, no meaningful tokens remained. Try adding more descriptive words.",
        }

    tokens = clean_text.split()

    try:
        if model_key == "logistic_regression":
            vec = extractor.transform([clean_text])
            probs = model.predict_proba(vec)[0]
            pos_prob = float(probs[1])
            neg_prob = float(probs[0])
            
            # Extract salient features from this specific review
            feature_names = extractor.get_feature_names_out()
            coefs = model.coef_[0]
            active_indices = vec.nonzero()[1]
            active_features = []
            for idx in active_indices:
                term = feature_names[idx]
                weight = float(coefs[idx])
                active_features.append({
                    "term": term,
                    "weight": round(weight, 3),
                    "sentiment": "positive" if weight > 0 else "negative"
                })
            active_features.sort(key=lambda x: abs(x["weight"]), reverse=True)

        elif model_key == "naive_bayes":
            vec = extractor.transform([clean_text])
            probs = model.predict_proba(vec)[0]
            pos_prob = float(probs[1])
            neg_prob = float(probs[0])
            active_features = []

        elif model_key == "bilstm":
            import torch
            vocab = extractor
            max_len = 200
            seq = [vocab.get(w, 1) for w in tokens[:max_len]]
            if len(seq) < max_len:
                seq = seq + [0] * (max_len - len(seq))
            tensor_seq = torch.tensor([seq], dtype=torch.int64)
            with torch.no_grad():
                prob_val = float(model(tensor_seq).item())
            pos_prob = prob_val
            neg_prob = 1.0 - prob_val
            active_features = []

        else:
            return {"success": False, "error": f"Unsupported model '{model_key}'."}

        is_positive = pos_prob >= 0.5
        label = "POSITIVE" if is_positive else "NEGATIVE"
        confidence = pos_prob if is_positive else neg_prob

        explanation = get_confidence_explanation(model_key, pos_prob)

        return {
            "success": True,
            "model_id": model_key,
            "label": label,
            "is_positive": is_positive,
            "positive_probability": round(pos_prob, 4),
            "negative_probability": round(neg_prob, 4),
            "confidence": round(confidence, 4),
            "confidence_percentage": round(confidence * 100, 1),
            "clean_text": clean_text,
            "token_count": len(tokens),
            "active_features": active_features[:15] if model_key == "logistic_regression" else [],
            "calibration_explanation": explanation,
        }

    except Exception as exc:
        return {
            "success": False,
            "error": f"Inference execution failed: {str(exc)}",
        }


def compare_all_models(text: str) -> Dict[str, Any]:
    """Run all available models against the review and return comparison results."""
    valid, err_msg = validate_review_input(text)
    if not valid:
        return {"success": False, "error": err_msg}

    available_models = get_available_models_list()
    results = {}
    for item in available_models:
        m_id = item["id"]
        if item["available"]:
            res = predict_sentiment(text, model_key=m_id)
            if res.get("success"):
                results[m_id] = {
                    "name": item["name"],
                    "label": res["label"],
                    "is_positive": res["is_positive"],
                    "positive_prob": res["positive_probability"],
                    "negative_prob": res["negative_probability"],
                    "confidence": res["confidence_percentage"],
                }

    return {
        "success": True,
        "results": results,
    }

