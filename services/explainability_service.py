"""
CineSense — Explainability & LIME Interpretation Service.
Provides local model interpretability via LIME (Local Interpretable Model-agnostic Explanations):
- Batched probability prediction wrappers for Logistic Regression, Naive Bayes, and BiLSTM
- Inline text word highlighting with double-cued semantic styling (solid underline for positive, dotted for negative)
- Opacity scaled to LIME feature attribution weights
- Accessible title tooltips with polarity and numeric weight
- Error handling for empty reviews, length limits (>2,000 words truncation), and LIME execution fallbacks
- Streamlit caching via @st.cache_data keyed on (review_text, model_name)
"""

import html
import re
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

from services.prediction_service import load_artifacts, validate_review_input
from services.preprocessing import clean_html_and_urls, normalize_text, _init_nltk_resources

# One-line educational takeaway required by UX specification
EXPLANATION_DISCLAIMER = (
    "Highlights show which words changed this model's score. "
    "They are not proof of why the model is right."
)

# In-memory lemma cache for fast perturbed text preprocessing
_LEMMA_CACHE: Dict[str, str] = {}
_STOP_WORDS_SET: Optional[set] = None
_LEMMATIZER_INST: Optional[Any] = None
_WORD_REGEX = re.compile(r"[a-z]{3,}")


def _get_nltk_helpers() -> Tuple[set, Any]:
    global _STOP_WORDS_SET, _LEMMATIZER_INST
    if _STOP_WORDS_SET is None or _LEMMATIZER_INST is None:
        sw, lem, _ = _init_nltk_resources()
        _STOP_WORDS_SET = sw
        _LEMMATIZER_INST = lem
    return _STOP_WORDS_SET, _LEMMATIZER_INST


def _fast_preprocess(text: str) -> str:
    """
    High-speed preprocessing optimized for LIME's 300 perturbed samples.
    Reuses cached lemmatizations to achieve sub-second LIME runtimes.
    """
    if not isinstance(text, str) or not text.strip():
        return ""
    stop_words, lemmatizer = _get_nltk_helpers()
    tokens = _WORD_REGEX.findall(text.lower())
    processed = []
    for t in tokens:
        if t not in stop_words:
            lem = _LEMMA_CACHE.get(t)
            if lem is None:
                lem = lemmatizer.lemmatize(t)
                _LEMMA_CACHE[t] = lem
            processed.append(lem)
    return " ".join(processed)


def predict_proba_wrapper(texts: List[str], model_key: str) -> np.ndarray:
    """
    Standardized predict_proba wrapper compatible with LIME.
    Returns np.ndarray of shape (N, 2) where:
      Column 0: Negative class probability
      Column 1: Positive class probability
    Probabilities are guaranteed to sum to 1.0.
    """
    if not texts:
        return np.empty((0, 2), dtype=float)

    model, extractor, err = load_artifacts(model_key)
    if err or model is None or extractor is None:
        raise RuntimeError(f"Cannot load artifacts for model '{model_key}': {err}")

    # Fast preprocessing for all input strings
    cleaned_texts = [_fast_preprocess(t) for t in texts]

    if model_key == "logistic_regression":
        vecs = extractor.transform(cleaned_texts)
        probs = model.predict_proba(vecs)
        # Ensure exact shape and normalization
        probs = np.clip(probs, 0.0, 1.0)
        row_sums = probs.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        return probs / row_sums

    elif model_key == "naive_bayes":
        vecs = extractor.transform(cleaned_texts)
        probs = model.predict_proba(vecs)
        probs = np.clip(probs, 0.0, 1.0)
        row_sums = probs.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        return probs / row_sums

    elif model_key == "bilstm":
        import torch
        vocab = extractor
        max_len = 200
        seqs = []
        for c_text in cleaned_texts:
            tokens = c_text.split()[:max_len]
            seq = [vocab.get(w, 1) for w in tokens]
            if len(seq) < max_len:
                seq = seq + [0] * (max_len - len(seq))
            seqs.append(seq)

        seq_tensor = torch.tensor(seqs, dtype=torch.int64)
        model.eval()

        # Batch forward passes to keep under 5 seconds
        batch_size = 256
        pos_probs_list = []
        with torch.no_grad():
            for b_idx in range(0, len(seq_tensor), batch_size):
                b_x = seq_tensor[b_idx : b_idx + batch_size]
                out = model(b_x).squeeze(-1).cpu().numpy()
                if out.ndim == 0:
                    out = np.array([float(out)])
                pos_probs_list.extend(out.tolist())

        pos_probs = np.clip(np.array(pos_probs_list, dtype=float), 0.0, 1.0)
        neg_probs = 1.0 - pos_probs
        return np.column_stack([neg_probs, pos_probs])

    else:
        raise ValueError(f"Unsupported model key for LIME explanation: {model_key}")


