"""
Home Tab for CineSense — Default Landing Page.
Presents 'In theatres now' and 'Coming soon' poster grids powered by TMDB API.
Clicking any film card opens its full details on the Movies tab with 'Review this film'.
"""

from typing import Any, Dict, List
import random
import time
import streamlit as st

from services.review_storage_service import get_recent_reviews, is_movie_watched
from services.tmdb_service import get_movies_by_category_and_region, get_tmdb_api_key
from ui.components import render_empty_state, render_html, render_letterboxd_review_card, set_active_tab


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
    genres_str = ", ".join(genres[:2]) if genres else "Film"
    m_watched = is_movie_watched(movie.get("id"), title)
    watched_badge_html = (
        '<div class="cinesense-watched-tag">Watched</div>'
        if m_watched
        else ""
    )

    # Poster Frame with Overlaid Score Pill and Watched Badge
    img_element = (
        f'<img src="{poster_url}" class="cinesense-poster-img" alt="{title}" loading="lazy" />'
        if poster_url
        else '<div class="cinesense-poster-placeholder"><span>Film Archive</span><span>No poster available</span></div>'
    )

    card_html = f"""
    <div class="cinesense-film-card">
        <div class="cinesense-poster-frame">
            {img_element}
            {watched_badge_html}
            <div class="cinesense-poster-gradient"></div>
            <div class="cinesense-poster-badge-wrap">
                <span class="cinesense-score-pill"><span style="color:var(--accent);">★</span> {score:.1f}</span>
            </div>
        </div>
        <div class="cinesense-card-content">
            <div class="cinesense-film-title" title="{title}">{title}</div>
            <div class="cinesense-film-meta" style="display:flex; justify-content:space-between; align-items:center;">
                <span class="cinesense-film-date" style="color:var(--accent); font-weight:600; font-size:0.75rem;">{formatted_date}</span>
                <span class="cinesense-genre-tag" title="{genres_str}">{genres_str}</span>
            </div>
        </div>
    </div>
    """
    render_html(card_html)

    # 44px Accessible CTA Button
    btn_key = f"home_card_{group_key}_{movie.get('id', idx)}_{idx}"
    if st.button("View film details", key=btn_key, use_container_width=True):
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



