"""
Movies Tab for CineSense.
Enables browsing and searching films using the TMDB API (metadata and posters only).
Displays poster grid, detail panel with TMDB audience score (visually separate from model metrics),
origin badge with explanatory title, experimental non-IMDB text notice,
and a 'Review this film' action that loads the film context into the analyzer with an empty, focused textarea.
"""

from typing import Any, Dict, List, Optional
import random
import streamlit as st

from services.llm_context_service import analyze_movie_context_cached
from services.tmdb_service import (
    fetch_movie_details,
    get_movies_by_category_and_region,
    get_tmdb_api_key,
    normalize_and_classify_movie,
    search_tmdb_movies,
)
from services.review_storage_service import is_movie_watched
from ui.components import (
    render_context_intelligence_card,
    render_empty_state,
    render_html,
    render_letterboxd_reviews_section,
    render_letterboxd_watched_actions,
    render_watched_movies_grid,
    set_active_tab,
)


def select_movie_and_open_analyzer(movie: Dict[str, Any]) -> None:
    """
    Select a film, write its ID to query parameters, clear any prior review text/results,
    switch to the Analyzer tab, and focus the empty textarea.
    """
    movie_id = movie.get("id")
    prev_selected = st.session_state.get("selected_movie")
    prev_id = prev_selected.get("id") if prev_selected else None

    # Clear textarea and previous results if film changes
    if prev_id != movie_id:
        st.session_state["review_text_input"] = ""
        st.session_state["has_run_analysis"] = False
        st.session_state["analyzer_textarea"] = ""
        if "previous_result" in st.session_state:
            st.session_state["previous_result"] = None

    origin_label = movie.get("origin_label", movie.get("origin_badge", "Unclassified"))
    origin_reason = movie.get("origin_reason", movie.get("origin_badge_title", f"{origin_label} film"))

    selected_obj = {
        "id": movie_id,
        "title": movie.get("title", "Untitled"),
        "year": movie.get("release_year") or (movie.get("release_date") or "")[:4] or "N/A",
        "poster": movie.get("poster_url", ""),
        "origin_badge": origin_label,
        "origin_badge_title": origin_reason,
    }
    st.session_state["selected_movie"] = selected_obj

    # Update recent films row (up to 5 films, no duplicates, most recent first)
    recent = st.session_state.get("recent_movies", [])
    recent = [m for m in recent if m.get("id") != movie_id]
    recent.insert(0, selected_obj)
    st.session_state["recent_movies"] = recent[:5]

    # Write movie ID to query params
    if movie_id:
        st.query_params["movie"] = str(movie_id)

    # Focus textarea on next render
    st.session_state["focus_analyzer_textarea"] = True

    # Switch to Analyzer tab
    set_active_tab("Analyzer")
    st.rerun()


