"""
Unit tests for ui.region classify_origin.
Validates the classification rules across Indian, Hollywood, International, and Unclassified films.
"""

import pytest
from ui.region import classify_origin, get_origin_reason


def test_hindi_film():
    """A Hindi film (origin_country IN, language hi) should be classified as Indian."""
    details = {
        "title": "Jawan",
        "origin_country": ["IN"],
        "original_language": "hi",
        "production_countries": [{"iso_3166_1": "IN", "name": "India"}],
    }
    assert classify_origin(details) == "Indian"
    reason = get_origin_reason(details)
    assert "Indian:" in reason
    assert "IN" in reason
    assert "hi" in reason


def test_tamil_film():
    """A Tamil film (origin_country IN, language ta) should be classified as Indian."""
    details = {
        "title": "Leo",
        "origin_country": ["IN"],
        "original_language": "ta",
        "production_countries": [{"iso_3166_1": "IN", "name": "India"}],
    }
    assert classify_origin(details) == "Indian"

    # Also test when origin_country is empty but language is ta and production_countries has IN
    details_no_origin = {
        "title": "Leo",
        "origin_country": [],
        "original_language": "ta",
        "production_countries": [{"iso_3166_1": "IN", "name": "India"}],
    }
    assert classify_origin(details_no_origin) == "Indian"


def test_english_language_indian_film():
    """An English-language Indian film (origin_country IN, language en) should be classified as Indian."""
    details = {
        "title": "The White Tiger",
        "origin_country": ["IN"],
        "original_language": "en",
        "production_countries": [{"iso_3166_1": "IN", "name": "India"}],
    }
    assert classify_origin(details) == "Indian"


def test_us_english_film_playing_in_india():
    """A US English film playing in Indian theatres should be classified as Hollywood, never Indian."""
    details = {
        "title": "Dune: Part Two",
        "origin_country": ["US"],
        "original_language": "en",
        "production_countries": [{"iso_3166_1": "US", "name": "United States of America"}],
    }
    assert classify_origin(details) == "Hollywood"
    reason = get_origin_reason(details)
    assert "Hollywood:" in reason
    assert "US" in reason
    assert "en" in reason


def test_uk_film():
    """A UK film (origin_country GB, language en) should be classified as International."""
    details = {
        "title": "Paddington",
        "origin_country": ["GB"],
        "original_language": "en",
        "production_countries": [{"iso_3166_1": "GB", "name": "United Kingdom"}],
    }
    assert classify_origin(details) == "International"


def test_korean_film():
    """A Korean film (origin_country KR, language ko) should be classified as International."""
    details = {
        "title": "Parasite",
        "origin_country": ["KR"],
        "original_language": "ko",
        "production_countries": [{"iso_3166_1": "KR", "name": "South Korea"}],
    }
    assert classify_origin(details) == "International"


def test_india_us_coproduction():
    """An India-US co-production matching both conditions should follow origin_country ordering."""
    # Lead country India
    details_in_lead = {
        "title": "The Namesake",
        "origin_country": ["IN", "US"],
        "original_language": "en",
        "production_countries": [
            {"iso_3166_1": "IN", "name": "India"},
            {"iso_3166_1": "US", "name": "United States of America"},
        ],
    }
    assert classify_origin(details_in_lead) == "Indian"

    # Lead country US
    details_us_lead = {
        "title": "Monkey Man",
        "origin_country": ["US", "IN"],
        "original_language": "en",
        "production_countries": [
            {"iso_3166_1": "US", "name": "United States of America"},
            {"iso_3166_1": "IN", "name": "India"},
        ],
    }
    assert classify_origin(details_us_lead) == "Hollywood"

    # Co-production with empty origin_country falls back to first production_country
    details_fallback = {
        "title": "Co-pro",
        "origin_country": [],
        "original_language": "hi",
        "production_countries": [
            {"iso_3166_1": "IN", "name": "India"},
            {"iso_3166_1": "US", "name": "United States"},
        ],
    }
    assert classify_origin(details_fallback) == "Indian"


def test_missing_details():
    """A film with missing details or None should return Unclassified."""
    assert classify_origin(None) == "Unclassified"
    assert classify_origin({}) == "Unclassified"
    assert classify_origin({"id": 123}) == "Unclassified"
    reason = get_origin_reason({})
    assert "Unclassified:" in reason