@st.fragment(run_every=7)
def render_theatrical_carousel(now_playing_movies: List[Dict[str, Any]]) -> None:
    """Theatrical releases carousel with automatic 7s rotation, pause/play toggle, and manual controls."""
    PAGE_SIZE = 5

    # Filter by region pill if selected (safely default to All if empty or deselected)
    region_now_pill = st.session_state.get("home_theatre_region_pills")
    reg_filter_now = "All" if (not region_now_pill or region_now_pill == "All cinema") else region_now_pill

    # Reset offset if region changed
    prev_reg = st.session_state.get("_prev_reg_now")
    if prev_reg != reg_filter_now:
        st.session_state["home_now_offset"] = 0
        st.session_state["_prev_reg_now"] = reg_filter_now

    active_now_movies = [m for m in now_playing_movies if reg_filter_now == "All" or m.get("origin_label") == reg_filter_now]
    total_now = len(active_now_movies)

    # Auto-advance timing: rotates every 7 seconds when active
    is_auto = st.session_state.get("home_now_auto", True)
    now_ts = time.time()
    last_ts = st.session_state.get("_now_frag_ts", 0)

    if is_auto and last_ts > 0 and (now_ts - last_ts) >= 6.0 and total_now > PAGE_SIZE:
        st.session_state["home_now_offset"] = (st.session_state.get("home_now_offset", 0) + PAGE_SIZE) % total_now
        st.session_state["_now_frag_ts"] = now_ts
    elif last_ts == 0:
        st.session_state["_now_frag_ts"] = now_ts

    if total_now > 0:
        offset_now = st.session_state.get("home_now_offset", 0) % total_now
        offset_now = (offset_now // PAGE_SIZE) * PAGE_SIZE
        displayed_now = [active_now_movies[(offset_now + i) % total_now] for i in range(min(PAGE_SIZE, total_now))]
        current_page_now = (offset_now // PAGE_SIZE) + 1
        total_pages_now = (total_now + PAGE_SIZE - 1) // PAGE_SIZE
        start_now = offset_now + 1
        end_now = min(offset_now + PAGE_SIZE, total_now)
    else:
        displayed_now = []
        current_page_now = 1
        total_pages_now = 1
        start_now = 0
        end_now = 0

    # Header Row: Title on Left, Controls on Right
    now_head_col, now_act_col = st.columns([2.55, 2.45], gap="medium", vertical_alignment="center")
    with now_head_col:
        st.markdown(
            """
            <div style="display:flex; align-items:center; gap:0.55rem; flex-wrap:wrap; margin-top:0.75rem;">
                <span class="cinesense-live-dot"></span>
                <span class="cinesense-section-title" style="margin:0; border:none; padding:0; line-height:1.2;">In theatres now</span>
                <span class="badge-neutral" style="font-size:0.7rem; letter-spacing:0.02em;">Latest dated releases</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with now_act_col:
        c_auto_col, c_badge_col, c_prev_col, c_next_col, c_sync_col = st.columns(
            [1.2, 1.25, 0.75, 0.75, 0.75], gap="small", vertical_alignment="center"
        )
        with c_auto_col:
            auto_label = "⏸ Auto" if is_auto else "▶ Auto"
            auto_help = "Auto-play is active (rotates every 7s). Click to pause." if is_auto else "Auto-play is paused. Click to play."
            if st.button(auto_label, key="btn_auto_home_now", use_container_width=True, help=auto_help):
                st.session_state["home_now_auto"] = not is_auto
                st.session_state["_now_frag_ts"] = time.time()
                st.rerun()
        with c_badge_col:
            st.markdown(
                f'<div class="cinesense-carousel-counter" style="text-align:center;">{start_now}–{end_now} of {total_now}</div>',
                unsafe_allow_html=True,
            )
        with c_prev_col:
            if st.button("◀", key="btn_prev_home_now", use_container_width=True, help="Previous 5 films"):
                if total_now > 0:
                    st.session_state["home_now_offset"] = (offset_now - PAGE_SIZE) % total_now
                    st.session_state["_now_frag_ts"] = time.time()
                    st.rerun()
        with c_next_col:
            if st.button("▶", key="btn_next_home_now", use_container_width=True, help="Next 5 films"):
                if total_now > 0:
                    st.session_state["home_now_offset"] = (offset_now + PAGE_SIZE) % total_now
                    st.session_state["_now_frag_ts"] = time.time()
                    st.rerun()
        with c_sync_col:
            if st.button("⟳", key="btn_refresh_home_now", use_container_width=True, help="Sync live TMDB releases"):
                st.cache_data.clear()
                st.rerun()

    # Section 1 Pills and Carousel Dots
    now_pills_col, now_dots_col = st.columns([3.2, 1.8], gap="medium", vertical_alignment="center")
    with now_pills_col:
        st.pills(
            "Filter theatrical releases",
            options=["All cinema", "Hollywood", "Indian"],
            default="All cinema",
            label_visibility="collapsed",
            key="home_theatre_region_pills",
        )
    with now_dots_col:
        if total_pages_now > 1:
            dots_html = "".join([
                f'<div class="cinesense-carousel-dot {"active" if p == current_page_now else ""}"></div>'
                for p in range(1, min(total_pages_now + 1, 15))
            ])
            st.markdown(
                f'<div class="cinesense-carousel-dots" style="justify-content:flex-end; margin:0;">{dots_html}</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div style="margin:0.25rem 0 0.85rem 0; border-bottom:1px solid var(--line);"></div>', unsafe_allow_html=True)

    render_movie_grid(
        displayed_now,
        group_key="now_playing",
        empty_title="No films currently in theatres",
        empty_desc="No current theatrical releases were returned from TMDB for this filter.",
    )


@st.fragment(run_every=7)
def render_upcoming_carousel(upcoming_movies: List[Dict[str, Any]]) -> None:
    """Coming soon carousel with automatic 7s rotation, pause/play toggle, and manual controls."""
    PAGE_SIZE = 5

    # Filter by region pill if selected (safely default to All if empty or deselected)
    region_up_pill = st.session_state.get("home_upcoming_region_pills")
    reg_filter_up = "All" if (not region_up_pill or region_up_pill == "All cinema") else region_up_pill

    # Reset offset if region changed
    prev_reg = st.session_state.get("_prev_reg_up")
    if prev_reg != reg_filter_up:
        st.session_state["home_upcoming_offset"] = 0
        st.session_state["_prev_reg_up"] = reg_filter_up

    active_up_movies = [m for m in upcoming_movies if reg_filter_up == "All" or m.get("origin_label") == reg_filter_up]
    total_up = len(active_up_movies)

    # Auto-advance timing: rotates every 7 seconds when active
    is_auto = st.session_state.get("home_upcoming_auto", True)
    now_ts = time.time()
    last_ts = st.session_state.get("_up_frag_ts", 0)

    if is_auto and last_ts > 0 and (now_ts - last_ts) >= 6.0 and total_up > PAGE_SIZE:
        st.session_state["home_upcoming_offset"] = (st.session_state.get("home_upcoming_offset", 0) + PAGE_SIZE) % total_up
        st.session_state["_up_frag_ts"] = now_ts
    elif last_ts == 0:
        st.session_state["_up_frag_ts"] = now_ts

    if total_up > 0:
        offset_up = st.session_state.get("home_upcoming_offset", 0) % total_up
        offset_up = (offset_up // PAGE_SIZE) * PAGE_SIZE
        displayed_up = [active_up_movies[(offset_up + i) % total_up] for i in range(min(PAGE_SIZE, total_up))]
        current_page_up = (offset_up // PAGE_SIZE) + 1
        total_pages_up = (total_up + PAGE_SIZE - 1) // PAGE_SIZE
        start_up = offset_up + 1
        end_up = min(offset_up + PAGE_SIZE, total_up)
    else:
        displayed_up = []
        current_page_up = 1
        total_pages_up = 1
        start_up = 0
        end_up = 0

    # Header Row: Title on Left, Controls on Right
    up_head_col, up_act_col = st.columns([2.55, 2.45], gap="medium", vertical_alignment="center")
    with up_head_col:
        st.markdown(
            """
            <div style="display:flex; align-items:center; gap:0.55rem; flex-wrap:wrap; margin-top:1.5rem;">
                <span class="cinesense-section-title" style="margin:0; border:none; padding:0; line-height:1.2;">Coming soon</span>
                <span class="badge-neutral" style="font-size:0.7rem; letter-spacing:0.02em;">Upcoming premieres</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with up_act_col:
        st.markdown('<div style="height:1.5rem;"></div>', unsafe_allow_html=True)
        up_auto_col, up_badge_col, up_prev_col, up_next_col, up_sync_col = st.columns(
            [1.2, 1.25, 0.75, 0.75, 0.75], gap="small", vertical_alignment="center"
        )
        with up_auto_col:
            auto_label = "⏸ Auto" if is_auto else "▶ Auto"
            auto_help = "Auto-play is active (rotates every 7s). Click to pause." if is_auto else "Auto-play is paused. Click to play."
            if st.button(auto_label, key="btn_auto_home_upcoming", use_container_width=True, help=auto_help):
                st.session_state["home_upcoming_auto"] = not is_auto
                st.session_state["_up_frag_ts"] = time.time()
                st.rerun()
        with up_badge_col:
            st.markdown(
                f'<div class="cinesense-carousel-counter" style="text-align:center;">{start_up}–{end_up} of {total_up}</div>',
                unsafe_allow_html=True,
            )
        with up_prev_col:
            if st.button("◀", key="btn_prev_home_upcoming", use_container_width=True, help="Previous 5 upcoming releases"):
                if total_up > 0:
                    st.session_state["home_upcoming_offset"] = (offset_up - PAGE_SIZE) % total_up
                    st.session_state["_up_frag_ts"] = time.time()
                    st.rerun()
        with up_next_col:
            if st.button("▶", key="btn_next_home_upcoming", use_container_width=True, help="Next 5 upcoming releases"):
                if total_up > 0:
                    st.session_state["home_upcoming_offset"] = (offset_up + PAGE_SIZE) % total_up
                    st.session_state["_up_frag_ts"] = time.time()
                    st.rerun()
        with up_sync_col:
            if st.button("⟳", key="btn_refresh_home_upcoming", use_container_width=True, help="Sync live TMDB releases"):
                st.cache_data.clear()
                st.rerun()

    # Section 2 Pills and Carousel Dots
    up_pills_col, up_dots_col = st.columns([3.2, 1.8], gap="medium", vertical_alignment="center")
    with up_pills_col:
        st.pills(
            "Filter upcoming releases",
            options=["All cinema", "Hollywood", "Indian"],
            default="All cinema",
            label_visibility="collapsed",
            key="home_upcoming_region_pills",
        )
    with up_dots_col:
        if total_pages_up > 1:
            dots_up_html = "".join([
                f'<div class="cinesense-carousel-dot {"active" if p == current_page_up else ""}"></div>'
                for p in range(1, min(total_pages_up + 1, 15))
            ])
            st.markdown(
                f'<div class="cinesense-carousel-dots" style="justify-content:flex-end; margin:0;">{dots_up_html}</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div style="margin:0.25rem 0 0.85rem 0; border-bottom:1px solid var(--line);"></div>', unsafe_allow_html=True)

    render_movie_grid(
        displayed_up,
        group_key="upcoming",
        empty_title="No upcoming films found",
        empty_desc="No upcoming releases were returned from TMDB for this filter.",
    )


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

    # Section 1 Data: In theatres now
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

    # Section 2 Data: Coming soon
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

    # Section 1: In theatres now (Auto-advancing carousel fragment)
    render_theatrical_carousel(now_playing_movies)

    # Section 2: Coming soon (Auto-advancing carousel fragment)
    render_upcoming_carousel(upcoming_movies)

    # Section 3: Letterboxd Community Reviews (Latest Premieres & Vintage Classics)
    all_reviews = get_recent_reviews(limit=50)
    if all_reviews:
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:2.5rem; margin-bottom:0.85rem; border-bottom:1px solid var(--line); padding-bottom:0.4rem;">
                <div style="display:flex; align-items:center; gap:0.4rem;">
                    <span class="cinesense-section-title" style="margin:0;">Recent Letterboxd Reviews</span>
                </div>
                <span class="badge-pos" style="font-size:0.75rem;">Community Activity</span>
            </div>
            <p style="font-family:var(--font-body); font-size:0.88rem; color:var(--muted); margin-bottom:0.75rem;">
                Thoughts logged by film enthusiasts across contemporary premieres and vintage classics, calibrated with AI sentiment detection.
            </p>
            """,
            unsafe_allow_html=True,
        )

        filter_col, action_col = st.columns([2.7, 1.1], gap="small", vertical_alignment="center")
        with filter_col:
            era_filter = st.pills(
                "Filter reviews by era",
                options=["All cinema", "Latest releases (2020s)", "Golden classics (Pre-2000)"],
                default="All cinema",
                label_visibility="collapsed",
                key="home_rev_era_pills",
            )
        with action_col:
            if st.button("More reviews", icon=":material/autorenew:", key="btn_cycle_home_reviews", use_container_width=True):
                st.session_state["home_reviews_offset"] = st.session_state.get("home_reviews_offset", 0) + 4
                st.rerun()

        def is_latest(rev: Dict[str, Any]) -> bool:
            try:
                y = int(str(rev.get("movie_year", "0"))[:4])
                return y >= 2020
            except Exception:
                return False

        def is_classic(rev: Dict[str, Any]) -> bool:
            try:
                y = int(str(rev.get("movie_year", "2000"))[:4])
                return 1900 <= y < 2000
            except Exception:
                return False

        if era_filter == "Latest releases (2020s)":
            filtered_reviews = [r for r in all_reviews if is_latest(r)]
        elif era_filter == "Golden classics (Pre-2000)":
            filtered_reviews = [r for r in all_reviews if is_classic(r)]
        else:
            # Interleave latest releases and timeless classics so both are prominently visible
            latest = [r for r in all_reviews if is_latest(r)]
            classics = [r for r in all_reviews if is_classic(r)]
            others = [r for r in all_reviews if r not in latest and r not in classics]
            interleaved = []
            for i in range(max(len(latest), len(classics))):
                if i < len(latest):
                    interleaved.append(latest[i])
                if i < len(classics):
                    interleaved.append(classics[i])
            interleaved.extend(others)
            filtered_reviews = interleaved

        # Dynamically rotate through reviews 4 at a time
        PAGE_REVS = 4
        total_revs = len(filtered_reviews)
        if total_revs > 0:
            rev_offset = st.session_state.get("home_reviews_offset", 0) % total_revs
            displayed_reviews = [
                filtered_reviews[(rev_offset + i) % total_revs]
                for i in range(min(PAGE_REVS, total_revs))
            ]
        else:
            displayed_reviews = []

        # Render 4 reviews in balanced 2 columns
        col_r1, col_r2 = st.columns(2, gap="medium")
        for idx, rev in enumerate(displayed_reviews):
            target_col = col_r1 if idx % 2 == 0 else col_r2
            with target_col:
                render_letterboxd_review_card(rev, key_prefix=f"home_rev_{idx}", show_film_tag=True)

