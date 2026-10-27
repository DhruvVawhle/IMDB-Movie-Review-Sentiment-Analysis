"""
Canonical text preprocessing pipeline for CineSense.
Preserves exact compatibility with the original research notebook methodology.
"""

import re
import html
from typing import Dict, List, Optional, Tuple

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Ensure NLTK resources are available
_STOPWORDS_SET: Optional[set] = None
_LEMMATIZER: Optional[WordNetLemmatizer] = None
_STEMMER: Optional[PorterStemmer] = None


def _init_nltk_resources() -> Tuple[set, WordNetLemmatizer, PorterStemmer]:
    global _STOPWORDS_SET, _LEMMATIZER, _STEMMER
    if _STOPWORDS_SET is None or _LEMMATIZER is None or _STEMMER is None:
        try:
            sw = set(stopwords.words("english"))
        except LookupError:
            nltk.download("stopwords", quiet=True)
            sw = set(stopwords.words("english"))
        
        try:
            _LEMMATIZER = WordNetLemmatizer()
            _LEMMATIZER.lemmatize("films")
        except LookupError:
            nltk.download("wordnet", quiet=True)
            _LEMMATIZER = WordNetLemmatizer()
            
        try:
            word_tokenize("test text")
        except LookupError:
            nltk.download("punkt", quiet=True)
            nltk.download("punkt_tab", quiet=True)

        _STEMMER = PorterStemmer()
        _STOPWORDS_SET = sw
        
    return _STOPWORDS_SET, _LEMMATIZER, _STEMMER


def clean_html_and_urls(text: str) -> str:
    """Strip HTML tags, decode entities, and remove web URLs."""
    if not isinstance(text, str):
        return ""
    text = html.unescape(text)
    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    return text


def normalize_text(text: str) -> str:
    """Lowercase text and strip all non-alphabetic characters."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_text(text: str) -> List[str]:
    """Tokenize normalized text using NLTK word_tokenize with regex fallback."""
    if not text:
        return []
    try:
        return word_tokenize(text)
    except Exception:
        return re.findall(r"\b[a-z]+\b", text)


def filter_tokens(tokens: List[str], stop_words: Optional[set] = None) -> List[str]:
    """Filter out stopwords and short tokens (len <= 2)."""
    if stop_words is None:
        stop_words, _, _ = _init_nltk_resources()
    return [t for t in tokens if t not in stop_words and len(t) > 2]


def apply_lemmatization(tokens: List[str]) -> List[str]:
    """Apply WordNet lemmatization to a list of tokens."""
    _, lemmatizer, _ = _init_nltk_resources()
    return [lemmatizer.lemmatize(t) for t in tokens]


def apply_stemming(tokens: List[str]) -> List[str]:
    """Apply Porter stemming to a list of tokens."""
    _, _, stemmer = _init_nltk_resources()
    return [stemmer.stem(t) for t in tokens]


def preprocess_text(text: str, use_lemma: bool = True) -> str:
    """
    Canonical preprocessing pipeline:
    1. Strip HTML and URLs
    2. Lowercase and remove non-alphabetic chars
    3. Tokenize
    4. Remove stopwords and tokens with len <= 2
    5. Lemmatize (or stem)
    6. Join into normalized space-delimited string
    """
    if not isinstance(text, str) or not text.strip():
        return ""
    
    stop_words, lemmatizer, stemmer = _init_nltk_resources()
    
    cleaned = clean_html_and_urls(text)
    normalized = normalize_text(cleaned)
    tokens = tokenize_text(normalized)
    filtered = [t for t in tokens if t not in stop_words and len(t) > 2]
    
    if use_lemma:
        processed = [lemmatizer.lemmatize(t) for t in filtered]
    else:
        processed = [stemmer.stem(t) for t in filtered]
        
    return " ".join(processed)


def get_pipeline_breakdown(text: str) -> Dict[str, str]:
    """
    Produce a step-by-step audit of the text transformation for the NLP insights page.
    """
    original = str(text) if text else ""
    step1_clean = clean_html_and_urls(original)
    step2_normalized = normalize_text(step1_clean)
    step3_tokens = tokenize_text(step2_normalized)
    
    stop_words, lemmatizer, stemmer = _init_nltk_resources()
    step4_filtered = [t for t in step3_tokens if t not in stop_words and len(t) > 2]
    step5_lemmatized = [lemmatizer.lemmatize(t) for t in step4_filtered]
    step5_stemmed = [stemmer.stem(t) for t in step4_filtered]
    
    return {
        "original": original,
        "html_and_url_cleaned": step1_clean,
        "normalized": step2_normalized,
        "token_count_raw": len(step3_tokens),
        "raw_tokens_sample": step3_tokens[:20],
        "filtered_tokens_sample": step4_filtered[:20],
        "filtered_count": len(step4_filtered),
        "lemmatized_text": " ".join(step5_lemmatized),
        "stemmed_text": " ".join(step5_stemmed),
    }

