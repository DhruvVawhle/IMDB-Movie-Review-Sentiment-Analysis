"""
Contextual NLP and LLM Intelligence Service for CineSense.
Connects to OpenRouter API to provide deep cinematic context, aspect-level
sentiment, nuance, and tone analysis for movie reviews, backed by a robust
deterministic local NLP heuristic engine if the API fails or is unavailable.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple
import requests
import streamlit as st

# Prioritized free/fast OpenRouter models
OPENROUTER_CANDIDATE_MODELS = [
    "liquid/lfm-2.5-2.6b:free",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3.5-lightning:free",
]

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Cinematic Aspect Lexicons for Local NLP Fallback Engine
ASPECT_PATTERNS = {
    "Direction & Craft": [
        "direct", "direction", "director", "vision", "visionary", "pacing", "pace",
        "editing", "craft", "auteur", "execution", "framing", "ambition", "style"
    ],
    "Acting & Performances": [
        "acting", "actor", "actress", "performance", "performances", "cast", "role",
        "character", "portrayal", "chemistry", "lead", "presence", "dialogue delivery"
    ],
    "Cinematography & Visuals": [
        "cinematography", "visual", "visuals", "camera", "lighting", "aesthetic",
        "shot", "spectacle", "cgi", "imagery", "composition", "effects"
    ],
    "Screenplay & Narrative": [
        "screenplay", "script", "story", "plot", "narrative", "writing", "twist",
        "premise", "dialogue", "arc", "climax", "second act", "third act", "concept"
    ],
    "Soundtrack & Score": [
        "soundtrack", "score", "music", "audio", "sound design", "sound", "theme", "orchestration"
    ],
}

POSITIVE_CINEMA_WORDS = {
    "masterpiece", "flawless", "brilliant", "superb", "breathtaking", "indelible",
    "peerless", "affecting", "compelling", "remarkable", "riveting", "transcendent",
    "sublime", "electrifying", "gripping", "poignant", "visceral", "stunning",
    "phenomenal", "exceptional", "great", "excellent", "fun", "solid", "entertaining"
}

NEGATIVE_CINEMA_WORDS = {
    "waste", "terrible", "horrible", "disjointed", "cliche", "clichés", "cliched",
    "artificial", "boring", "drag", "drags", "insulting", "pretentious", "shallow",
    "flat", "forgettable", "awful", "weak", "mess", "unwatchable", "uninspired",
    "disappointing", "predictable", "tedious", "cringe"
}


def get_openrouter_api_key() -> Optional[str]:
    """Retrieve the OpenRouter API key from st.secrets, environment, or .env."""
    # 1. Try Streamlit secrets
    try:
        if hasattr(st, "secrets") and "OPENROUTER_API_KEY" in st.secrets:
            key = str(st.secrets["OPENROUTER_API_KEY"]).strip()
            if key and not key.startswith("your_"):
                return key
    except Exception:
        pass

    # 2. Try os.environ
    env_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if env_key:
        return env_key

    # 3. Try reading directly from .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("OPENROUTER_API_KEY="):
                        val = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            return val
        except Exception:
            pass

    return None


@st.cache_data(show_spinner=False, ttl=3600)
def analyze_movie_context_cached(
    review_text: str,
    movie_title: Optional[str] = None,
    force_fallback: bool = False,
) -> Dict[str, Any]:
    """Cached wrapper around contextual NLP analysis to prevent redundant API queries."""
    return analyze_movie_context(review_text, movie_title=movie_title, force_fallback=force_fallback)


def analyze_movie_context(
    review_text: str,
    movie_title: Optional[str] = None,
    force_fallback: bool = False,
) -> Dict[str, Any]:
    """
    Main entry point for contextual NLP analysis.
    Attempts live LLM reasoning via OpenRouter API with multi-model failover;
    gracefully drops to a deterministic local NLP heuristic engine if the API fails.
    """
    if not review_text or not review_text.strip():
        return {
            "summary": "No review text provided for contextual analysis.",
            "aspects": [],
            "tone": "Neutral",
            "nuance": "N/A",
            "verdict": "Indeterminate",
            "engine": "Local NLP Engine",
            "is_fallback": True,
            "status_message": "Awaiting review text input.",
        }

    api_key = get_openrouter_api_key()

    # If no key configured or fallback forced, run local NLP engine directly
    if force_fallback or not api_key:
        status_msg = (
            "Local NLP Engine active (no OpenRouter API key configured)."
            if not api_key else "Local NLP Engine active (offline fallback mode)."
        )
        return _heuristic_context_fallback(review_text, movie_title, failure_reason=status_msg)

    # Attempt OpenRouter API across candidate models
    llm_result, error_reason = _call_openrouter_api(review_text, movie_title, api_key)
    if llm_result:
        return llm_result

    # Fallback seamlessly to local heuristic NLP engine on API failure
    return _heuristic_context_fallback(review_text, movie_title, failure_reason=error_reason)


def _call_openrouter_api(
    review_text: str,
    movie_title: Optional[str],
    api_key: str,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Call OpenRouter API with prioritized model failover and parse structured JSON.
    Returns (result_dict, None) on success or (None, error_str) on failure.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://cinesense.ai",
        "X-Title": "CineSense Movie Intelligence",
        "Content-Type": "application/json",
    }

    movie_ctx = f"Film Title: {movie_title}\n" if movie_title else ""
    prompt = f"""You are a film critic and natural language processing expert.
