"""
TMDB API Service for CineSense.
Fetches, caches (1-hour TTL), and normalizes live theatrical releases and upcoming titles.
Origins are classified using full movie details (/movie/{id}) via ui.region.classify_origin,
never inferred from the theatrical region list.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import os
from typing import Any, Dict, List, Optional
import requests
from requests.adapters import HTTPAdapter
import streamlit as st
from urllib3.util.retry import Retry

from ui.region import classify_origin, get_origin_reason

# TMDB Genre ID to Name Mapping
TMDB_GENRES = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science Fiction",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western",
}

_SESSION: Optional[requests.Session] = None


def get_tmdb_session() -> requests.Session:
    """Return a configured requests.Session with connection retries and standard headers."""
    global _SESSION
    if _SESSION is not None:
        return _SESSION

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }

    session.headers.update(headers)
    _SESSION = session
    return session


def get_tmdb_api_key() -> Optional[str]:
    """Retrieve TMDB API key safely from st.secrets['TMDB_API_KEY']. Never hardcode it."""
    try:
        if hasattr(st, "secrets") and "TMDB_API_KEY" in st.secrets:
            key = str(st.secrets["TMDB_API_KEY"]).strip()
            if key and not key.startswith("your_"):
                return key
    except Exception:
        pass

    # Secondary check in os.environ for non-Streamlit test contexts
    env_key = os.environ.get("TMDB_API_KEY", "").strip()
    if env_key and not env_key.startswith("your_"):
        return env_key

    return None


def format_release_date(date_str: Optional[str]) -> str:
    """Format 'YYYY-MM-DD' into human-friendly 'MMM DD, YYYY'."""
    if not date_str:
        return "Coming Soon"
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%b %d, %Y")
    except Exception:
        return date_str


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_movie_details(movie_id: int, api_key: str) -> Optional[Dict[str, Any]]:
    """
    Fetch full movie details (/movie/{id}) from TMDB.
    Cached for 1 hour with a strict 5-second timeout.
    """
    if not api_key or not movie_id:
        return None

    session = get_tmdb_session()
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        "api_key": api_key,
        "language": "en-US",
    }
    try:
        resp = session.get(url, params=params, timeout=5.0)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_tmdb_movies_raw(category: str, region: str, api_key: str, page: int = 1) -> List[Dict[str, Any]]:
    """
    Fetch raw movie list from TMDB for a category ('now_playing', 'upcoming') and region.
    Cached for 30 minutes with a strict 5-second timeout.
    """
    if not api_key:
        return []

    session = get_tmdb_session()
    url = f"https://api.themoviedb.org/3/movie/{category}"
    params = {
        "api_key": api_key,
        "region": region,
        "language": "en-US",
        "page": page,
    }
    try:
        resp = session.get(url, params=params, timeout=5.0)
        if resp.status_code == 200:
            return resp.json().get("results", [])
    except Exception:
        pass
    return []


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_indian_upcoming_discover(api_key: str) -> List[Dict[str, Any]]:
    """
    Query /discover/movie with with_origin_country=IN and primary_release_date in next 60 days,
    sorted by popularity, ensuring Indian upcoming row is never empty when region=IN upcoming is thin.
    Cached for 1 hour with a strict 5-second timeout.
    """
    if not api_key:
        return []

    session = get_tmdb_session()
    url = "https://api.themoviedb.org/3/discover/movie"
    today = datetime.now().date()
    end_date = today + timedelta(days=60)

    params = {
        "api_key": api_key,
        "with_origin_country": "IN",
        "primary_release_date.gte": today.isoformat(),
        "primary_release_date.lte": end_date.isoformat(),
        "sort_by": "popularity.desc",
        "page": 1,
    }
    try:
        resp = session.get(url, params=params, timeout=5.0)
        if resp.status_code == 200:
            return resp.json().get("results", [])
    except Exception:
        pass
    return []


@st.cache_data(ttl=3600, show_spinner=False)
def search_tmdb_movies(query: str, api_key: str) -> List[Dict[str, Any]]:
    """
    Search TMDB movies (/search/movie).
    Cached for 1 hour with a strict 5-second timeout.
    """
    if not api_key or not query.strip():
        return []

    session = get_tmdb_session()
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": api_key,
        "query": query.strip(),
        "include_adult": False,
        "language": "en-US",
        "page": 1,
    }
    try:
        resp = session.get(url, params=params, timeout=5.0)
        if resp.status_code == 200:
            return resp.json().get("results", [])
    except Exception:
        pass
    return []


def normalize_and_classify_movie(
    item: Dict[str, Any], details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Normalize raw TMDB movie data and apply origin classification.
    Uses full movie details (/movie/{id}) when available, not list location.
    Retains the most recent dated theatrical release date.
    Never attaches TMDB review text.
    """
    data = details if details else item
    poster_path = data.get("poster_path") or item.get("poster_path")
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""

    # Always keep the most recent dated release between raw theatrical listing and details
    raw_date = item.get("release_date") or ""
    details_date = (details.get("release_date") if details else "") or ""
    if raw_date and details_date:
        release_date = max(raw_date, details_date)
    else:
        release_date = raw_date or details_date or ""

    release_year = release_date[:4] if release_date else "N/A"

    # Resolve genres
    if details and "genres" in details and details["genres"]:
        genres = [
            g.get("name")
            for g in details["genres"]
            if isinstance(g, dict) and g.get("name")
        ]
    elif "genre_ids" in item:
        genres = [TMDB_GENRES.get(gid, "Film") for gid in item.get("genre_ids", [])]
    else:
        genres = ["Film"]

    title = data.get("title") or item.get("title") or "Untitled"
    movie_id = data.get("id") or item.get("id")
    raw_vote = data.get("vote_average") if data.get("vote_average") is not None else item.get("vote_average", 0.0)
    audience_score = round(float(raw_vote), 1)
    overview = data.get("overview") or item.get("overview") or "No plot summary available from TMDB."

    # Origin classification & reason
    origin_label = classify_origin(details) if details else classify_origin(item)
    origin_reason = get_origin_reason(details if details else item, origin_label=origin_label)

    return {
        "id": movie_id,
        "title": title,
        "release_date": release_date,
        "formatted_date": format_release_date(release_date),
        "release_year": release_year,
        "genres": genres or ["Film"],
        "audience_score": audience_score,
        "overview": overview,
        "poster_url": poster_url,
        "origin_label": origin_label,
        "origin_reason": origin_reason,
        "origin_badge": origin_label,
        "origin_badge_title": origin_reason,
    }


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_all_classified_movies_for_category(category: str) -> List[Dict[str, Any]]:
    """
    Fetch and classify all raw movies for a given category ('now_playing' or 'upcoming').
    Deduplicates across US, IN, and discover queries and runs concurrent details classification.
    Orders 'now_playing' strictly by latest dated release (descending) so newest theatrical films appear first.
    Cached for 30 minutes so region filtering in the UI is instantaneous.
    """
    api_key = get_tmdb_api_key()
    if not api_key:
        return []

    # 1. Fetch raw candidates (fetching up to 2 pages for now_playing to ensure deep, up-to-date coverage)
    us_raw_p1 = fetch_tmdb_movies_raw(category, "US", api_key, page=1)
    us_raw_p2 = fetch_tmdb_movies_raw(category, "US", api_key, page=2) if category == "now_playing" else []
    in_raw_p1 = fetch_tmdb_movies_raw(category, "IN", api_key, page=1)
    in_raw_p2 = fetch_tmdb_movies_raw(category, "IN", api_key, page=2) if category == "now_playing" else []
    discover_raw = fetch_indian_upcoming_discover(api_key) if category == "upcoming" else []

    # 2. Deduplicate raw movies by TMDB ID, retaining the latest theatrical release date across regional entries
    all_raw: List[Dict[str, Any]] = []
    seen_movies: Dict[int, Dict[str, Any]] = {}

    for movie in in_raw_p1 + in_raw_p2 + us_raw_p1 + us_raw_p2 + discover_raw:
        m_id = movie.get("id")
        if not m_id:
            continue
        if m_id not in seen_movies:
            movie_copy = dict(movie)
            seen_movies[m_id] = movie_copy
            all_raw.append(movie_copy)
        else:
            existing_date = seen_movies[m_id].get("release_date") or ""
            candidate_date = movie.get("release_date") or ""
            if candidate_date > existing_date:
                seen_movies[m_id]["release_date"] = candidate_date

    if not all_raw:
        return []

    # 3. Fetch full details for classification (concurrently across worker pool)
    classified_movies: List[Dict[str, Any]] = []

    def _fetch_and_normalize(item: Dict[str, Any]) -> Dict[str, Any]:
        m_id = item.get("id")
        details = fetch_movie_details(m_id, api_key) if m_id else None
        return normalize_and_classify_movie(item, details=details)

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_map = {executor.submit(_fetch_and_normalize, item): item for item in all_raw}
        for future in as_completed(future_map):
            try:
                classified_movies.append(future.result())
            except Exception:
                item = future_map[future]
                classified_movies.append(normalize_and_classify_movie(item, details=None))

    # 4. Sort and filter movies based on category requirement:
    today_iso = datetime.now().date().isoformat()
    cutoff_past_iso = (datetime.now().date() - timedelta(days=60)).isoformat()

    if category == "now_playing":
        # Keep only contemporary theatrical releases within the current window
        classified_movies = [m for m in classified_movies if (m.get("release_date") or "") >= cutoff_past_iso]

        # Strictly sort by latest release date descending so newest theatrical titles appear first
        def _now_playing_sort_key(m: Dict[str, Any]):
            r_date = m.get("release_date") or "0000-00-00"
            score = float(m.get("audience_score", 0.0) or 0.0)
            return (r_date, score)

        classified_movies.sort(key=_now_playing_sort_key, reverse=True)
    elif category == "upcoming":
        # Keep only truly upcoming titles (release date today or future)
        classified_movies = [m for m in classified_movies if (m.get("release_date") or "") >= today_iso]

        # Sort upcoming titles by chronological release date (soonest premiere first)
        def _upcoming_sort_key(m: Dict[str, Any]):
            r_date = m.get("release_date") or "9999-99-99"
            score = float(m.get("audience_score", 0.0) or 0.0)
            return (r_date, -score)

        classified_movies.sort(key=_upcoming_sort_key)
    else:
        # Keep stable order matching source list
        id_order = {item["id"]: idx for idx, item in enumerate(all_raw)}
        classified_movies.sort(key=lambda m: id_order.get(m["id"], 999999))

    return classified_movies


@st.cache_data(ttl=1800, show_spinner=False)
def get_movies_by_category_and_region(
    category: str,
    region_filter: str,
) -> List[Dict[str, Any]]:
    """
    Retrieve, classify, and filter movies for 'now_playing' or 'upcoming'.
    Uses cached movie collection to make region switching instant.
    - Filters by classify_origin label ONLY:
      * 'Hollywood' -> origin_label == 'Hollywood'
      * 'Indian' -> origin_label == 'Indian'
      * 'All' -> shows all films (including 'International' and 'Unclassified').
    """
    classified_movies = fetch_all_classified_movies_for_category(category)

    # Filter strictly by classify_origin
    if region_filter == "Hollywood":
        return [m for m in classified_movies if m.get("origin_label") == "Hollywood"]
    elif region_filter == "Indian":
        return [m for m in classified_movies if m.get("origin_label") == "Indian"]
    else:  # "All"
        return classified_movies
