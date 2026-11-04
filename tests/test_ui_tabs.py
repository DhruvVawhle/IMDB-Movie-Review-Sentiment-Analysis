"""
Integration tests for Streamlit UI tabs.
Ensures every tab renders without uncaught exceptions.
"""

import os
import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app.py"))

MOCK_MOVIES = [
    {
        "id": 27205,
        "title": "Inception",
        "release_year": "2010",
        "audience_score": 8.4,
        "poster_url": "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
        "overview": "A thief who steals corporate secrets through the use of dream-sharing technology.",
        "genres": ["Action", "Sci-Fi"],
        "origin_badge": "Hollywood",
        "origin_badge_title": "Hollywood release",
        "formatted_date": "16 Jul 2010",
    }
]


@pytest.fixture(autouse=True)
def mock_tmdb_calls(monkeypatch):
    """Mock external TMDB network requests to avoid remote connection resets and timeouts."""
    import services.tmdb_service as tmdb_mod
    monkeypatch.setattr(tmdb_mod, "get_movies_by_category_and_region", lambda *args, **kwargs: MOCK_MOVIES)
    monkeypatch.setattr(tmdb_mod, "search_tmdb_movies", lambda *args, **kwargs: MOCK_MOVIES)


@pytest.mark.parametrize("tab_name", [
    "Overview",
    "Analyze a review",
    "Movies",
    "Dataset",
    "Model benchmarks",
    "NLP pipeline",
])
def test_tab_renders_without_exceptions(tab_name):
    at = AppTest.from_file(APP_PATH, default_timeout=60)
    at.query_params["tab"] = tab_name
    at.run()
    assert not at.exception, f"Tab '{tab_name}' raised an exception: {at.exception}"


def test_normalize_and_classify_movie_preserves_latest_theatrical_date():
    from services.tmdb_service import normalize_and_classify_movie
    # Raw item has theatrical release date Oct 23, details has older festival premiere Jul 15
    raw_item = {
        "id": 1058424,
        "title": "Hope",
        "release_date": "2026-10-23",
        "vote_average": 6.8,
        "overview": "Story of hope.",
    }
    details = {
        "id": 1058424,
        "title": "Hope",
        "release_date": "2026-07-15",
        "vote_average": 6.8,
        "production_countries": [{"iso_3166_1": "KR"}],
    }
    normalized = normalize_and_classify_movie(raw_item, details=details)
    assert normalized["release_date"] == "2026-10-23"
    assert normalized["formatted_date"] == "Oct 23, 2026"