def render_movies_tab() -> None:
    st.markdown(
        '<p class="cinesense-takeaway" style="font-size:1.05rem; color:var(--ink); margin-bottom: 1.25rem;">'
        'Explore film metadata and posters from The Movie Database (TMDB). Select any film to inspect details and write a review in the analyzer.'
        '</p>',
        unsafe_allow_html=True,
    )

    api_key = get_tmdb_api_key()

    if not api_key:
        st.markdown(
            """
            <div class="cinesense-notice" style="margin-bottom: 1.25rem;">
                <strong>TMDB API key not configured.</strong> Live film search and browsing require an API key.<br />
                To enable live title search across TMDB's full library, add your key to
                <code>.streamlit/secrets.toml</code>:<br />
                <code>TMDB_API_KEY = "your_tmdb_api_key"</code>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Search Bar (wrapped in form so it searches on Enter or Search click, never every keystroke)
    with st.form("movies_search_form", clear_on_submit=False):
        fcol1, fcol2 = st.columns([5, 1])
        with fcol1:
            search_query = st.text_input(
                "Search movies",
                placeholder="Search for a film title (e.g. Inception, Jawan, Parasite)...",
                label_visibility="collapsed",
            )
        with fcol2:
            search_submitted = st.form_submit_button("Search", use_container_width=True)

    # Fetch or filter movies
    movies_list: List[Dict[str, Any]] = []
    active_search = search_query.strip()

    if api_key and active_search:
        try:
            with st.spinner("Querying TMDB API..."):
                raw_results = search_tmdb_movies(active_search, api_key)
                # Normalize and classify origin directly from search items without blocking on N+1 network lookups
                movies_list = [
                    normalize_and_classify_movie(item) for item in raw_results[:18]
                ]
        except Exception:
            st.warning("TMDB request failed or timed out. Please check your connection.")

        if not movies_list:
            render_empty_state(
                "No matching movies found",
                f"No films found for '{active_search}'. Check the spelling or try the original title.",
            )
            return

    elif api_key:
        # Default browse view: filter by theatrical category and origin region
        try:
            with st.spinner("Fetching theatrical releases..."):
                cat_filter = st.session_state.get("movies_browse_category") or "In theatres now (latest)"
                reg_filter = st.session_state.get("movies_browse_region") or "All"

                if cat_filter == "In theatres now (latest)":
                    movies_list = get_movies_by_category_and_region("now_playing", reg_filter)
                elif cat_filter == "Coming soon":
                    movies_list = get_movies_by_category_and_region("upcoming", reg_filter)
                else:  # "All featured"
                    np_movies = get_movies_by_category_and_region("now_playing", reg_filter)
                    up_movies = get_movies_by_category_and_region("upcoming", reg_filter)
                    seen_ids = set()
                    combined = []
                    for m in np_movies + up_movies:
                        if m.get("id") not in seen_ids:
                            seen_ids.add(m.get("id"))
                            combined.append(m)
                    movies_list = combined if combined else np_movies
        except Exception:
            movies_list = []

    # Display exactly 9 movies at a time, cycling as the user clicks the Movies tab
    PAGE_SIZE = 9
    total_available = len(movies_list)

    if not active_search and total_available > 0:
        browse_offset = st.session_state.get("movies_browse_offset", 0) % total_available
        displayed_movies = []
        for i in range(min(PAGE_SIZE, total_available)):
            idx = (browse_offset + i) % total_available
            displayed_movies.append(movies_list[idx])
    else:
        displayed_movies = movies_list[:PAGE_SIZE]

    # Check if a specific movie was selected from Home tab or another source
    selected_movie_data = st.session_state.get("selected_movie_data")
    if selected_movie_data:
        matched_idx = next((i for i, m in enumerate(displayed_movies) if m.get("id") == selected_movie_data.get("id")), None)
        if matched_idx is not None:
            selected_idx = matched_idx
            selected_movie = displayed_movies[selected_idx]
        else:
            selected_idx = 0
            selected_movie = selected_movie_data
    else:
        selected_idx = st.session_state.get("selected_movie_idx", 0)
        if selected_idx >= len(displayed_movies):
            selected_idx = 0
        selected_movie = displayed_movies[selected_idx] if displayed_movies else None

    # Top-level tabs: Browse films vs. Watched diary
    tab_browse, tab_diary = st.tabs(["Browse featured films", "Watched diary"])

    with tab_browse:
        # 1. Cinema Spotlight Hero Card (full width, no column mismatch)
        if selected_movie:
            st.markdown(
                '<div style="font-family:var(--font-mono); font-size:0.75rem; text-transform:uppercase; color:var(--muted); letter-spacing:0.04em; margin-bottom:0.4rem;">'
                'Spotlight film overview'
                '</div>',
                unsafe_allow_html=True,
            )
            hero_col_poster, hero_col_info = st.columns([1, 2.7], gap="medium")

            with hero_col_poster:
                m_poster = selected_movie.get("poster_url") or selected_movie.get("poster", "")
                if m_poster:
                    st.markdown(
                        f"""
                        <div class="cinesense-detail-poster-wrap" style="width:100%; max-width:240px; margin-bottom:0.5rem;">
                            <img src="{m_poster}" class="cinesense-detail-poster-img" alt="{selected_movie.get('title')}" loading="lazy" decoding="async" />
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        """
                        <div class="cinesense-detail-poster-wrap" style="width:100%; max-width:240px; margin-bottom:0.5rem;">
                            <div class="cinesense-poster-placeholder" style="height:100%;"><span>Film</span><span>No poster</span></div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with hero_col_info:
                # Title, Year, Origin Badge
                origin_lbl = selected_movie.get("origin_badge", selected_movie.get("origin_label", "Cinema"))
                origin_desc = selected_movie.get("origin_badge_title", selected_movie.get("origin_reason", f"{origin_lbl} film"))
                badge_markup = f'<span class="cinesense-spotlight-pill" title="{origin_desc}">{origin_lbl}</span>'

                st.markdown(
                    f'<div style="display:flex; align-items:baseline; gap:0.6rem; flex-wrap:wrap; margin-bottom:0.25rem;">'
                    f'<h3 style="font-family:var(--font-heading); font-size:1.55rem; font-weight:700; color:var(--ink); margin:0;">'
                    f'{selected_movie.get("title", "Untitled")}'
                    f'</h3>'
                    f'<span style="font-family:var(--font-mono); font-size:0.95rem; color:var(--muted);">({selected_movie.get("release_year") or (selected_movie.get("release_date") or "")[:4] or "N/A"})</span>'
                    f'{badge_markup}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                # Genres
                genres_badges = " ".join([f'<span class="badge-neutral" style="font-size:0.75rem;">{g}</span>' for g in selected_movie.get("genres", [])])
                if genres_badges:
                    st.markdown(f'<div style="margin-bottom:0.6rem;">{genres_badges}</div>', unsafe_allow_html=True)

                # TMDB Audience Score Metric
                render_html(
                    f"""
                    <div class="cinesense-card" style="padding: 0.55rem 0.85rem; margin-bottom: 0.75rem; display:inline-block;">
                        <div style="font-family:var(--font-mono); font-size:0.68rem; text-transform:uppercase; color:var(--muted); letter-spacing:0.04em;">
                            External Reference Metric
                        </div>
                        <div style="display:flex; align-items:baseline; gap:0.45rem; margin-top:0.15rem;">
                            <span style="font-family:var(--font-heading); font-size:1.25rem; font-weight:700; color:var(--ink);">
                                ★ {selected_movie.get('audience_score', 0.0):.1f} / 10
                            </span>
                            <span style="font-family:var(--font-body); font-size:0.8rem; color:var(--muted);">
                                TMDB audience score
                            </span>
                        </div>
                    </div>
                    """
                )

                # Letterboxd Watched Diary Actions
                render_letterboxd_watched_actions(selected_movie, key_prefix="mov_detail", show_status_bar=True)

                # Synopsis
                synopsis = selected_movie.get("overview", "")
                if synopsis:
                    st.markdown(
                        f'<p style="font-family:var(--font-body); font-size:0.88rem; color:var(--muted); line-height:1.5; margin: 0.5rem 0 0.85rem 0;">'
                        f'{synopsis}'
                        f'</p>',
                        unsafe_allow_html=True,
                    )

                # Action Button: Review this film
                if st.button("Review this film in Analyzer ➔", type="primary", key="btn_review_this_film"):
                    select_movie_and_open_analyzer(selected_movie)

                # Cinematic Context Profile
                with st.expander("Cinematic context & nuance profile", expanded=False):
                    with st.spinner("Analyzing film context & reception..."):
                        movie_ctx = analyze_movie_context_cached(
                            selected_movie.get("overview", ""),
                            movie_title=selected_movie.get("title", ""),
                        )
                    render_context_intelligence_card(movie_ctx)
                    st.markdown(
                        """
                        <div class="cinesense-notice" style="margin-top: 0.6rem; margin-bottom: 0;">
                            <strong>Notice:</strong> Results on non-IMDB text are experimental.
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown('<div style="margin: 1.5rem 0; border-top: 1px solid var(--line);"></div>', unsafe_allow_html=True)

        # 2. Featured Cinema Releases (Full-width 3x3 grid — 9 films total)
        st.markdown(
            f'<div class="cinesense-section-title" style="margin-top:0; margin-bottom:0.25rem;">'
            f'Featured cinema releases <span style="font-size:0.85rem; font-weight:400; color:var(--muted); margin-left:0.4rem;">({total_available} titles available)</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="font-family:var(--font-body); font-size:0.85rem; color:var(--muted); margin-bottom:0.85rem;">'
            'Browse current and upcoming theatrical titles sorted by latest release date. Select "Inspect" to spotlight any title above, or "Review" to load it into the sentiment analyzer.'
            '</p>',
            unsafe_allow_html=True,
        )

        if not active_search:
            ctrl_c1, ctrl_c2, ctrl_c3 = st.columns([2.8, 1.8, 1.4], gap="small", vertical_alignment="center")
            with ctrl_c1:
                st.pills(
                    "Browse category",
                    options=["In theatres now (latest)", "Coming soon", "All featured"],
                    default="In theatres now (latest)",
                    label_visibility="collapsed",
                    key="movies_browse_category",
                )
            with ctrl_c2:
                st.pills(
                    "Browse region",
                    options=["All", "Hollywood", "Indian"],
                    default="All",
                    label_visibility="collapsed",
                    key="movies_browse_region",
                )
            with ctrl_c3:
                btn_m1, btn_m2 = st.columns(2, gap="small")
                with btn_m1:
                    if st.button("More ↻", icon=":material/autorenew:", key="btn_cycle_movies", use_container_width=True, help="Cycle next 9 films"):
                        st.session_state["movies_browse_offset"] = st.session_state.get("movies_browse_offset", 0) + PAGE_SIZE
                        st.rerun()
                with btn_m2:
                    if st.button("Sync", icon=":material/refresh:", key="btn_refresh_movies", use_container_width=True, help="Force refresh latest theatrical releases from TMDB"):
                        st.cache_data.clear()
                        st.rerun()

        n_cols = 3
        rows = [displayed_movies[i : i + n_cols] for i in range(0, len(displayed_movies), n_cols)]
        for row_idx, row in enumerate(rows):
            grid_cols = st.columns(n_cols, gap="medium")
            for col_idx, movie in enumerate(row):
                actual_idx = row_idx * n_cols + col_idx
                with grid_cols[col_idx]:
                    m_title = movie.get("title", "Untitled")
                    m_score = movie.get("audience_score", 0.0)
                    m_year = movie.get("release_year") or "N/A"
                    m_date = movie.get("formatted_date") or m_year
                    m_origin = movie.get("origin_label", movie.get("origin_badge", ""))
                    m_poster = movie.get("poster_url", "")
                    m_watched = is_movie_watched(movie.get("id"), m_title)
                    watched_badge = (
                        '<div class="cinesense-watched-poster-badge"><span style="font-weight:700;">✓</span> Watched</div>'
                        if m_watched
                        else ""
                    )
                    m_img = (
                        f'<img src="{m_poster}" class="cinesense-poster-img" alt="{m_title}" loading="lazy" decoding="async" />'
                        if m_poster
                        else '<div class="cinesense-poster-placeholder"><span>Film</span><span>No Poster</span></div>'
                    )

                    is_active_card = selected_movie and (
                        (movie.get("id") and movie.get("id") == selected_movie.get("id"))
                        or (actual_idx == selected_idx)
                    )
                    active_style = "border: 2px solid var(--accent); box-shadow: 0 0 10px rgba(210, 153, 34, 0.28);" if is_active_card else ""

                    badge_tag = f'<span class="badge-neutral" style="font-size:0.68rem; padding:1px 6px;">{m_origin}</span>' if m_origin else ''

                    render_html(
                        f"""
                        <div class="cinesense-film-card" style="{active_style}">
                            <div class="cinesense-poster-frame">
                                {m_img}
                                {watched_badge}
                                <div class="cinesense-poster-gradient"></div>
                                <div class="cinesense-poster-badge-wrap">
                                    <span class="cinesense-score-pill"><span style="color:var(--accent);">★</span> {m_score:.1f}</span>
                                </div>
                            </div>
                            <div class="cinesense-card-content">
                                <div class="cinesense-film-title" title="{m_title}">{m_title}</div>
                                <div class="cinesense-film-meta" style="display:flex; justify-content:space-between; align-items:center;">
                                    <span class="cinesense-film-date">{m_date}</span>
                                    {badge_tag}
                                </div>
                            </div>
                        </div>
                        """
                    )

                    btn_c1, btn_c2 = st.columns([1, 1], gap="small")
                    with btn_c1:
                        btn_label = "Spotlighted" if is_active_card else "Inspect"
                        if st.button(btn_label, key=f"sel_mov_{actual_idx}", use_container_width=True):
                            st.session_state["selected_movie_idx"] = actual_idx
                            st.session_state["selected_movie_data"] = movie
                            st.rerun()
                    with btn_c2:
                        if st.button("Review ➔", key=f"rev_mov_{actual_idx}", use_container_width=True):
                            select_movie_and_open_analyzer(movie)
                    st.write("")

    with tab_diary:
        render_watched_movies_grid()

    # Full Letterboxd-Style Community Reviews and Discussion Section
    st.markdown('<div style="margin-top:2.5rem; border-top:1px solid var(--line); padding-top:1.5rem;"></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="cinesense-section-title" style="margin-bottom:0.35rem;">Community Reviews & Discussions</div>',
        unsafe_allow_html=True,
    )
    render_letterboxd_reviews_section(selected_movie, allow_compose=True)