def generate_highlighted_html(
    text: str,
    feature_weights: List[Tuple[str, float]],
    theme_mode: str = "light",
) -> str:
    """
    Render review text with inline word highlights:
    - Green background for words pushing Positive, red for Negative
    - Opacity scaled to absolute weight
    - Double-cued: Solid underline for Positive, dotted underline for Negative
    - Title tooltip attribute: 'pushes Positive (+0.12)' or 'pushes Negative (-0.08)'
    - Neutral words remain plain
    """
    if not text:
        return ""

    if not feature_weights:
        return f'<div class="highlighted-review-box">{html.escape(text)}</div>'

    # Build dictionary of word -> weight (case-insensitive)
    word_weight_map: Dict[str, float] = {}
    max_abs_wt = 0.0001
    for word, wt in feature_weights:
        w_lower = str(word).lower()
        word_weight_map[w_lower] = float(wt)
        if abs(wt) > max_abs_wt:
            max_abs_wt = abs(wt)

    # Color tokens depending on theme
    if theme_mode == "dark":
        pos_rgb = "79, 199, 150"
        neg_rgb = "242, 124, 142"
        pos_border = "#4FC796"
        neg_border = "#F27C8E"
    else:
        pos_rgb = "23, 120, 90"
        neg_rgb = "191, 50, 72"
        pos_border = "#17785A"
        neg_border = "#BF3248"

    # Tokenize preserving whitespace and punctuation
    # Regex splits by word boundary or non-word sequence
    tokens = re.findall(r"\w+|\W+", text)

    highlighted_parts: List[str] = []
    for token in tokens:
        # Check if alphanumeric word
        tok_lower = token.lower()
        if tok_lower in word_weight_map:
            wt = word_weight_map[tok_lower]
            ratio = min(1.0, max(0.15, abs(wt) / max_abs_wt))
            alpha = 0.12 + ratio * 0.40  # 0.12 to 0.52 opacity

            if wt > 0:
                color_bg = f"rgba({pos_rgb}, {alpha:.2f})"
                underline_style = f"border-bottom: 2px solid {pos_border};"
                tooltip = f"pushes Positive (+{wt:.2f})"
                aria_label = f"{token} pushes Positive"
            else:
                color_bg = f"rgba({neg_rgb}, {alpha:.2f})"
                underline_style = f"border-bottom: 2px dotted {neg_border};"
                tooltip = f"pushes Negative ({wt:.2f})"
                aria_label = f"{token} pushes Negative"

            span_html = (
                f'<span class="lime-highlight" '
                f'style="background-color:{color_bg}; {underline_style} padding:1px 3px; border-radius:3px; font-weight:500; cursor:help;" '
                f'title="{tooltip}" aria-label="{aria_label}">{html.escape(token)}</span>'
            )
            highlighted_parts.append(span_html)
        else:
            # Preserve linebreaks as <br /> or keep plain
            escaped = html.escape(token).replace("\n", "<br />")
            highlighted_parts.append(escaped)

    content_html = "".join(highlighted_parts)
    return (
        f'<div class="highlighted-review-box" style="'
        f'background:var(--surface); border:1px solid var(--line); border-radius:6px; '
        f'padding:1rem 1.15rem; font-family:var(--font-body); font-size:0.95rem; line-height:1.75; '
        f'color:var(--ink); margin-top:0.75rem; margin-bottom:0.75rem;">'
        f'{content_html}'
        f'</div>'
    )


def compute_lime_explanation_raw(
    review_text: str,
    model_name: str,
    num_features: int = 10,
    num_samples: int = 300,
) -> Dict[str, Any]:
    """
    Internal LIME explanation runner.
    Handles:
    - Input validation
    - Truncation of reviews > 2,000 words
    - LIME execution
    - Fallback on failure
    """
    t0 = time.time()
    valid, err_msg = validate_review_input(review_text)
    if not valid:
        return {
            "success": False,
            "error": err_msg or "Invalid review input.",
            "duration": 0.0,
            "features": [],
            "highlighted_html": "",
        }

    # Word count check and truncation (> 2,000 words)
    words = review_text.split()
    truncated = False
    active_text = review_text
    truncation_note = None
    if len(words) > 2000:
        active_text = " ".join(words[:2000])
        truncated = True
        truncation_note = f"Review length ({len(words):,} words) exceeded 2,000 words. Truncated to first 2,000 words for explanation analysis."

    try:
        from lime.lime_text import LimeTextExplainer

        explainer = LimeTextExplainer(
            class_names=["Negative", "Positive"],
            random_state=42,
            bow=True,
        )

        def classifier_fn(batch_texts: List[str]) -> np.ndarray:
            return predict_proba_wrapper(batch_texts, model_name)

        exp = explainer.explain_instance(
            active_text,
            classifier_fn,
            num_features=num_features,
            num_samples=num_samples,
            labels=(1,),  # Positive class index
        )

        features = exp.as_list(label=1)
        duration = round(time.time() - t0, 3)

        return {
            "success": True,
            "model_name": model_name,
            "duration": duration,
            "truncated": truncated,
            "truncation_note": truncation_note,
            "features": features,
            "original_text": active_text,
            "disclaimer": EXPLANATION_DISCLAIMER,
        }

    except Exception as exc:
        duration = round(time.time() - t0, 3)
        return {
            "success": False,
            "error": f"LIME explanation generation failed: {str(exc)}",
            "duration": duration,
            "features": [],
            "disclaimer": EXPLANATION_DISCLAIMER,
        }


# Streamlit Cached Wrapper
if HAS_STREAMLIT:
    @st.cache_data(show_spinner=False)
    def get_lime_explanation_cached(
        review_text: str,
        model_name: str,
        num_features: int = 10,
        num_samples: int = 300,
    ) -> Dict[str, Any]:
        """Cache LIME explanations keyed on (review_text, model_name)."""
        return compute_lime_explanation_raw(
            review_text=review_text,
            model_name=model_name,
            num_features=num_features,
            num_samples=num_samples,
        )
else:
    def get_lime_explanation_cached(
        review_text: str,
        model_name: str,
        num_features: int = 10,
        num_samples: int = 300,
    ) -> Dict[str, Any]:
        return compute_lime_explanation_raw(
            review_text=review_text,
            model_name=model_name,
            num_features=num_features,
            num_samples=num_samples,
        )
