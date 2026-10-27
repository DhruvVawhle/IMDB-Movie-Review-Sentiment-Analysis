"""
Region Classification Service for CineSense.
Classifies movies into Indian, Hollywood, or International based on full TMDB details,
never based on the list/market the film appeared in.
"""

from typing import Any, Dict, List, Optional

INDIAN_LANGUAGES = {
    "hi",  # Hindi
    "ta",  # Tamil
    "te",  # Telugu
    "ml",  # Malayalam
    "kn",  # Kannada
    "bn",  # Bengali
    "mr",  # Marathi
    "pa",  # Punjabi
    "gu",  # Gujarati
    "or",  # Odia
    "ur",  # Urdu
}


def _extract_country_list(field: Any) -> List[str]:
    """Extract list of uppercase ISO 3166-1 alpha-2 country codes from string, list of strings, or list of dicts."""
    codes: List[str] = []
    if not field:
        return codes
    if isinstance(field, str):
        c = field.strip().upper()
        if c:
            codes.append(c)
        return codes
    if isinstance(field, list):
        for item in field:
            if isinstance(item, str):
                c = item.strip().upper()
                if c:
                    codes.append(c)
            elif isinstance(item, dict):
                c = (item.get("iso_3166_1") or item.get("code") or item.get("id") or "").strip().upper()
                if c:
                    codes.append(c)
    return codes


def classify_origin(movie_details: Optional[Dict[str, Any]]) -> str:
    """
    Classify the origin of a movie as 'Indian', 'Hollywood', 'International', or 'Unclassified'.
    Uses the full movie details (/movie/{id}), not the list item.

    Order of evaluation:
    a. Indian if origin_country contains "IN", or original_language is one of
       {hi, ta, te, ml, kn, bn, mr, pa, gu, or, ur} AND production_countries includes IN.
    b. Hollywood if origin_country contains "US" and original_language is "en".
    c. Co-productions matching both a and b: use first entry in origin_country.
       If origin_country is empty, use first production_countries entry.
    d. Everything else is "International".
    e. If details are missing or the call fails, label it "Unclassified". Never guess.
    """
    if not movie_details or not isinstance(movie_details, dict):
        return "Unclassified"

    origin_countries = _extract_country_list(movie_details.get("origin_country"))
    prod_countries = _extract_country_list(movie_details.get("production_countries"))
    orig_lang = str(movie_details.get("original_language") or "").strip().lower()

    # If details are completely empty or missing origin, production, and language info
    if not origin_countries and not prod_countries and not orig_lang:
        return "Unclassified"

    # a. Indian condition
    is_indian = ("IN" in origin_countries) or (
        orig_lang in INDIAN_LANGUAGES and "IN" in prod_countries
    )

    # b. Hollywood condition
    is_hollywood = ("US" in origin_countries) and (orig_lang == "en")

    # c. Co-productions that match both a and b
    if is_indian and is_hollywood:
        if origin_countries:
            first_entry = origin_countries[0]
        elif prod_countries:
            first_entry = prod_countries[0]
        else:
            first_entry = ""

        if first_entry == "IN":
            return "Indian"
        elif first_entry == "US":
            return "Hollywood"
        else:
            return "International"

    if is_indian:
        return "Indian"

    if is_hollywood:
        return "Hollywood"

    # d. Everything else
    return "International"


def get_origin_reason(
    movie_details: Optional[Dict[str, Any]], origin_label: Optional[str] = None
) -> str:
    """
    Generate an explanatory string for the badge title attribute.
    Example: 'Indian: origin country IN, language hi'
    """
    if not movie_details or not isinstance(movie_details, dict):
        return "Unclassified: details unavailable"

    if origin_label is None:
        origin_label = classify_origin(movie_details)

    origin_countries = _extract_country_list(movie_details.get("origin_country"))
    orig_lang = str(movie_details.get("original_language") or "").strip().lower() or "unknown"
    origin_str = ", ".join(origin_countries) if origin_countries else "none"

    if origin_label == "Indian":
        return f"Indian: origin country {origin_str}, language {orig_lang}"
    elif origin_label == "Hollywood":
        return f"Hollywood: origin country {origin_str}, language {orig_lang}"
    elif origin_label == "International":
        return f"International: origin country {origin_str}, language {orig_lang}"
    else:
        return "Unclassified: details unavailable"

