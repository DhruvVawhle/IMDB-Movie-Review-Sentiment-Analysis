"""
Unit tests for review storage service.
"""

import os
import shutil
import tempfile
import pytest

from services import review_storage_service


@pytest.fixture(autouse=True)
def isolated_storage(monkeypatch):
    """Isolate review and watched storage to a temporary directory for each test."""
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, "test_reviews.json")
    temp_watched = os.path.join(temp_dir, "test_watched.json")
    monkeypatch.setattr(review_storage_service, "DATA_DIR", temp_dir)
    monkeypatch.setattr(review_storage_service, "REVIEWS_FILE", temp_file)
    monkeypatch.setattr(review_storage_service, "WATCHED_FILE", temp_watched)
    yield
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_initial_seed_creation():
    reviews = review_storage_service.load_all_reviews()
    assert len(reviews) > 0
    assert reviews[0]["movie_title"] in [
        "Inception", "The Dark Knight", "Parasite", "Interstellar",
        "Dune: Part Two", "The Godfather", "Oppenheimer", "12 Angry Men",
        "Pulp Fiction", "Taxi Driver", "Past Lives"
    ]


def test_save_and_retrieve_review():
    new_rev = review_storage_service.save_review(
        movie_id=99999,
        movie_title="Test Cinematic Masterpiece",
        movie_year="2024",
        movie_poster="https://example.com/poster.jpg",
        author_name="Cinephile Tester",
        author_handle="cine_tester",
        rating=4.5,
        is_liked=True,
        contains_spoilers=False,
        review_text="An absolutely exquisite sensory journey with remarkable performances and score.",
        sentiment_label="POSITIVE",
        sentiment_confidence=97.5,
        model_used="Logistic Regression",
    )

    assert new_rev["id"].startswith("rev_")
    assert new_rev["author_handle"] == "@cine_tester"
    assert new_rev["rating"] == 4.5
    assert new_rev["is_liked"] is True

    # Retrieve by movie_id
    movie_revs = review_storage_service.get_reviews_for_movie(99999)
    assert len(movie_revs) == 1
    assert movie_revs[0]["movie_title"] == "Test Cinematic Masterpiece"

    # Retrieve by title
    title_revs = review_storage_service.get_reviews_for_movie(movie_title="Test Cinematic Masterpiece")
    assert len(title_revs) == 1


def test_like_review():
    new_rev = review_storage_service.save_review(
        movie_id=88888,
        movie_title="Film To Like",
        movie_year="2023",
        movie_poster="",
        author_name="Sam",
        author_handle="@sam",
        rating=5.0,
        is_liked=False,
        contains_spoilers=False,
        review_text="Loved this film deeply.",
        sentiment_label="POSITIVE",
        sentiment_confidence=95.0,
        model_used="Naive Bayes",
    )

    rev_id = new_rev["id"]
    updated_likes = review_storage_service.like_review(rev_id)
    assert updated_likes == 1

    updated_likes_2 = review_storage_service.like_review(rev_id)
    assert updated_likes_2 == 2


def test_review_stats():
    # Save a positive and negative review
    review_storage_service.save_review(
        movie_id=77777,
        movie_title="Duality Film",
        movie_year="2025",
        movie_poster="",
        author_name="Viewer A",
        author_handle="@a",
        rating=5.0,
        is_liked=True,
        contains_spoilers=False,
        review_text="Fantastic film.",
        sentiment_label="POSITIVE",
        sentiment_confidence=92.0,
        model_used="Logistic Regression",
    )
    review_storage_service.save_review(
        movie_id=77777,
        movie_title="Duality Film",
        movie_year="2025",
        movie_poster="",
        author_name="Viewer B",
        author_handle="@b",
        rating=2.0,
        is_liked=False,
        contains_spoilers=False,
        review_text="Terrible pacing.",
        sentiment_label="NEGATIVE",
        sentiment_confidence=88.0,
        model_used="Logistic Regression",
    )

    stats = review_storage_service.get_movie_review_stats(77777)
    assert stats["total_count"] == 2
    assert stats["average_rating"] == 3.5
    assert stats["positive_count"] == 1
    assert stats["negative_count"] == 1
    assert stats["positive_percentage"] == 50.0
    assert stats["liked_count"] == 1


