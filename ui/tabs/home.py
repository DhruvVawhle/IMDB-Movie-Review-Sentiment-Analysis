"""
Home Tab for CineSense — Default Landing Page.
Presents 'In theatres now' and 'Coming soon' poster grids powered by TMDB API.
Clicking any film card opens its full details on the Movies tab with 'Review this film'.
"""

from typing import Any, Dict, List
import streamlit as st

from services.tmdb_service import get_movies_by_category_and_region, get_tmdb_api_key
from ui.components import render_empty_state, set_active_tab


def get_badge_css_class(origin_label: str) -> str:
    """Backward-compatible helper returning neutral or accent badge CSS class."""
    mapping = {
        "Indian": "cinesense-region-badge-in",
        "Hollywood": "cinesense-region-badge-us",
        "International": "cinesense-region-badge-intl",
        "Unclassified": "cinesense-region-badge-unclassified",
    }
    return mapping.get(origin_label, "cinesense-region-badge-unclassified")


def render_movie_card(movie: Dict[str, Any], group_key: str, idx: int) -> None:
    """Render an art-directed cinema poster card with 2:3 aspect ratio, audience score, and view CTA."""
    poster_url = movie.get("poster_url", "")
    score = movie.get("audience_score", 0.0)
    title = movie.get("title", "Untitled")
    formatted_date = movie.get("formatted_date", "TBA")
    genres = movie.get("genres", [])
    genres_str = " · ".join(genres[:2]) if genres else "Film"

    # Poster Frame with Overlaid Score Pill
    img_element = (
        f'<img src="{poster_url}" class="cinesense-poster-img" alt="{title}" loading="lazy" />'
        if poster_url
        else '<div class="cinesense-poster-placeholder"><span>🎬</span> No Poster</div>'
    )

    card_html = f"""
    <div class="cinesense-film-card">
        <div class="cinesense-poster-frame">
            {img_element}
            <div class="cinesense-poster-gradient"></div>
            <div class="cinesense-poster-badge-wrap">
                <span class="cinesense-score-pill"><span style="color:var(--accent);">★</span> {score:.1f}</span>
            </div>
        </div>
        <div class="cinesense-card-content">
            <div class="cinesense-film-title" title="{title}">{title}</div>
            <div class="cinesense-film-meta">
                <span class="cinesense-film-date">{formatted_date}</span>
                <span class="cinesense-film-dot">·</span>
                <span class="cinesense-film-genre" title="{genres_str}">{genres_str}</span>
            </div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

    # 44px Accessible CTA Button
    btn_key = f"home_card_{group_key}_{movie.get('id', idx)}_{idx}"
    if st.button("View details →", key=btn_key, use_container_width=True):
        st.session_state["selected_movie_data"] = movie
        st.session_state["selected_movie_id"] = movie.get("id")
        st.session_state["selected_movie_title"] = movie.get("title", "")
        set_active_tab("Movies")
        st.rerun()


def render_movie_grid(movies: List[Dict[str, Any]], group_key: str, empty_title: str, empty_desc: str) -> None:
    """Render a responsive multi-column poster grid with empty state support."""
    if not movies:
        render_empty_state(empty_title, empty_desc)
        return

    n_cols = 5
    rows = [movies[i : i + n_cols] for i in range(0, len(movies), n_cols)]
    for r_idx, row in enumerate(rows):
        cols = st.columns(n_cols)
        for c_idx, movie in enumerate(row):
            global_idx = r_idx * n_cols + c_idx
            with cols[c_idx]:
                render_movie_card(movie, group_key, global_idx)
                st.write("")


def render_home_tab() -> None:
    api_key = get_tmdb_api_key()
    if not api_key:
        st.markdown(
            """
            <div class="cinesense-notice" style="margin-bottom: 1.25rem;">
                <strong>TMDB API key not configured.</strong> Live theatrical lists cannot be retrieved.<br />
                To enable live title search, add your key to
                <code>.streamlit/secrets.toml</code>:<br />
                <code>TMDB_API_KEY = "your_tmdb_api_key"</code>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Editorial Intro Banner
    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <p class="cinesense-takeaway" style="font-size:1.05rem; color:var(--ink); margin-bottom: 0.35rem;">
                Live theatrical releases and upcoming premieres.
            </p>
            <p style="font-family:var(--font-body); font-size:0.85rem; color:var(--muted); margin:0;">
                Select any title to view details and launch the sentiment analyzer directly for that film.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Section 1: In theatres now
    now_playing_movies: List[Dict[str, Any]] = []
    error_now_playing = False
    with st.spinner("Fetching current theatrical releases..."):
        try:
            now_playing_movies = get_movies_by_category_and_region("now_playing", "All")
        except Exception:
            error_now_playing = True

    if error_now_playing:
        st.warning("TMDB request failed or timed out while fetching current theatrical releases.")
        if st.button("Retry releases", key="retry_now_playing"):
            st.cache_data.clear()
            st.rerun()

    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:1.25rem; margin-bottom:0.85rem; border-bottom:1px solid var(--line); padding-bottom:0.4rem;">
            <div style="display:flex; align-items:center; gap:0.4rem;">
                <span class="cinesense-live-dot"></span>
                <span class="cinesense-section-title" style="margin:0;">In theatres now</span>
            </div>
            <span class="badge-neutral" style="font-size:0.75rem;">{len(now_playing_movies)} titles</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_movie_grid(
        now_playing_movies,
        group_key="now_playing",
        empty_title="No films currently in theatres",
        empty_desc="No current theatrical releases were returned from TMDB.",
    )

    # Section 2: Coming soon
    upcoming_movies: List[Dict[str, Any]] = []
    error_upcoming = False
    with st.spinner("Fetching upcoming releases..."):
        try:
            upcoming_movies = get_movies_by_category_and_region("upcoming", "All")
        except Exception:
            error_upcoming = True

    if error_upcoming:
        st.warning("TMDB request failed or timed out while fetching upcoming releases.")
        if st.button("Retry upcoming", key="retry_upcoming"):
            st.cache_data.clear()
            st.rerun()

    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:2.25rem; margin-bottom:0.85rem; border-bottom:1px solid var(--line); padding-bottom:0.4rem;">
            <div style="display:flex; align-items:center; gap:0.4rem;">
                <span style="font-size:1.1rem; line-height:1;">🗓️</span>
                <span class="cinesense-section-title" style="margin:0;">Coming soon</span>
            </div>
            <span class="badge-neutral" style="font-size:0.75rem;">{len(upcoming_movies)} titles</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_movie_grid(
        upcoming_movies,
        group_key="upcoming",
        empty_title="No upcoming films found",
        empty_desc="No upcoming releases were returned from TMDB.",
    )
