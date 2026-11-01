"""
Review Storage Service for CineSense.
Provides persistent storage, querying, and statistics for movie reviews in Letterboxd format.
Reviews are saved persistently in data/community_reviews.json.
"""

from datetime import datetime
import json
import os
import threading
from typing import Any, Dict, List, Optional
import uuid

# Base path for storing reviews
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
REVIEWS_FILE = os.path.join(DATA_DIR, "community_reviews.json")
WATCHED_FILE = os.path.join(DATA_DIR, "user_watched_movies.json")

_LOCK = threading.RLock()

# Initial Seed Data for Watched Diary (dynamically editable and persisted)
INITIAL_SEED_WATCHED: List[Dict[str, Any]] = [
    {
        "movie_id": 27205,
        "title": "Inception",
        "year": "2010",
        "poster_url": "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
        "watched_at": "2026-10-25T19:42:00",
        "formatted_date": "25 Oct 2026",
        "is_liked": True,
        "rating": 5.0,
        "watch_count": 1,
    },
    {
        "movie_id": 155,
        "title": "The Dark Knight",
        "year": "2008",
        "poster_url": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "watched_at": "2026-10-24T21:10:00",
        "formatted_date": "24 Oct 2026",
        "is_liked": True,
        "rating": 5.0,
        "watch_count": 2,
    },
]

# Curated avatar background palettes for Letterboxd user monograms
AVATAR_PALETTES = [
    {"bg": "#1A4B5C", "fg": "#8BE9FD"},
    {"bg": "#3B2654", "fg": "#FF79C6"},
    {"bg": "#1B4D3E", "fg": "#50FA7B"},
    {"bg": "#5C3A21", "fg": "#FFB86C"},
    {"bg": "#4A1525", "fg": "#FF5555"},
    {"bg": "#22314E", "fg": "#BD93F9"},
]

