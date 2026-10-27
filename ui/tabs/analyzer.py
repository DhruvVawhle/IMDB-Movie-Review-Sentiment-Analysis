"""
Analyze a Review Tab for CineSense.
Supports model evaluation for any text with optional film context grounding.
Enables choosing any film via TMDB search, film strip with change/clear actions,
recent films navigation, session review history, and deep explainability (LIME).
"""

from typing import Any, Dict, List, Optional
import streamlit as st
import streamlit.components.v1 as st_components

from services.explainability_service import (
    EXPLANATION_DISCLAIMER,
    generate_highlighted_html,
    get_lime_explanation_cached,
)
from services.llm_context_service import analyze_movie_context_cached
from services.prediction_service import (
    compare_all_models,
    get_available_models_list,
    predict_sentiment,
    validate_review_input,
)
from services.tmdb_service import (
    fetch_movie_details,
    get_tmdb_api_key,
    normalize_and_classify_movie,
    search_tmdb_movies,
)
from ui.components import (
    plot_lime_feature_bars,
    plot_probability_meter,
    render_context_intelligence_card,
    render_empty_state,
    set_active_tab,
)

PRESET_REVIEWS = {
    "Rave Review": (
        "A truly remarkable cinematic achievement. The direction is flawless, the performances are deeply "
        "affecting, and the emotional resonance lingered long after the credits rolled. Easily one of the finest films of the decade."
    ),
    "Critical Pan": (
        "A colossal waste of time and talent. The screenplay is disjointed and filled with tired cliches, the pacing drags "
        "aimlessly, and the dialogue feels insultingly artificial. Terribly disappointing from start to finish."
    ),
    "Nuanced Mixed": (
        "Visually striking with gorgeous cinematography and solid practical effects, but unfortunately hampered by a weak "
        "and predictable second act. Worth a watch for film enthusiasts, but far from a masterpiece."
    ),
    "Short Remark": (
        "Decent Saturday evening popcorn movie. Fun action scenes, though nothing memorable."
    ),
}


def _select_film_for_analyzer(movie_obj: Dict[str, Any]) -> None:
    """Set selected movie, sync query params, clear textarea and prior result, and focus textarea."""
    prev = st.session_state.get("selected_movie")
    new_id = movie_obj.get("id")
    prev_id = prev.get("id") if prev else None

    if prev_id != new_id:
        st.session_state["review_text_input"] = ""
        st.session_state["analyzer_textarea"] = ""
        st.session_state["has_run_analysis"] = False

    st.session_state["selected_movie"] = movie_obj
    st.session_state["show_analyzer_film_search"] = False
    st.session_state["focus_analyzer_textarea"] = True

    if new_id:
        st.query_params["movie"] = str(new_id)

    # Update recent films (last 5, deduplicated, no emoji)
    recent = st.session_state.get("recent_movies", [])
    recent = [m for m in recent if m.get("id") != new_id]
    recent.insert(0, movie_obj)
    st.session_state["recent_movies"] = recent[:5]


def _clear_selected_film() -> None:
    """Remove film context, remove movie query param, clear textarea and result."""
    st.session_state["selected_movie"] = None
    st.session_state["show_analyzer_film_search"] = False
    st.session_state["review_text_input"] = ""
    st.session_state["analyzer_textarea"] = ""
    st.session_state["has_run_analysis"] = False
    if "movie" in st.query_params:
        del st.query_params["movie"]


