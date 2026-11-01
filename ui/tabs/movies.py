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
                # Fetch details and classify origin for top search results
                classified_results = []
                for item in raw_results[:18]:
                    m_id = item.get("id")
                    details = fetch_movie_details(m_id, api_key) if m_id else None
                    classified_results.append(normalize_and_classify_movie(item, details=details))
                movies_list = classified_results
        except Exception:
            st.warning("TMDB request failed or timed out. Please check your connection.")

        if not movies_list:
            render_empty_state(
                "No matching movies found",
                f"No films found for '{active_search}'. Check the spelling or try the original title.",
            )
            return

    elif api_key:
        # Default browse view: now_playing list classified by origin
        try:
            with st.spinner("Fetching theatrical releases..."):
                np_movies = get_movies_by_category_and_region("now_playing", "All")
                up_movies = get_movies_by_category_and_region("upcoming", "All")
                # Combine now playing and upcoming for a deep pool to cycle through
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
        selected_movie = displayed_movies[selected_idx]
    detail_col, grid_col = st.columns([1.1, 1.4], gap="large")

    with detail_col:
        st.markdown('<div class="cinesense-section-title" style="margin-top:0;">Film overview</div>', unsafe_allow_html=True)

        # Poster Image
        if selected_movie.get("poster_url"):
            st.markdown(
                f"""
                <div class="cinesense-detail-poster-wrap">
                    <img src="{selected_movie['poster_url']}" class="cinesense-detail-poster-img" alt="{selected_movie.get('title')}" loading="lazy" decoding="async" />
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="cinesense-detail-poster-wrap">
                    <div class="cinesense-poster-placeholder" style="height:100%;"><span>Film</span><span>No poster available</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Title & Year
        st.markdown(
            f'<h3 style="font-family:var(--font-heading); font-size:1.45rem; font-weight:700; color:var(--ink); margin:0.5rem 0 0.15rem 0;">'
            f'{selected_movie["title"]} <span style="font-size:1rem; font-weight:400; color:var(--muted);">({selected_movie.get("release_year", "N/A")})</span>'
            f'</h3>',
            unsafe_allow_html=True,
        )

        # Genres
        genres_badges = " ".join([f'<span class="badge-neutral">{g}</span>' for g in selected_movie.get("genres", [])])
        st.markdown(f'<div style="margin-bottom:0.75rem;">{genres_badges}</div>', unsafe_allow_html=True)

        # TMDB Audience Score (visually distinct from model outputs)
        render_html(
            f"""
            <div class="cinesense-card" style="padding: 0.65rem 0.85rem; margin-bottom: 0.85rem;">
                <div style="font-family:var(--font-mono); font-size:0.7rem; text-transform:uppercase; color:var(--muted); letter-spacing:0.04em;">
                    External Reference Metric
                </div>
                <div style="display:flex; align-items:baseline; gap:0.5rem; margin-top:0.2rem;">
                    <span style="font-family:var(--font-heading); font-size:1.35rem; font-weight:700; color:var(--ink);">
                        {selected_movie.get('audience_score', 0.0)} / 10
                    </span>
                    <span style="font-family:var(--font-body); font-size:0.85rem; color:var(--muted);">
                        TMDB audience score
                    </span>
                </div>
            </div>
            """
        )

        # Dynamic Letterboxd Watched Diary Actions (Stored persistently)
        render_letterboxd_watched_actions(selected_movie, key_prefix="mov_detail")

        # Overview synopsis
        st.markdown(
            f'<p style="font-family:var(--font-body); font-size:0.88rem; color:var(--muted); line-height:1.5; margin-bottom:1rem;">'
            f'{selected_movie.get("overview", "")}'
            f'</p>',
            unsafe_allow_html=True,
        )

        # AI Cinematic Context Profile Expander
        with st.expander("Cinematic context profile", expanded=False):
            with st.spinner("Analyzing film context & reception..."):
                movie_ctx = analyze_movie_context_cached(
                    selected_movie.get("overview", ""),
                    movie_title=selected_movie["title"],
                )
            render_context_intelligence_card(movie_ctx)

        # Experimental Disclaimer
        st.markdown(
            """
            <div class="cinesense-notice" style="margin-bottom: 1rem;">
                <strong>Notice:</strong> Results on non-IMDB text are experimental.
                Models were calibrated on Stanford IMDB long-form reviews; contemporary social media or
                short-form ratings may exhibit domain shifts.
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Primary Action Button: Review this film
        if st.button("Review this film", type="primary", use_container_width=True, key="btn_review_this_film"):
            select_movie_and_open_analyzer(selected_movie)

    with grid_col:
        subtab_browse, subtab_diary = st.tabs(["Browse titles", "Watched diary"])

        with subtab_browse:
            # Header with film count, Next 9, and Shuffle buttons
            hdr_c1, hdr_c2, hdr_c3 = st.columns([1.8, 1.1, 1.1], gap="small", vertical_alignment="center")
            with hdr_c1:
                if not active_search and total_available > PAGE_SIZE:
                    batch_num = (st.session_state.get("movies_browse_offset", 0) // PAGE_SIZE) % max(1, (total_available + PAGE_SIZE - 1) // PAGE_SIZE) + 1
                    total_batches = max(1, (total_available + PAGE_SIZE - 1) // PAGE_SIZE)
                    st.markdown(
                        f'<div class="cinesense-takeaway" style="margin:0;">Showing <strong>9</strong> featured films &bull; Batch {batch_num} of {total_batches}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="cinesense-takeaway" style="margin:0;">Showing top <strong>{len(displayed_movies)}</strong> films</div>',
                        unsafe_allow_html=True,
                    )

            with hdr_c2:
                if not active_search and total_available > PAGE_SIZE:
                    if st.button("Next 9 ↻", icon=":material/autorenew:", key="btn_cycle_titles", use_container_width=True):
                        st.session_state["movies_browse_offset"] = (st.session_state.get("movies_browse_offset", 0) + PAGE_SIZE) % total_available
                        st.session_state["selected_movie_idx"] = 0
                        st.session_state["selected_movie_data"] = None
                        st.rerun()

            with hdr_c3:
                if not active_search and total_available > PAGE_SIZE:
                    if st.button("Shuffle 🔀", icon=":material/shuffle:", key="btn_shuffle_titles", use_container_width=True):
                        st.session_state["movies_browse_offset"] = random.randint(0, max(0, total_available - 1))
                        st.session_state["selected_movie_idx"] = 0
                        st.session_state["selected_movie_data"] = None
                        st.rerun()

            st.write("")

            # Exactly 3x3 poster grid (9 movies)
            n_cols = 3
            rows = [displayed_movies[i : i + n_cols] for i in range(0, len(displayed_movies), n_cols)]
            for row_idx, row in enumerate(rows):
                grid_cols = st.columns(n_cols)
                for col_idx, movie in enumerate(row):
                    actual_idx = row_idx * n_cols + col_idx
                    with grid_cols[col_idx]:
                        m_title = movie.get("title", "Untitled")
                        m_score = movie.get("audience_score", 0.0)
                        m_year = movie.get("release_year") or "N/A"
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

                        is_active_card = (actual_idx == selected_idx) or (movie.get("id") == selected_movie.get("id"))
                        active_style = "border: 2px solid var(--accent); box-shadow: 0 0 8px rgba(210, 153, 34, 0.25);" if is_active_card else ""

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
                                    <div class="cinesense-film-meta">
                                        <span class="cinesense-film-date">{m_year}</span>
                                    </div>
                                </div>
                            </div>
                            """
                        )
                        btn_label = "Inspecting" if is_active_card else "Inspect film"
                        if st.button(btn_label, key=f"sel_mov_{actual_idx}", use_container_width=True):
                            st.session_state["selected_movie_idx"] = actual_idx
                            st.session_state["selected_movie_data"] = movie
                            st.rerun()
                        st.write("")

            # Bottom pagination controls to easily refresh or step through batches
            if not active_search and total_available > PAGE_SIZE:
                st.markdown('<div style="margin-top:0.5rem; border-top:1px solid var(--line); padding-top:0.75rem;"></div>', unsafe_allow_html=True)
                pg_c1, pg_c2, pg_c3 = st.columns([1.2, 1.6, 1.2], gap="small", vertical_alignment="center")
                with pg_c1:
                    if st.button("⬅ Previous 9", key="btn_prev_movies", use_container_width=True):
                        st.session_state["movies_browse_offset"] = (st.session_state.get("movies_browse_offset", 0) - PAGE_SIZE) % total_available
                        st.session_state["selected_movie_idx"] = 0
                        st.session_state["selected_movie_data"] = None
                        st.rerun()
                with pg_c2:
                    st.markdown(
                        f'<div style="text-align:center; font-family:var(--font-mono); font-size:0.78rem; color:var(--muted); line-height:2.2;">'
                        f'Batch {batch_num} of {total_batches} &bull; {total_available} titles'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                with pg_c3:
                    if st.button("Next 9 ➔", key="btn_next_movies", use_container_width=True):
                        st.session_state["movies_browse_offset"] = (st.session_state.get("movies_browse_offset", 0) + PAGE_SIZE) % total_available
                        st.session_state["selected_movie_idx"] = 0
                        st.session_state["selected_movie_data"] = None
                        st.rerun()

        with subtab_diary:
            render_watched_movies_grid()

    # Full Letterboxd-Style Community Reviews and Discussion Section
    st.markdown('<div style="margin-top:2.5rem; border-top:1px solid var(--line); padding-top:1.5rem;"></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="cinesense-section-title" style="margin-bottom:0.35rem;">Community Reviews & Discussions</div>',
        unsafe_allow_html=True,
    )
    render_letterboxd_reviews_section(selected_movie, allow_compose=True)