# Initial Seed Data with high-craft Letterboxd-style reviews for iconic benchmark films, latest releases & old classics
INITIAL_SEED_REVIEWS: List[Dict[str, Any]] = [
    {
        "id": "rev_seed_dune2_01",
        "movie_id": 693134,
        "movie_title": "Dune: Part Two",
        "movie_year": "2024",
        "movie_poster": "https://image.tmdb.org/t/p/w500/6izwz7rsy95ARzTR3poZ8H6c5pp.jpg",
        "author_name": "Devon Scott",
        "author_handle": "@devoncinema",
        "avatar_color": "#5C3A21",
        "avatar_fg": "#FFB86C",
        "rating": 5.0,
        "is_liked": True,
        "contains_spoilers": False,
        "review_text": (
            "A desert leviathan of scale and apocalyptic dread. Greig Fraser’s cinematography turns Arrakis into an elemental myth "
            "where every sandworm crest feels titanic. Timothée Chalamet’s descent from reluctant messiah into terrifying religious fanatic "
            "is chillingly earned. Blockbuster sci-fi operating at its absolute zenith."
        ),
        "sentiment_label": "POSITIVE",
        "sentiment_confidence": 99.2,
        "model_used": "Logistic Regression",
        "created_at": "2026-10-31T21:30:00",
        "formatted_date": "31 Oct 2026",
        "likes_count": 76,
    },
    {
        "id": "rev_seed_godfather_01",
        "movie_id": 238,
        "movie_title": "The Godfather",
        "movie_year": "1972",
        "movie_poster": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
        "author_name": "Vincent Corle",
        "author_handle": "@vincent_screen",
        "avatar_color": "#4A1525",
        "avatar_fg": "#FF5555",
        "rating": 5.0,
        "is_liked": True,
        "contains_spoilers": False,
        "review_text": (
            "The apex of American cinematic tragedy. Gordon Willis sculpts shadowy, amber-lit interiors where family devotion and moral "
            "corruption entwine irreversibly. Al Pacino’s chilling metamorphosis from decorated war hero to icy mafia don remains the "
            "gold standard of character evolution. Every shot is painted with classical permanence."
        ),
        "sentiment_label": "POSITIVE",
        "sentiment_confidence": 99.5,
        "model_used": "Logistic Regression",
        "created_at": "2026-10-30T22:00:00",
        "formatted_date": "30 Oct 2026",
        "likes_count": 92,
    },
    {
        "id": "rev_seed_oppenheimer_01",
        "movie_id": 872585,
        "movie_title": "Oppenheimer",
        "movie_year": "2023",
        "movie_poster": "https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
        "author_name": "Callum Wright",
        "author_handle": "@wrightonfilm",
        "avatar_color": "#1A4B5C",
        "avatar_fg": "#8BE9FD",
        "rating": 5.0,
        "is_liked": True,
        "contains_spoilers": False,
        "review_text": (
            "A kinetic chamber tragedy disguised as a historical epic. Christopher Nolan constructs three hours of pure auditory and moral "
            "propulsion. The Trinity test holds your breath in suffocating total silence before the concussive roar tears through the room. "
            "Cillian Murphy's thousand-yard stare carries the weight of a transformed universe."
        ),
        "sentiment_label": "POSITIVE",
        "sentiment_confidence": 98.7,
        "model_used": "BiLSTM Neural Network",
        "created_at": "2026-10-29T16:45:00",
        "formatted_date": "29 Oct 2026",
        "likes_count": 64,
    },
    {
        "id": "rev_seed_12angrymen_01",
        "movie_id": 389,
        "movie_title": "12 Angry Men",
        "movie_year": "1957",
        "movie_poster": "https://image.tmdb.org/t/p/w500/zhG3vKWyDRaZYoaww1UVAi29T9h.jpg",
        "author_name": "Arthur Pendelton",
        "author_handle": "@arthur_classic",
        "avatar_color": "#22314E",
        "avatar_fg": "#BD93F9",
        "rating": 5.0,
        "is_liked": True,
        "contains_spoilers": False,
        "review_text": (
            "A masterclass in spatial tension and dramatic economy. Twelve men in one sweltering jury room dissecting the anatomy of "
            "reasonable doubt. Boris Kaufman’s slowly compressing focal lengths create an unbearable sense of psychological claustrophobia. "
            "Henry Fonda’s quiet moral conviction still cuts like a razor across seven decades."
        ),
        "sentiment_label": "POSITIVE",
        "sentiment_confidence": 98.9,
        "model_used": "Naive Bayes",
        "created_at": "2026-10-28T18:25:00",
        "formatted_date": "28 Oct 2026",
        "likes_count": 53,
    },
    {
        "id": "rev_seed_pastlives_01",
        "movie_id": 666277,
        "movie_title": "Past Lives",
        "movie_year": "2023",
        "movie_poster": "https://image.tmdb.org/t/p/w500/k3waqVXSnvCZWfJYNtdamTgTtTA.jpg",
        "author_name": "Hana Kim",
        "author_handle": "@hanareels",
        "avatar_color": "#3B2654",
        "avatar_fg": "#FF79C6",
        "rating": 4.5,
        "is_liked": True,
        "contains_spoilers": False,
        "review_text": (
            "The quietest devastation of modern romance. Celine Song treats In-Yun not as a whimsical trope, but as an aching eulogy "
            "for the alternate lives we abandon at border crossings. Greta Lee and Teo Yoo communicate entire unwritten decades "
            "through glances across a subway car. That final silent walk to the Uber is utterly shattering."
        ),
        "sentiment_label": "POSITIVE",
        "sentiment_confidence": 96.8,
        "model_used": "Logistic Regression",
        "created_at": "2026-10-27T19:10:00",
        "formatted_date": "27 Oct 2026",
        "likes_count": 48,
    },
    {
        "id": "rev_seed_pulpfiction_01",
        "movie_id": 680,
        "movie_title": "Pulp Fiction",
        "movie_year": "1994",
        "movie_poster": "https://image.tmdb.org/t/p/w500/vQWk5YBFWF4bZaofAbv0tShwBvQ.jpg",
        "author_name": "Zoe Cassavetes",
        "author_handle": "@zoe_cinema",
        "avatar_color": "#1B4D3E",
        "avatar_fg": "#50FA7B",
        "rating": 5.0,
        "is_liked": True,
        "contains_spoilers": False,
        "review_text": (
            "The seismic earthquake that reshaped modern independent cinema. Nonlinear storytelling turned into a dazzling jazz riff "
            "of diner theology, sharp conversational rhythm, and needle drops that immediately etched into pop culture. Travolta and "
            "Samuel L. Jackson possess a kinetic chemistry that will never get old."
        ),
        "sentiment_label": "POSITIVE",
        "sentiment_confidence": 97.4,
        "model_used": "BiLSTM Neural Network",
        "created_at": "2026-10-26T15:30:00",
        "formatted_date": "26 Oct 2026",
        "likes_count": 68,
    },
    {
        "id": "rev_seed_taxidriver_01",
        "movie_id": 103,
        "movie_title": "Taxi Driver",
        "movie_year": "1976",
        "movie_poster": "https://image.tmdb.org/t/p/w500/ekstpH614fwDX8DUln1a2Opz0N8.jpg",
        "author_name": "Damon Price",
        "author_handle": "@damonp_films",
        "avatar_color": "#4A1525",
        "avatar_fg": "#FF5555",
        "rating": 4.5,
        "is_liked": True,
        "contains_spoilers": False,
        "review_text": (
            "A neon-drenched descent into urban alienation and simmering psychological decay. Robert De Niro’s Travis Bickle is the "
            "ultimate lonely observer, drifting through nocturnal steam and grit. Paul Schrader’s searing script and Bernard Herrmann’s "
            "mournful jazz score create a timeless, haunting portrait of detachment."
        ),
        "sentiment_label": "POSITIVE",
        "sentiment_confidence": 94.2,
        "model_used": "Logistic Regression",
        "created_at": "2026-10-25T23:15:00",
        "formatted_date": "25 Oct 2026",
        "likes_count": 45,
    },
    {
        "id": "rev_seed_darkknight_01",
        "movie_id": 155,
        "movie_title": "The Dark Knight",
        "movie_year": "2008",
        "movie_poster": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "author_name": "Marcus Vance",
        "author_handle": "@marcusonfilm",
        "avatar_color": "#1B4D3E",
        "avatar_fg": "#50FA7B",
        "rating": 5.0,
        "is_liked": True,
        "contains_spoilers": False,
        "review_text": (
            "Heath Ledger did not simply play the Joker; he manifested a walking philosophical rupture. Michael Mann-esque urban grit "
            "meets Shakespearean moral tragedy. Every scene feels charged with genuine stakes and ideological tension that superhero "
            "movies still haven't managed to replicate."
        ),
        "sentiment_label": "POSITIVE",
        "sentiment_confidence": 99.1,
        "model_used": "Logistic Regression",
        "created_at": "2026-10-24T21:10:00",
        "formatted_date": "24 Oct 2026",
        "likes_count": 58,
    },
    {
        "id": "rev_seed_inception_01",
        "movie_id": 27205,
        "movie_title": "Inception",
        "movie_year": "2010",
        "movie_poster": "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
        "author_name": "Julian Miller",
        "author_handle": "@julian_cine",
        "avatar_color": "#1A4B5C",
        "avatar_fg": "#8BE9FD",
        "rating": 5.0,
        "is_liked": True,
        "contains_spoilers": False,
        "review_text": (
            "A labyrinth of subconscious architecture and sheer auditory grandeur. Christopher Nolan treats the human psyche "
            "not as a dreamscape of whimsy, but as an impenetrable fortress of regret and catharsis. Zimmer's score vibrates straight "
            "into your ribcage. That final spinning totem remains one of cinema's most exhilarating ambiguities."
        ),
        "sentiment_label": "POSITIVE",
        "sentiment_confidence": 98.4,
        "model_used": "Logistic Regression",
        "created_at": "2026-10-23T19:42:00",
        "formatted_date": "23 Oct 2026",
        "likes_count": 42,
    },
    {
        "id": "rev_seed_parasite_01",
        "movie_id": 496243,
        "movie_title": "Parasite",
        "movie_year": "2019",
        "movie_poster": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
        "author_name": "Sora Takahashi",
        "author_handle": "@soracine",
        "avatar_color": "#5C3A21",
        "avatar_fg": "#FFB86C",
        "rating": 5.0,
        "is_liked": True,
        "contains_spoilers": False,
        "review_text": (
            "Bong Joon-ho crafts a flawless social satire where every staircase, line of sight, and rainfall sequence carries architectural "
            "weight. The mid-film doorbell ring is the exact hinge where modern cinema transformed. Hilarious, devastating, and immaculate."
        ),
        "sentiment_label": "POSITIVE",
        "sentiment_confidence": 97.9,
        "model_used": "Naive Bayes",
        "created_at": "2026-10-22T18:05:00",
        "formatted_date": "22 Oct 2026",
        "likes_count": 37,
    },
    {
        "id": "rev_seed_interstellar_01",
        "movie_id": 157336,
        "movie_title": "Interstellar",
        "movie_year": "2014",
        "movie_poster": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        "author_name": "Elena Rostova",
        "author_handle": "@elenafilms",
        "avatar_color": "#22314E",
        "avatar_fg": "#BD93F9",
        "rating": 4.5,
        "is_liked": True,
        "contains_spoilers": False,
        "review_text": (
            "A celestial hymn to human stubbornness and love across spatiotemporal dimensions. The docking sequence at spinning frequency "
            "made my chest seize up in the theatre. Even when the dialogue tilts slightly sentimental, Hoyte van Hoytema's 70mm imagery is staggering."
        ),
        "sentiment_label": "POSITIVE",
        "sentiment_confidence": 95.3,
        "model_used": "Logistic Regression",
        "created_at": "2026-10-21T11:20:00",
        "formatted_date": "21 Oct 2026",
        "likes_count": 31,
    },
]