Analyze the following movie review to extract deep contextual cinematic insights.

{movie_ctx}Review text:
\"\"\"{review_text[:2000]}\"\"\"

Return ONLY a valid JSON object without markdown fences, preamble, or commentary with this exact schema:
{{
  "summary": "A concise 1-sentence contextual summary of the review's core argument.",
  "aspects": [
    {{"aspect": "Direction & Craft", "sentiment": "Positive|Mixed|Negative", "detail": "Concise detail"}},
    {{"aspect": "Acting & Performances", "sentiment": "Positive|Mixed|Negative", "detail": "Concise detail"}}
  ],
  "tone": "Brief tone descriptor (e.g., Rapturous, Caustic, Analytical, Sarcastic)",
  "nuance": "Key nuance or subtext note (e.g., praise qualified by weak pacing; sarcasm detected).",
  "verdict": "Short contextual verdict (e.g., Unanimous Recommendation, Critical Pan, Mixed Verdict)"
}}
"""

    last_error = "OpenRouter request failed"
    # Try top candidate models (max 3 attempts to keep response snappy)
    candidates_to_try = OPENROUTER_CANDIDATE_MODELS[:3]

    for model in candidates_to_try:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional film context analyzer. Always output strict valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 450,
            "temperature": 0.2,
        }

        try:
            resp = requests.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
                timeout=5.0,  # Strict timeout for snappy UI
            )

            if resp.status_code == 200:
                body = resp.json()
                choices = body.get("choices", [])
                if not choices:
                    last_error = f"{model} returned empty choices"
                    continue

                content = choices[0].get("message", {}).get("content", "")
                if not content and "reasoning" in choices[0].get("message", {}):
                    content = choices[0]["message"]["reasoning"]

                if not content:
                    last_error = f"{model} returned blank content"
                    continue

                parsed = _extract_json_from_llm(content)
                if parsed and "summary" in parsed:
                    aspects = parsed.get("aspects", [])
                    if not isinstance(aspects, list):
                        aspects = []

                    return {
                        "summary": str(parsed.get("summary", "Review context analyzed.")),
                        "aspects": aspects[:5],
                        "tone": str(parsed.get("tone", "Analytical")),
                        "nuance": str(parsed.get("nuance", "Balanced critical perspective.")),
                        "verdict": str(parsed.get("verdict", "Evaluated")),
                        "engine": f"OpenRouter AI ({model.split(':')[0]})",
                        "is_fallback": False,
                        "status_message": f"Live LLM context reasoning powered by {model.split(':')[0]} via OpenRouter.",
                    }, None
                else:
                    last_error = f"{model} JSON parsing failed"
            elif resp.status_code == 429:
                last_error = f"Rate limited upstream on {model} (HTTP 429)"
            elif resp.status_code == 502:
                last_error = f"Model provider temporarily unavailable for {model} (HTTP 502)"
            elif resp.status_code == 402:
                last_error = "OpenRouter free credits exhausted (HTTP 402)"
            else:
                last_error = f"OpenRouter status {resp.status_code}"

        except requests.exceptions.Timeout:
            last_error = f"OpenRouter model {model} timed out (>5s)"
        except Exception as exc:
            last_error = f"Connection error: {str(exc)}"

    return None, last_error


def _extract_json_from_llm(text: str) -> Optional[Dict[str, Any]]:
    """Extract and parse JSON from LLM text output even if surrounded by markdown fences."""
    text_clean = text.strip()
    if text_clean.startswith("```"):
        text_clean = re.sub(r"^```[a-zA-Z]*\n?", "", text_clean)
        text_clean = re.sub(r"\n?```$", "", text_clean)
        text_clean = text_clean.strip()

    try:
        return json.loads(text_clean)
    except Exception:
        pass

    match = re.search(r"(\{.*\})", text_clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    return None


def _heuristic_context_fallback(
    review_text: str,
    movie_title: Optional[str] = None,
    failure_reason: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Deterministic rule-based and lexicon NLP engine.
    Extracts cinematic dimensions, tone, nuance, and contextual verdict offline.
    Guarantees 100% uptime with zero external dependencies.
    """
    lower_text = review_text.lower()
    sentences = [s.strip() for s in re.split(r"[.!?]+", review_text) if len(s.strip()) > 8]

    # 1. Lexicon sentiment counts
    pos_matches = [w for w in POSITIVE_CINEMA_WORDS if re.search(rf"\b{re.escape(w)}\b", lower_text)]
    neg_matches = [w for w in NEGATIVE_CINEMA_WORDS if re.search(rf"\b{re.escape(w)}\b", lower_text)]
    pos_score = len(pos_matches)
    neg_score = len(neg_matches)

    # 2. Aspect extraction
    extracted_aspects: List[Dict[str, str]] = []
    for aspect_name, keywords in ASPECT_PATTERNS.items():
        found_kw = [k for k in keywords if re.search(rf"\b{re.escape(k)}\b", lower_text)]
        if found_kw:
            matched_sentence = ""
            for sent in sentences:
                if any(k in sent.lower() for k in found_kw):
                    matched_sentence = sent
                    break

            aspect_pos = any(w in matched_sentence.lower() for w in POSITIVE_CINEMA_WORDS)
            aspect_neg = any(w in matched_sentence.lower() for w in NEGATIVE_CINEMA_WORDS)

            if aspect_pos and not aspect_neg:
                sentiment = "Positive"
                detail = f"High praise for {', '.join(found_kw[:2])} ({matched_sentence[:80]}...)" if matched_sentence else f"High praise for {found_kw[0]}."
            elif aspect_neg and not aspect_pos:
                sentiment = "Negative"
                detail = f"Criticism directed at {', '.join(found_kw[:2])} ({matched_sentence[:80]}...)" if matched_sentence else f"Criticism directed at {found_kw[0]}."
            elif aspect_pos and aspect_neg:
                sentiment = "Mixed"
                detail = f"Mixed feelings on {', '.join(found_kw[:2])}: {matched_sentence[:80]}..."
            else:
                sentiment = "Positive" if pos_score >= neg_score else "Negative"
                detail = f"Mentions {', '.join(found_kw[:2])} in context: \"{matched_sentence[:75]}...\"" if matched_sentence else f"Highlighted {found_kw[0]}."

            extracted_aspects.append({
                "aspect": aspect_name,
                "sentiment": sentiment,
                "detail": detail,
            })

    if not extracted_aspects:
        extracted_aspects.append({
            "aspect": "Overall Cinematic Experience",
            "sentiment": "Positive" if pos_score >= neg_score else "Negative",
            "detail": "Review focuses on general film reception and pacing.",
        })

    # 3. Tone analysis
    contrast_markers = ["however", "although", "despite", "but", "yet", "on the other hand", "while"]
    has_contrast = any(re.search(rf"\b{c}\b", lower_text) for c in contrast_markers)

    sarcasm_markers = ["supposedly", "so-called", "if you can call it", "waste of time", "laughable"]
    has_sarcasm = any(s in lower_text for s in sarcasm_markers)

    if has_sarcasm or (pos_score > 0 and "waste" in lower_text):
        tone = "Sarcastic & Caustic"
    elif has_contrast:
        tone = "Analytical & Nuanced"
    elif pos_score >= 3 and neg_score == 0:
        tone = "Rapturous & Acclaiming"
    elif neg_score >= 3 and pos_score == 0:
        tone = "Harsh & Scathing"
    elif pos_score > neg_score:
        tone = "Warm & Favorable"
    elif neg_score > pos_score:
        tone = "Critical & Dissatisfied"
    else:
        tone = "Measured & Balanced"

    # 4. Nuance & Subtext detection
    if has_sarcasm:
        nuance = "Potential irony or biting sarcasm detected regarding cinematic execution."
    elif has_contrast:
        nuance = "Reviewer articulates qualified sentiment; balanced strengths against noticeable shortcomings."
    elif pos_score > 0 and neg_score == 0:
        nuance = "Unconditional praise with high emotional resonance; no discernible reservations noted."
    elif neg_score > 0 and pos_score == 0:
        nuance = "Uncompromisingly critical stance with persistent negative sentiment across multiple elements."
    else:
        nuance = "Standard subjective impressions without extreme stylistic contrast."

    # 5. Contextual verdict
    if pos_score > neg_score + 1:
        verdict = "Enthusiastic Recommendation"
    elif pos_score > neg_score:
        verdict = "Favorable with Minor Reservations"
    elif neg_score > pos_score + 1:
        verdict = "Critical Pan / Avoid"
    elif neg_score > pos_score:
        verdict = "Unfavorable Overall"
    else:
        verdict = "Mixed / Polarized Reception"

    # 6. Concise Summary
    target_name = f"'{movie_title}'" if movie_title else "the film"
    if pos_score > neg_score:
        summary = f"The reviewer expresses predominantly favorable reactions toward {target_name}, commending its creative execution."
    elif neg_score > pos_score:
        summary = f"The reviewer delivers a critical assessment of {target_name}, citing notable issues in pacing, writing, or performance."
    else:
        summary = f"The reviewer provides a balanced perspective on {target_name}, weighing distinct strengths against clear limitations."

    fallback_reason_text = failure_reason or "OpenRouter API unavailable / rate limited"

    return {
        "summary": summary,
        "aspects": extracted_aspects[:4],
        "tone": tone,
        "nuance": nuance,
        "verdict": verdict,
        "engine": "Deterministic Local NLP Engine (Offline Fallback)",
        "is_fallback": True,
        "status_message": f"Fallback active: {fallback_reason_text}",
    }