def render_analyzer_tab() -> None:
    api_key = get_tmdb_api_key()

    # 1. Sync shared links: ?tab=analyzer&movie=<id>
    movie_param = st.query_params.get("movie")
    curr_selected = st.session_state.get("selected_movie")
    if movie_param:
        try:
            param_id = int(movie_param)
            if not curr_selected or curr_selected.get("id") != param_id:
                if api_key:
                    details = fetch_movie_details(param_id, api_key)
                    if details:
                        norm = normalize_and_classify_movie(details, details)
                        loaded_film = {
                            "id": norm["id"],
                            "title": norm["title"],
                            "year": norm["release_year"],
                            "poster": norm["poster_url"],
                            "origin_badge": norm["origin_badge"],
                            "origin_badge_title": norm["origin_badge_title"],
                        }
                        _select_film_for_analyzer(loaded_film)
                        curr_selected = loaded_film
        except Exception:
            pass

    st.markdown(
        '<p class="cinesense-takeaway" style="font-size:1.05rem; color:var(--ink); margin-bottom: 1.25rem;">'
        'Test individual movie reviews through trained models. Pick an algorithm or compare all three simultaneously.'
        '</p>',
        unsafe_allow_html=True,
    )

    available_models = get_available_models_list()
    valid_models = {m["id"]: m["name"] for m in available_models if m.get("available")}

    if not valid_models:
        st.error("No trained models are currently available. Please ensure model files exist in models/.")
        return

    # Two-column layout: Input & Controls (Left), Result Panel (Right)
    col_input, col_result = st.columns([1.1, 1.0], gap="large")

    selected_movie = st.session_state.get("selected_movie")

    with col_input:
        st.markdown('<div class="cinesense-section-title" style="margin-top:0;">Input review</div>', unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # TMDB Film Context (Optional): Search, Film Strip & Recent Films
        # ---------------------------------------------------------------------
        if not api_key:
            st.markdown(
                """
                <div class="cinesense-notice" style="margin-bottom: 0.85rem; font-size: 0.82rem;">
                    <strong>TMDB API key not configured.</strong> Film search is unavailable. To attach film context, add your key to
                    <code>.streamlit/secrets.toml</code>:<br />
                    <code>TMDB_API_KEY = "your_tmdb_api_key"</code><br />
                    The Analyzer continues to work normally for any review text without a film selected.
                </div>
                """,
                unsafe_allow_html=True,
            )

        show_search = st.session_state.get("show_analyzer_film_search", False) or (selected_movie is None)

        if selected_movie and not st.session_state.get("show_analyzer_film_search", False):
            # Render Selected Film Strip
            poster_url = selected_movie.get("poster")
            title = selected_movie.get("title", "Untitled")
            year = selected_movie.get("year", "N/A")

            thumb_html = (
                f'<img src="{poster_url}" class="cinesense-film-strip-thumb" alt="{title}" />'
                if poster_url
                else '<div class="cinesense-film-strip-thumb-placeholder">🎬</div>'
            )

            strip_html = f"""
            <div class="cinesense-film-strip-card">
                <div class="cinesense-film-strip-info">
                    {thumb_html}
                    <div>
                        <span class="cinesense-film-strip-title">{title}</span>
                        <span class="cinesense-film-strip-year">({year})</span>
                    </div>
                </div>
            </div>
            """
            st.markdown(strip_html, unsafe_allow_html=True)

            act_col1, act_col2 = st.columns([1, 1])
            with act_col1:
                if st.button("Change film", key="strip_change_film", use_container_width=True):
                    st.session_state["show_analyzer_film_search"] = True
                    st.rerun()
            with act_col2:
                if st.button("Clear film", key="strip_clear_film", use_container_width=True):
                    _clear_selected_film()
                    st.rerun()

        elif api_key:
            # Render "Choose a film" Search Box
            with st.form("analyzer_movie_search_form", clear_on_submit=False):
                st.markdown(
                    '<div style="font-family:var(--font-mono); font-size:0.75rem; text-transform:uppercase; color:var(--muted); margin-bottom:0.25rem;">'
                    'Choose a film (optional context)'
                    '</div>',
                    unsafe_allow_html=True,
                )
                scol1, scol2 = st.columns([4, 1])
                with scol1:
                    search_query = st.text_input(
                        "Choose a film",
                        placeholder="Search TMDB for any film (e.g. Inception, RRR, Parasite)...",
                        label_visibility="collapsed",
                    )
                with scol2:
                    search_btn = st.form_submit_button("Search", use_container_width=True)

            if search_btn or st.session_state.get("analyzer_last_search"):
                active_q = search_query.strip() if search_btn else st.session_state.get("analyzer_last_search", "")
                if search_btn:
                    st.session_state["analyzer_last_search"] = active_q

                if active_q:
                    with st.spinner("Searching TMDB..."):
                        try:
                            raw_results = search_tmdb_movies(active_q, api_key)
                        except Exception:
                            st.warning("TMDB request failed or timed out.")
                            raw_results = []

                    if not raw_results:
                        st.info(f"No films found for '{active_q}'. Check the spelling or try the original title.")
                    else:
                        st.markdown(
                            '<div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--muted); margin:0.35rem 0;">'
                            'Select a film below:'
                            '</div>',
                            unsafe_allow_html=True,
                        )
                        # Show up to 8 compact rows
                        for idx, item in enumerate(raw_results[:8]):
                            m_id = item.get("id")
                            details = fetch_movie_details(m_id, api_key) if m_id else None
                            norm = normalize_and_classify_movie(item, details=details)

                            r_title = norm["title"]
                            r_year = norm["release_year"]
                            r_poster = norm["poster_url"]

                            row_thumb_html = (
                                f'<img src="{r_poster}" class="cinesense-search-thumb" alt="{r_title}" />'
                                if r_poster
                                else '<div class="cinesense-search-thumb-placeholder">🎬</div>'
                            )

                            r_col_info, r_col_btn = st.columns([4.2, 1.2])
                            with r_col_info:
                                st.markdown(
                                    f"""
                                    <div class="cinesense-search-row">
                                        <div class="cinesense-search-row-left">
                                            {row_thumb_html}
                                            <div>
                                                <div class="cinesense-search-row-title">{r_title}</div>
                                                <div class="cinesense-search-row-meta">
                                                    <span>{r_year}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                            with r_col_btn:
                                if st.button("Select", key=f"sel_search_res_{m_id}_{idx}", use_container_width=True):
                                    selected_film_data = {
                                        "id": norm["id"],
                                        "title": r_title,
                                        "year": r_year,
                                        "poster": r_poster,
                                        "origin_badge": r_badge,
                                        "origin_badge_title": r_reason,
                                    }
                                    _select_film_for_analyzer(selected_film_data)
                                    st.session_state["analyzer_last_search"] = ""
                                    st.rerun()

            if selected_movie and st.session_state.get("show_analyzer_film_search", False):
                if st.button("Cancel search", key="cancel_film_search"):
                    st.session_state["show_analyzer_film_search"] = False
                    st.rerun()

        # ---------------------------------------------------------------------
        # Recent Films Row (Session-only, last 5, no emoji)
        # ---------------------------------------------------------------------
        recent_films = st.session_state.get("recent_movies", [])
        if recent_films:
            st.markdown(
                '<div style="font-family:var(--font-mono); font-size:0.75rem; text-transform:uppercase; color:var(--muted); margin:0.6rem 0 0.25rem 0;">'
                'Recent films'
                '</div>',
                unsafe_allow_html=True,
            )
            rec_cols = st.columns(len(recent_films))
            for r_idx, r_movie in enumerate(recent_films):
                with rec_cols[r_idx]:
                    r_label = f"{r_movie['title']} ({r_movie['year']})"
                    if st.button(r_label, key=f"recent_btn_{r_movie.get('id', r_idx)}_{r_idx}", use_container_width=True):
                        _select_film_for_analyzer(r_movie)
                        st.rerun()

        # ---------------------------------------------------------------------
        # Model selector & Compare Mode
        # ---------------------------------------------------------------------
        model_keys = list(valid_models.keys())
        default_model = "logistic_regression" if "logistic_regression" in model_keys else model_keys[0]

        st.markdown(
            '<div style="font-family:var(--font-mono); font-size:0.75rem; text-transform:uppercase; color:var(--muted); margin:0.85rem 0 0.25rem 0;">'
            'Model Architecture'
            '</div>',
            unsafe_allow_html=True,
        )
        if hasattr(st, "segmented_control"):
            selected_model_id = st.segmented_control(
                "Model",
                options=model_keys,
                format_func=lambda k: valid_models[k],
                default=default_model,
                label_visibility="collapsed",
            )
            if not selected_model_id:
                selected_model_id = default_model
        else:
            selected_model_id = st.radio(
                "Model",
                options=model_keys,
                format_func=lambda k: valid_models[k],
                index=model_keys.index(default_model),
                horizontal=True,
                label_visibility="collapsed",
            )

        compare_mode = st.toggle("Compare all three models", value=False)

        # Example chips
        st.markdown(
            '<div style="font-family:var(--font-mono); font-size:0.75rem; text-transform:uppercase; color:var(--muted); margin:0.5rem 0 0.25rem 0;">'
            'Sample reviews'
            '</div>',
            unsafe_allow_html=True,
        )
        chip_cols = st.columns(len(PRESET_REVIEWS))
        for idx, (label, text) in enumerate(PRESET_REVIEWS.items()):
            with chip_cols[idx]:
                if st.button(label, key=f"chip_{idx}", use_container_width=True):
                    st.session_state["review_text_input"] = text
                    st.session_state["has_run_analysis"] = True
                    st.rerun()

        # ---------------------------------------------------------------------
        # Textarea with Contextual Label
        # ---------------------------------------------------------------------
        if selected_movie:
            textarea_label = f"Reviewing: {selected_movie['title']} ({selected_movie['year']})"
        else:
            textarea_label = "Review text"

        st.markdown(
            f'<div style="font-family:var(--font-heading); font-size:0.95rem; font-weight:600; color:var(--ink); margin:0.85rem 0 0.25rem 0;">{textarea_label}</div>',
            unsafe_allow_html=True,
        )

        current_text = st.session_state.get("review_text_input", "")
        review_input = st.text_area(
            textarea_label,
            value=current_text,
            height=165,
            placeholder="Type or paste any movie review here...",
            label_visibility="collapsed",
            key="analyzer_textarea",
        )

        # Telemetry counters
        raw_words = len(review_input.split())
        raw_chars = len(review_input)
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:-0.4rem; margin-bottom:0.75rem;">
                <span style="font-family:var(--font-body); font-size:0.8rem; color:var(--muted);">
                    Predictions run on demand when you press Analyze.
                </span>
                <span style="font-family:var(--font-mono); font-size:0.78rem; color:var(--muted);">
                    {raw_words:,} words | {raw_chars:,} chars
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Action Buttons
        btn_col1, btn_col2 = st.columns([1.5, 1])
        with btn_col1:
            analyze_btn = st.button("Analyze Review", type="primary", use_container_width=True)
        with btn_col2:
            if st.button("Clear text", use_container_width=True):
                st.session_state["review_text_input"] = ""
                st.session_state["has_run_analysis"] = False
                st.rerun()

        # JavaScript to focus textarea if requested
        if st.session_state.get("focus_analyzer_textarea", False):
            st.session_state["focus_analyzer_textarea"] = False
            focus_script = """
            <script>
            setTimeout(function() {
                const doc = window.parent.document;
                if (!doc) return;
                const ta = doc.querySelector('textarea[data-testid="stTextArea"], textarea');
                if (ta) {
                    ta.focus();
                    ta.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }, 150);
            </script>
            """
            st_components.html(focus_script, height=0, width=0)

    # -------------------------------------------------------------------------
    # Evaluation Logic
    # -------------------------------------------------------------------------
    should_evaluate = False
    if analyze_btn:
        st.session_state["review_text_input"] = review_input
        st.session_state["has_run_analysis"] = True
        should_evaluate = True
    elif st.session_state.get("has_run_analysis", False) and review_input.strip():
        should_evaluate = True

    with col_result:
        # Results panel title: 'Result for {title}' when a film is selected
        if selected_movie:
            panel_title = f"Result for {selected_movie['title']}"
        else:
            panel_title = "Model evaluation"

        st.markdown(
            f'<div class="cinesense-section-title" style="margin-top:0;">{panel_title}</div>',
            unsafe_allow_html=True,
        )

        if not should_evaluate or not review_input.strip():
            render_empty_state(
                "Ready to analyze review",
                "Paste or type a movie review on the left, choose a model, and click Analyze Review to inspect sentiment classification and active feature attribution.",
            )
            # Render Session Review History if entries exist for this film
            _render_session_history_block(selected_movie)
            return

        is_valid, err_msg = validate_review_input(review_input)
        if not is_valid:
            st.warning(err_msg)
            _render_session_history_block(selected_movie)
            return

        if compare_mode:
            # Multi-model comparative panel (only review_input sent to model)
            comp_res = compare_all_models(review_input)
            if not comp_res.get("success"):
                st.error(comp_res.get("error", "Comparison failed."))
                return

            st.markdown(
                '<div class="cinesense-takeaway">Predictions generated across Logistic Regression, Naive Bayes, and BiLSTM architectures.</div>',
                unsafe_allow_html=True,
            )

            results_dict = comp_res.get("results", {})
            for m_id, m_data in results_dict.items():
                is_pos = m_data["is_positive"]
                badge_class = "badge-pos" if is_pos else "badge-neg"
                box_class = "pos" if is_pos else "neg"

                st.markdown(
                    f"""
                    <div class="verdict-box {box_class}" style="padding: 0.85rem; margin-bottom: 0.65rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.25rem;">
                            <span style="font-family:var(--font-heading); font-weight:600; font-size:1rem; color:var(--ink);">
                                {m_data["name"]}
                            </span>
                            <span class="{badge_class}">{m_data["label"]}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-family:var(--font-mono); font-size:0.85rem; color:var(--muted);">
                                Confidence: {m_data["confidence"]:.1f}%
                            </span>
                            <span style="font-family:var(--font-mono); font-size:0.8rem; color:var(--muted);">
                                Pos: {m_data["positive_prob"]*100:.1f}% | Neg: {m_data["negative_prob"]*100:.1f}%
                            </span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Single model detailed prediction (review_input only is sent to model)
        result = predict_sentiment(review_input, model_key=selected_model_id)
        if not result.get("success"):
            st.error(result.get("error", "Inference failed."))
            return

        is_pos = result["is_positive"]
        label = result["label"]
        box_class = "pos" if is_pos else "neg"
        badge_class = "badge-pos" if is_pos else "badge-neg"
        conf_pct = result["confidence_percentage"]
        pos_prob = result["positive_probability"]
        neg_prob = result["negative_probability"]

        # Record in session history
        _record_session_history(selected_movie, review_input, label, is_pos, conf_pct)

        st.markdown(
            f"""
            <div class="verdict-box {box_class}">
                <div class="verdict-header">
                    <div>
                        <span class="{badge_class}">{label} SENTIMENT</span>
                        <h2 class="verdict-title {box_class}" style="margin-top:0.35rem;">{label}</h2>
                    </div>
                    <div class="verdict-conf">{conf_pct:.1f}% <span style="font-size:0.8rem; font-weight:400; color:var(--muted);">Confidence</span></div>
                </div>
                <div style="font-family:var(--font-body); font-size:0.88rem; color:var(--muted); line-height:1.45;">
                    Model: <strong>{valid_models[selected_model_id]}</strong>. Posterior probability calibrated to
                    <strong>{pos_prob*100:.1f}%</strong> positive and <strong>{neg_prob*100:.1f}%</strong> negative.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Probability Meter
        st.markdown(
            '<div style="font-family:var(--font-mono); font-size:0.75rem; text-transform:uppercase; color:var(--muted); margin-bottom:0.25rem;">'
            'Posterior Probability Distribution'
            '</div>',
            unsafe_allow_html=True,
        )
        meter_fig = plot_probability_meter(pos_prob, neg_prob)
        st.plotly_chart(meter_fig, use_container_width=True)

        # -------------------------------------------------------------
        # Word-level explanations (LIME)
        # -------------------------------------------------------------
        st.markdown(
            '<div class="cinesense-section-title" style="font-size:1.05rem; margin-top:1.5rem;">Word-level explanation</div>',
            unsafe_allow_html=True,
        )

        if compare_mode:
            model_keys = list(valid_models.keys())
            if hasattr(st, "segmented_control"):
                model_to_explain = st.segmented_control(
                    "Explain model",
                    options=model_keys,
                    format_func=lambda k: valid_models[k],
                    default=selected_model_id if selected_model_id in model_keys else model_keys[0],
                    key="analyzer_lime_model_picker",
                    label_visibility="collapsed",
                )
                if not model_to_explain:
                    model_to_explain = selected_model_id
            else:
                model_to_explain = st.radio(
                    "Explain model",
                    options=model_keys,
                    format_func=lambda k: valid_models[k],
                    index=model_keys.index(selected_model_id) if selected_model_id in model_keys else 0,
                    horizontal=True,
                    key="analyzer_lime_model_picker",
                    label_visibility="collapsed",
                )
        else:
            model_to_explain = selected_model_id

        curr_theme = st.session_state.get("theme_mode", "light")
        with st.spinner("Explaining..."):
            lime_res = get_lime_explanation_cached(
                review_input,
                model_name=model_to_explain,
                num_features=10,
                num_samples=300,
            )

        if lime_res.get("truncated"):
            st.warning(lime_res.get("truncation_note"))

        if lime_res.get("success"):
            active_text = lime_res.get("original_text", review_input)
            highlighted_html = generate_highlighted_html(
                active_text,
                lime_res.get("features", []),
                theme_mode=curr_theme,
            )
            st.markdown(highlighted_html, unsafe_allow_html=True)

            st.markdown(
                f'<div style="font-family:var(--font-mono); font-size:0.78rem; color:var(--muted); margin-top:0.35rem; margin-bottom:0.95rem;">'
                f'{lime_res.get("disclaimer", EXPLANATION_DISCLAIMER)}'
                f'</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="cinesense-section-title" style="font-size:1rem; margin-top:0.75rem;">Words that moved the score</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="cinesense-takeaway" style="font-size:0.8rem;">'
                f'Top LIME word attribution weights for <strong>{valid_models[model_to_explain]}</strong>. '
                f'Green bars push toward Positive (solid underline in text); red bars push toward Negative (dotted underline).'
                f'</div>',
                unsafe_allow_html=True,
            )
            fig_lime = plot_lime_feature_bars(
                lime_res.get("features", []),
                title=f"LIME Word Weights — {valid_models[model_to_explain]}",
            )
            st.plotly_chart(fig_lime, use_container_width=True)
        else:
            err_text = lime_res.get("error", "LIME attribution error.")
            st.info(f"Word explanation unavailable: {err_text}. Standard prediction results displayed above.")

        # Experimental Disclaimer Notice
        st.markdown(
            """
            <div class="cinesense-notice" style="margin-top: 1rem; margin-bottom: 1rem;">
                <strong>Notice:</strong> Results on non-IMDB text are experimental.
            </div>
            """,
            unsafe_allow_html=True,
        )

        # AI Cinematic Context Profile
        context_movie_title = selected_movie.get("title") if selected_movie else None
        with st.spinner("Analyzing cinematic context & nuance..."):
            context_data = analyze_movie_context_cached(
                review_input,
                movie_title=context_movie_title,
            )
        render_context_intelligence_card(context_data)

        # Session review history block
        _render_session_history_block(selected_movie)


def _get_history_key(selected_movie: Optional[Dict[str, Any]]) -> str:
    """Return storage key for current movie or general session history."""
    if selected_movie and selected_movie.get("id"):
        return str(selected_movie["id"])
    return "general_session"


def _record_session_history(
    selected_movie: Optional[Dict[str, Any]],
    review_text: str,
    verdict: str,
    is_positive: bool,
    confidence: float,
) -> None:
    """Store analyzed review in in-memory session history (never saved to disk)."""
    if "session_history_store" not in st.session_state:
        st.session_state["session_history_store"] = {}

    key = _get_history_key(selected_movie)
    hist = st.session_state["session_history_store"].setdefault(key, [])

    snippet = review_text[:80] + ("..." if len(review_text) > 80 else "")

    # Avoid duplicate entry if identical to last review
    if hist and hist[-1].get("snippet") == snippet and hist[-1].get("verdict") == verdict:
        return

    hist.append({
        "snippet": snippet,
        "verdict": verdict,
        "is_positive": is_positive,
        "confidence": confidence,
    })


def _render_session_history_block(selected_movie: Optional[Dict[str, Any]]) -> None:
    """Render the session history list and one-line summary below the results panel."""
    if "session_history_store" not in st.session_state:
        return

    key = _get_history_key(selected_movie)
    history: List[Dict[str, Any]] = st.session_state["session_history_store"].get(key, [])

    if not history:
        return

    total = len(history)
    pos_count = sum(1 for h in history if h.get("is_positive"))
    neg_count = sum(1 for h in history if not h.get("is_positive"))

    count_str = f"{total} {'reviews' if total != 1 else 'review'}"
    summary_text = f"{count_str}: {pos_count} Positive, {neg_count} Negative"

    film_label = f" for {selected_movie['title']}" if selected_movie else ""

    st.markdown(
        f"""
        <div class="cinesense-history-box">
            <div class="cinesense-section-title" style="font-size:1.05rem; margin-top:0.5rem; margin-bottom:0.25rem;">
                Session review history{film_label}
            </div>
            <div class="cinesense-history-summary">
                {summary_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for item in reversed(history):
        b_class = "badge-pos" if item.get("is_positive") else "badge-neg"
        st.markdown(
            f"""
            <div class="cinesense-history-item">
                <span class="cinesense-history-snippet" title="{item['snippet']}">"{item['snippet']}"</span>
                <div class="cinesense-history-meta">
                    <span class="{b_class}">{item['verdict']}</span>
                    <span style="font-family:var(--font-mono); font-size:0.78rem; color:var(--muted);">{item['confidence']:.1f}%</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