def _ensure_storage_initialized() -> None:
    """Ensure data directory and JSON storage files exist with seed data."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(REVIEWS_FILE):
        try:
            with open(REVIEWS_FILE, "w", encoding="utf-8") as f:
                json.dump(INITIAL_SEED_REVIEWS, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    if not os.path.exists(WATCHED_FILE):
        try:
            with open(WATCHED_FILE, "w", encoding="utf-8") as f:
                json.dump(INITIAL_SEED_WATCHED, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


def load_all_reviews() -> List[Dict[str, Any]]:
    """
    Load all stored reviews from persistent storage, ordered by most recent first.
    Returns empty list if file cannot be loaded.
    """
    _ensure_storage_initialized()
    with _LOCK:
        try:
            if not os.path.exists(REVIEWS_FILE):
                return []
            with open(REVIEWS_FILE, "r", encoding="utf-8") as f:
                reviews = json.load(f)
                if isinstance(reviews, list):
                    # Sort by created_at descending (latest first)
                    return sorted(reviews, key=lambda r: r.get("created_at", ""), reverse=True)
                return []
        except Exception:
            return []


def _save_all_reviews_atomic(reviews: List[Dict[str, Any]]) -> bool:
    """Save reviews list atomically to avoid corruption on concurrent writes."""
    _ensure_storage_initialized()
    tmp_file = f"{REVIEWS_FILE}.tmp_{uuid.uuid4().hex[:8]}"
    try:
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(reviews, f, indent=2, ensure_ascii=False)
        os.replace(tmp_file, REVIEWS_FILE)
        return True
    except Exception:
        if os.path.exists(tmp_file):
            try:
                os.remove(tmp_file)
            except Exception:
                pass
        return False


def get_reviews_for_movie(
    movie_id: Optional[Any] = None,
    movie_title: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve stored reviews matching a specific film by movie_id or title.
    If movie_id is provided, matches on int or string comparison.
    If not, falls back to normalized movie title comparison.
    """
    all_reviews = load_all_reviews()
    matched: List[Dict[str, Any]] = []

    m_id_str = str(movie_id).strip() if movie_id is not None and str(movie_id).strip() not in ("", "None") else None
    norm_title = movie_title.strip().lower() if movie_title else None

    for rev in all_reviews:
        rev_m_id = str(rev.get("movie_id", "")).strip()
        rev_title = rev.get("movie_title", "").strip().lower()

        if m_id_str and rev_m_id == m_id_str:
            matched.append(rev)
        elif norm_title and rev_title == norm_title:
            matched.append(rev)

    return matched