def test_dynamic_watched_movie_lifecycle():
    # 1. Check initially not watched
    assert review_storage_service.is_movie_watched(54321) is False

    # 2. Mark as watched dynamically
    res = review_storage_service.mark_movie_as_watched(
        movie_id=54321,
        title="Spirited Away",
        year="2001",
        poster_url="https://example.com/spirited.jpg",
        is_liked=True,
        rating=5.0,
    )
    assert res["title"] == "Spirited Away"
    assert res["is_liked"] is True
    assert res["watch_count"] == 1

    # Verify dynamically stored
    assert review_storage_service.is_movie_watched(54321) is True
    assert review_storage_service.is_movie_watched(movie_title="Spirited Away") is True

    record = review_storage_service.get_watched_movie(54321)
    assert record is not None
    assert record["rating"] == 5.0

    # 3. Toggle watched status off
    toggle_res = review_storage_service.toggle_movie_watched({"id": 54321, "title": "Spirited Away"})
    assert toggle_res is False
    assert review_storage_service.is_movie_watched(54321) is False

    # 4. Toggle watched status on
    toggle_res_2 = review_storage_service.toggle_movie_watched({"id": 54321, "title": "Spirited Away"})
    assert toggle_res_2 is True
    assert review_storage_service.is_movie_watched(54321) is True

    # 5. Toggle liked status
    liked = review_storage_service.toggle_movie_liked({"id": 54321, "title": "Spirited Away"})
    assert liked in (True, False)

    # 6. Unmark
    unmarked = review_storage_service.unmark_movie_as_watched(54321)
    assert unmarked is True
    assert review_storage_service.is_movie_watched(54321) is False


def test_render_html_no_indented_code_blocks(monkeypatch):
    """Ensure render_html strips all indentation and empty lines so markdown never creates code blocks."""
    from ui.components import render_html
    import streamlit as st

    captured_markdown = []
    monkeypatch.setattr(st, "markdown", lambda content, unsafe_allow_html=False: captured_markdown.append(content))

    raw_indented_html = """
    <div class="test-card">
        
        <div class="test-inner">
            <span>Nested content</span>
        </div>
    </div>
    """
    render_html(raw_indented_html)

    assert len(captured_markdown) == 1
    rendered = captured_markdown[0]
    for line in rendered.splitlines():
        assert not line.startswith("    "), f"Line starts with 4 spaces: {line}"
        assert line.strip() != "", "Empty line found in rendered HTML"
    assert "<div class=\"test-card\">" in rendered
    assert "<div class=\"test-inner\">" in rendered


def test_render_letterboxd_review_card_does_not_leak_raw_code(monkeypatch):
    """Verify render_letterboxd_review_card never produces 4-space indented lines after empty variables."""
    from ui.components import render_letterboxd_review_card
    import streamlit as st

    captured_markdown = []
    monkeypatch.setattr(st, "markdown", lambda content, unsafe_allow_html=False: captured_markdown.append(content))

    maya_review = {
        "id": "rev_test_maya",
        "movie_id": 27205,
        "movie_title": "Inception",
        "movie_year": "2010",
        "author_name": "Maya Lin",
        "author_handle": "@mayareviews",
        "avatar_color": "#3B2654",
        "avatar_fg": "#FF79C6",
        "rating": 4.5,
        "is_liked": True,
        "contains_spoilers": False,
        "review_text": "The hallway fight sequence alone rewired how action cinema could stage physics.",
        "sentiment_label": "POSITIVE",
        "sentiment_confidence": 95.0,
        "model_used": "BiLSTM Neural Network",
        "formatted_date": "26 Oct 2026",
        "likes_count": 19,
    }

    # Render without film tag (show_film_tag=False), which previously left an empty interpolation line
    render_letterboxd_review_card(maya_review, show_film_tag=False)

    assert len(captured_markdown) == 1
    rendered = captured_markdown[0]
    # Verify no line has leading spaces that would trigger an indented code block
    for line in rendered.splitlines():
        assert not line.startswith("    "), f"Line has >=4 spaces leading: {line}"
    assert "letterboxd-card-header" in rendered
    assert "Maya Lin" in rendered
    assert "BiLSTM Neural Network" in rendered