def save_review(
    movie_id: Optional[Any],
    movie_title: str,
    movie_year: str,
    movie_poster: str,
    author_name: str,
    author_handle: str,
    rating: float,
    is_liked: bool,
    contains_spoilers: bool,
    review_text: str,
    sentiment_label: str,
    sentiment_confidence: float,
    model_used: str,
) -> Dict[str, Any]:
    """
    Persistently save a new review entry into the Letterboxd community store.
    """
    _ensure_storage_initialized()

    now = datetime.now()
    created_at = now.isoformat()
    formatted_date = now.strftime("%d %b %Y")

    # Pick avatar color hash from author name
    palette_idx = abs(hash(author_name or "cinephile")) % len(AVATAR_PALETTES)
    palette = AVATAR_PALETTES[palette_idx]

    # Clean handle
    clean_handle = author_handle.strip()
    if clean_handle and not clean_handle.startswith("@"):
        clean_handle = f"@{clean_handle}"
    elif not clean_handle:
        clean_handle = f"@{author_name.lower().replace(' ', '')}" if author_name else "@cinephile"

    new_review: Dict[str, Any] = {
        "id": f"rev_{now.strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}",
        "movie_id": movie_id,
        "movie_title": movie_title.strip() if movie_title else "Untitled",
        "movie_year": str(movie_year).strip() if movie_year else "N/A",
        "movie_poster": movie_poster.strip() if movie_poster else "",
        "author_name": author_name.strip() if author_name else "Anonymous Cinephile",
        "author_handle": clean_handle,
        "avatar_color": palette["bg"],
        "avatar_fg": palette["fg"],
        "rating": float(rating),
        "is_liked": bool(is_liked),
        "contains_spoilers": bool(contains_spoilers),
        "review_text": review_text.strip(),
        "sentiment_label": sentiment_label.upper(),
        "sentiment_confidence": round(float(sentiment_confidence), 1),
        "model_used": model_used,
        "created_at": created_at,
        "formatted_date": formatted_date,
        "likes_count": 0,
    }

    with _LOCK:
        all_reviews = load_all_reviews()
        all_reviews.insert(0, new_review)
        _save_all_reviews_atomic(all_reviews)

    # Dynamically log movie in user's watched diary
    if movie_title:
        mark_movie_as_watched(
            movie_id=movie_id,
            title=movie_title,
            year=str(movie_year),
            poster_url=movie_poster,
            is_liked=is_liked,
            rating=rating,
        )

    return new_review


def like_review(review_id: str) -> int:
    """
    Increment like count on a review by ID.
    Returns the updated like count, or 0 if not found.
    """
    with _LOCK:
        all_reviews = load_all_reviews()
        updated_likes = 0
        found = False
        for rev in all_reviews:
            if rev.get("id") == review_id:
                rev["likes_count"] = int(rev.get("likes_count", 0)) + 1
                updated_likes = rev["likes_count"]
                found = True
                break
        if found:
            _save_all_reviews_atomic(all_reviews)
        return updated_likes


def get_movie_review_stats(
    movie_id: Optional[Any] = None,
    movie_title: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Calculate Letterboxd-style statistics for a movie:
    - total reviews
    - average rating (1 to 5)
    - star counts histogram (1, 2, 3, 4, 5)
    - positive vs negative counts and percentages
    - liked percentage
    """
    reviews = get_reviews_for_movie(movie_id, movie_title)
    total = len(reviews)
    if total == 0:
        return {
            "total_count": 0,
            "average_rating": 0.0,
            "star_counts": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            "positive_count": 0,
            "negative_count": 0,
            "positive_percentage": 0.0,
            "liked_count": 0,
            "liked_percentage": 0.0,
        }

    ratings = [float(r.get("rating", 0.0)) for r in reviews]
    avg_rating = sum(ratings) / total

    star_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r in ratings:
        clamped = max(1, min(5, round(r)))
        star_counts[clamped] += 1

    pos_count = sum(1 for r in reviews if r.get("sentiment_label") == "POSITIVE")
    neg_count = sum(1 for r in reviews if r.get("sentiment_label") == "NEGATIVE")
    liked_count = sum(1 for r in reviews if r.get("is_liked"))

    return {
        "total_count": total,
        "average_rating": round(avg_rating, 1),
        "star_counts": star_counts,
        "positive_count": pos_count,
        "negative_count": neg_count,
        "positive_percentage": round((pos_count / total) * 100, 1),
        "liked_count": liked_count,
        "liked_percentage": round((liked_count / total) * 100, 1),
    }


def get_recent_reviews(limit: int = 6) -> List[Dict[str, Any]]:
    """Get the latest reviews across all films."""
    all_revs = load_all_reviews()
    return all_revs[:limit]


# =============================================================================
# Dynamic Watched Movies & Diary Tracking (Letterboxd Watched System)
# =============================================================================

def load_all_watched_movies() -> List[Dict[str, Any]]:
    """
    Load all dynamically stored watched films from data/user_watched_movies.json.
    Returns list sorted by latest watched first.
    """
    _ensure_storage_initialized()
    with _LOCK:
        try:
            if not os.path.exists(WATCHED_FILE):
                return []
            with open(WATCHED_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return sorted(data, key=lambda m: m.get("watched_at", ""), reverse=True)
                return []
        except Exception:
            return []


def _save_all_watched_atomic(watched: List[Dict[str, Any]]) -> bool:
    """Save watched movies list atomically to avoid concurrent corruption."""
    _ensure_storage_initialized()
    tmp_file = f"{WATCHED_FILE}.tmp_{uuid.uuid4().hex[:8]}"
    try:
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(watched, f, indent=2, ensure_ascii=False)
        os.replace(tmp_file, WATCHED_FILE)
        return True
    except Exception:
        if os.path.exists(tmp_file):
            try:
                os.remove(tmp_file)
            except Exception:
                pass
        return False


def is_movie_watched(movie_id: Optional[Any] = None, movie_title: Optional[str] = None) -> bool:
    """
    Check dynamically if a movie has been marked as watched.
    Checks by ID first, then falls back to title.
    """
    return get_watched_movie(movie_id, movie_title) is not None


def get_watched_movie(movie_id: Optional[Any] = None, movie_title: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieve watched record for a movie if it exists in the persistent store.
    """
    watched_list = load_all_watched_movies()
    m_id_str = str(movie_id).strip() if movie_id is not None and str(movie_id).strip() not in ("", "None") else None
    norm_title = movie_title.strip().lower() if movie_title else None

    for m in watched_list:
        if m_id_str and str(m.get("movie_id", "")).strip() == m_id_str:
            return m
        if norm_title and m.get("title", "").strip().lower() == norm_title:
            return m
    return None


def mark_movie_as_watched(
    movie_id: Optional[Any],
    title: str,
    year: str = "",
    poster_url: str = "",
    is_liked: bool = False,
    rating: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Dynamically save or update a watched movie in persistent storage.
    If already marked, increments watch_count and updates timestamp.
    """
    _ensure_storage_initialized()
    now = datetime.now()
    watched_at = now.isoformat()
    formatted_date = now.strftime("%d %b %Y")

    with _LOCK:
        watched_list = load_all_watched_movies()
        m_id_str = str(movie_id).strip() if movie_id is not None and str(movie_id).strip() not in ("", "None") else None
        norm_title = title.strip().lower() if title else None

        existing_idx = None
        for i, m in enumerate(watched_list):
            if m_id_str and str(m.get("movie_id", "")).strip() == m_id_str:
                existing_idx = i
                break
            if norm_title and m.get("title", "").strip().lower() == norm_title:
                existing_idx = i
                break

        if existing_idx is not None:
            entry = watched_list.pop(existing_idx)
            entry["watch_count"] = int(entry.get("watch_count", 1)) + 1
            entry["watched_at"] = watched_at
            entry["formatted_date"] = formatted_date
            if is_liked:
                entry["is_liked"] = True
            if rating is not None:
                entry["rating"] = float(rating)
            if poster_url and not entry.get("poster_url"):
                entry["poster_url"] = poster_url
            watched_list.insert(0, entry)
            _save_all_watched_atomic(watched_list)
            return entry
        else:
            new_entry: Dict[str, Any] = {
                "movie_id": movie_id,
                "title": title.strip() if title else "Untitled",
                "year": str(year).strip() if year else "N/A",
                "poster_url": poster_url.strip() if poster_url else "",
                "watched_at": watched_at,
                "formatted_date": formatted_date,
                "is_liked": bool(is_liked),
                "rating": float(rating) if rating is not None else None,
                "watch_count": 1,
            }
            watched_list.insert(0, new_entry)
            _save_all_watched_atomic(watched_list)
            return new_entry


def unmark_movie_as_watched(movie_id: Optional[Any] = None, movie_title: Optional[str] = None) -> bool:
    """
    Dynamically remove a movie from persistent watched storage.
    """
    _ensure_storage_initialized()
    with _LOCK:
        watched_list = load_all_watched_movies()
        m_id_str = str(movie_id).strip() if movie_id is not None and str(movie_id).strip() not in ("", "None") else None
        norm_title = movie_title.strip().lower() if movie_title else None

        initial_len = len(watched_list)
        filtered = [
            m for m in watched_list
            if not (
                (m_id_str and str(m.get("movie_id", "")).strip() == m_id_str)
                or (norm_title and m.get("title", "").strip().lower() == norm_title)
            )
        ]
        if len(filtered) != initial_len:
            _save_all_watched_atomic(filtered)
            return True
        return False


def toggle_movie_watched(movie: Dict[str, Any]) -> bool:
    """
    Dynamically toggle watched status for a movie:
    - If already watched -> unmarks it and returns False.
    - If not watched -> marks it and returns True.
    """
    m_id = movie.get("id")
    m_title = movie.get("title", "")
    if is_movie_watched(m_id, m_title):
        unmark_movie_as_watched(m_id, m_title)
        return False
    else:
        m_year = movie.get("release_year") or (movie.get("release_date") or "")[:4] or "N/A"
        m_poster = movie.get("poster_url") or movie.get("poster") or ""
        mark_movie_as_watched(
            movie_id=m_id,
            title=m_title,
            year=m_year,
            poster_url=m_poster,
        )
        return True


def toggle_movie_liked(movie: Dict[str, Any]) -> bool:
    """
    Dynamically toggle liked (heart) status for a movie.
    """
    m_id = movie.get("id")
    m_title = movie.get("title", "")
    _ensure_storage_initialized()
    with _LOCK:
        watched_list = load_all_watched_movies()
        found = False
        res = False
        for m in watched_list:
            if (m_id and str(m.get("movie_id", "")).strip() == str(m_id).strip()) or (m_title and m.get("title", "").strip().lower() == m_title.strip().lower()):
                m["is_liked"] = not m.get("is_liked", False)
                res = m["is_liked"]
                found = True
                break
        if found:
            _save_all_watched_atomic(watched_list)
            return res

        # If movie was not marked watched yet, mark it as watched and liked
        m_year = movie.get("release_year") or (movie.get("release_date") or "")[:4] or "N/A"
        m_poster = movie.get("poster_url") or movie.get("poster") or ""
        mark_movie_as_watched(m_id, m_title, m_year, m_poster, is_liked=True)
        return True


def get_watched_stats() -> Dict[str, Any]:
    """
    Summary stats of dynamically watched movies in user diary.
    """
    watched_list = load_all_watched_movies()
    total = len(watched_list)
    liked = sum(1 for m in watched_list if m.get("is_liked"))
    rated = [m.get("rating") for m in watched_list if m.get("rating") is not None]
    avg_r = (sum(rated) / len(rated)) if rated else 0.0
    return {
        "total_watched": total,
        "liked_count": liked,
        "rated_count": len(rated),
        "average_rating": round(avg_r, 1),
    }

