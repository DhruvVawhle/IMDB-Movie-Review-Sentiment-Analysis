"""
Reusable UI components and Plotly chart generators for CineSense.
Adheres strictly to the calm, light-first analytics design system.
"""

import html
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ui.theme import (
    DARK_THEME,
    FONT_BODY,
    FONT_HEADING,
    FONT_MONO,
    LIGHT_THEME,
    get_plotly_layout,
)
import streamlit.components.v1 as st_components


def get_current_theme_tokens() -> Dict[str, str]:
    """Retrieve theme color dictionary matching the current session state mode."""
    theme_mode = "dark"
    try:
        if hasattr(st, "session_state") and "theme_mode" in st.session_state:
            theme_mode = st.session_state["theme_mode"]
    except Exception:
        pass
    return LIGHT_THEME if theme_mode == "light" else DARK_THEME


def render_html(html_str: str) -> None:
    """
    Safely render raw HTML in Streamlit via st.markdown(..., unsafe_allow_html=True).
    Strips leading and trailing whitespace from each line and discards blank lines.
    This guarantees that CommonMark/markdown-it never interprets indented HTML tags
    or empty interpolations as Markdown indented code blocks (<pre><code>).
    """
    clean_lines = [line.strip() for line in html_str.strip().splitlines() if line.strip()]
    st.markdown("\n".join(clean_lines), unsafe_allow_html=True)


# Tab Definitions & Backward-Compatible Aliases
TABS_LIST = [
    "Home",
    "Movies",
    "Analyzer",
    "Project",
    "Dataset",
    "Benchmarks",
    "NLP pipeline",
]

TAB_CONFIG = [
    {"name": "Home", "icon": ":material/home:", "group": "left"},
    {"name": "Movies", "icon": ":material/movie:", "group": "left"},
    {"name": "Analyzer", "icon": ":material/analytics:", "group": "left"},
    {"name": "Project", "icon": ":material/dashboard:", "group": "right"},
    {"name": "Dataset", "icon": ":material/database:", "group": "right"},
    {"name": "Benchmarks", "icon": ":material/bar_chart:", "group": "right"},
    {"name": "NLP pipeline", "icon": ":material/account_tree:", "group": "right"},
]

TAB_ALIASES = {
    "Overview": "Project",
    "Analyze a review": "Analyzer",
    "Model benchmarks": "Benchmarks",
}


def render_header() -> None:
    """
    Render CineSense Header:
    - Left: 'CineSense' in Bricolage Grotesque + tagline:
      'Paste a movie review and see whether three models read it as positive or negative.'
      (muted text, max 52 chars wide, one sentence). No subtitle, no badge/pill/demo label.
    - Right: Primary button 'Analyze a review', ghost button 'See model results', light/dark toggle.
      All controls at least 44px tall with visible keyboard focus.
    - Responsive: Below 640px buttons wrap under tagline in one column.
    - Zero red in header.
    """
    col_left, col_right = st.columns([1.5, 1.3], gap="medium", vertical_alignment="center")

    with col_left:
        st.markdown(
            """
            <div class="cinesense-header-brand">
                <h1 class="cinesense-brand-title">CineSense</h1>
                <p class="cinesense-brand-tagline">
                    Paste a movie review and see whether three models read it as positive or negative.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        b1, b2, b3 = st.columns([1.35, 1.35, 0.85], gap="small", vertical_alignment="center")

        with b1:
            if st.button("Analyze a review", type="primary", key="hdr_analyze_cta", use_container_width=True):
                set_active_tab("Analyzer")
                st.rerun()

        with b2:
            if st.button("See model results", type="secondary", key="hdr_bench_cta", use_container_width=True):
                set_active_tab("Benchmarks")
                st.rerun()

        with b3:
            curr_theme = st.session_state.get("theme_mode", "light")
            toggle_icon = ":material/dark_mode:" if curr_theme == "light" else ":material/light_mode:"
            toggle_label = "Dark" if curr_theme == "light" else "Light"
            if st.button(toggle_label, icon=toggle_icon, type="secondary", key="hdr_theme_toggle", use_container_width=True):
                st.session_state["theme_mode"] = "dark" if curr_theme == "light" else "light"
                st.rerun()


def render_footer() -> None:
    """
    Render CineSense Footer:
    - 1px line at the top
    - Two columns (stacked below 640px)
    - Left: 'CineSense' in Bricolage Grotesque with one muted sentence:
      'Compares Logistic Regression, Naive Bayes and a BiLSTM on 50,000 IMDB reviews. Built as a data science project.'
    - Right: links to Analyzer, Benchmarks, Dataset, and NLP pipeline (accent color, 44px tap height, set via st.query_params)
      + required TMDB note:
      'Movie data and posters from TMDB. This product uses the TMDB API but is not endorsed or certified by TMDB. Reviews come from the Stanford IMDB 50K dataset.'
    """
    col_left, col_right = st.columns([1.1, 1.4], gap="large")

    with col_left:
        st.markdown(
            """
            <div class="cinesense-footer-brand">CineSense</div>
            <p class="cinesense-footer-desc">
                Compares Logistic Regression, Naive Bayes and a BiLSTM on 50,000 IMDB reviews. Built as a data science project.
            </p>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        # Links to Analyzer, Benchmarks, Dataset, and NLP pipeline (accent color, 44px tap height, set via st.query_params)
        l1, l2, l3, l4 = st.columns(4)
        links = [
            ("Analyzer", "Analyzer", l1),
            ("Benchmarks", "Benchmarks", l2),
            ("Dataset", "Dataset", l3),
            ("NLP pipeline", "NLP pipeline", l4),
        ]
        for label, tab_name, col in links:
            with col:
                st.markdown('<div class="cinesense-footer-link-btn">', unsafe_allow_html=True)
                if st.button(label, key=f"ftr_lnk_{tab_name.lower().replace(' ', '_')}", use_container_width=True):
                    set_active_tab(tab_name)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(
            """
            <div class="cinesense-footer-tmdb-note">
                Movie data and posters from TMDB. This product uses the TMDB API but is not endorsed or certified by TMDB. Reviews come from the Stanford IMDB 50K dataset.
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("Model limitations & operational scope", expanded=False):
            st.markdown(
                """
                <div style="font-family:var(--font-body); font-size:0.85rem; line-height:1.55; color:var(--muted);">
                    <strong>1. English only:</strong> Preprocessing and vocabulary are tailored exclusively to English; non-English inputs produce uncalibrated tokens.<br />
                    <strong>2. IMDB-only training:</strong> Fitted exclusively on Stanford's 50,000 IMDB dataset. Distribution shifts may occur on other review sites or short tweets.<br />
                    <strong>3. Sarcasm and negation errors:</strong> Sarcastic phrasing ("A masterpiece of boring cinema") and multi-clause negations can mislead linear models.<br />
                    <strong>4. No neutral class:</strong> Binary classification architecture (Positive vs Negative). Ambivalent reviews are forced into binary polarity.<br />
                    <strong>5. Non-IMDB text is experimental:</strong> Inferences on text outside long-form film reviews are experimental and outside the training distribution.
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_navigation() -> str:
    """
    Render sticky navigation tab bar:
    Left: Home, Movies, Analyzer | Divider | Right: Project, Dataset, Benchmarks, NLP pipeline.
    Active tab: accent text, light accent background, 3px accent underline.
    Hover: subtle background.
    Tabs at least 44px tall.
    Supports arrow keys, Home, and End via accessible WAI-ARIA tab navigation.
    Stores the active tab in st.query_params['tab']. Zero red in the navigation.
    """
    param_tab = st.query_params.get("tab")
    # Resolve aliases if legacy query param was passed
    if param_tab in TAB_ALIASES:
        param_tab = TAB_ALIASES[param_tab]

    if param_tab in TABS_LIST:
        current = param_tab
    else:
        current = st.session_state.get("active_tab", "Home")
        if current in TAB_ALIASES:
            current = TAB_ALIASES[current]
        if current not in TABS_LIST:
            current = "Home"

    st.session_state["active_tab"] = current

    # 8 columns: 3 left tabs, 1 thin divider, 4 right tabs
    cols = st.columns([1.1, 1.1, 1.25, 0.08, 1.1, 1.1, 1.2, 1.35])

    # Left group: Home (col 0), Movies (col 1), Analyzer (col 2)
    left_tabs = [t for t in TAB_CONFIG if t["group"] == "left"]
    for i, tab in enumerate(left_tabs):
        tab_name = tab["name"]
        with cols[i]:
            is_active = tab_name == current
            active_class = "active" if is_active else ""
            st.markdown(f'<div class="cinesense-nav-btn {active_class}">', unsafe_allow_html=True)
            if st.button(
                tab_name,
                key=f"nav_tab_{tab_name.lower().replace(' ', '_')}",
                icon=tab["icon"],
                use_container_width=True,
            ):
                if tab_name == "Home":
                    st.session_state["home_now_offset"] = st.session_state.get("home_now_offset", 0) + 5
                    st.session_state["home_upcoming_offset"] = st.session_state.get("home_upcoming_offset", 0) + 5
                    st.session_state["home_reviews_offset"] = st.session_state.get("home_reviews_offset", 0) + 4
                elif tab_name == "Movies":
                    st.session_state["movies_browse_offset"] = st.session_state.get("movies_browse_offset", 0) + 9
                    st.session_state["selected_movie_idx"] = 0
                    st.session_state["selected_movie_data"] = None
                st.query_params["tab"] = tab_name
                st.session_state["active_tab"] = tab_name
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # Thin vertical divider after Analyzer (col 3)
    with cols[3]:
        st.markdown('<div class="cinesense-nav-divider"></div>', unsafe_allow_html=True)

    # Right group: Project (col 4), Dataset (col 5), Benchmarks (col 6), NLP pipeline (col 7)
    right_tabs = [t for t in TAB_CONFIG if t["group"] == "right"]
    for j, tab in enumerate(right_tabs):
        tab_name = tab["name"]
        col_idx = 4 + j
        with cols[col_idx]:
            is_active = tab_name == current
            active_class = "active" if is_active else ""
            st.markdown(f'<div class="cinesense-nav-btn {active_class}">', unsafe_allow_html=True)
            if st.button(
                tab_name,
                key=f"nav_tab_{tab_name.lower().replace(' ', '_')}",
                icon=tab["icon"],
                use_container_width=True,
            ):
                if tab_name == "Home":
                    st.session_state["home_now_offset"] = st.session_state.get("home_now_offset", 0) + 5
                    st.session_state["home_upcoming_offset"] = st.session_state.get("home_upcoming_offset", 0) + 5
                    st.session_state["home_reviews_offset"] = st.session_state.get("home_reviews_offset", 0) + 4
                elif tab_name == "Movies":
                    st.session_state["movies_browse_offset"] = st.session_state.get("movies_browse_offset", 0) + 9
                    st.session_state["selected_movie_idx"] = 0
                    st.session_state["selected_movie_data"] = None
                st.query_params["tab"] = tab_name
                st.session_state["active_tab"] = tab_name
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # Keyboard navigation support: Arrow keys, Home, and End
    keyboard_script = """
    <script>
    (function() {
        function setupAccessibleTabs() {
            try {
                const doc = window.parent.document;
                if (!doc) return;
                const navBtns = Array.from(doc.querySelectorAll('.cinesense-nav-btn button'));
                if (!navBtns || navBtns.length === 0) return;

                navBtns.forEach((btn, idx) => {
                    const isTabActive = btn.closest('.cinesense-nav-btn')?.classList.contains('active');
                    btn.setAttribute('role', 'tab');
                    btn.setAttribute('aria-selected', isTabActive ? 'true' : 'false');
                    btn.setAttribute('tabindex', isTabActive ? '0' : '-1');

                    if (!btn.dataset.cinesenseKeybound) {
                        btn.dataset.cinesenseKeybound = 'true';
                        btn.addEventListener('keydown', function(e) {
                            let targetIdx = -1;
                            if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
                                targetIdx = (idx + 1) % navBtns.length;
                            } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                                targetIdx = (idx - 1 + navBtns.length) % navBtns.length;
                            } else if (e.key === 'Home') {
                                targetIdx = 0;
                            } else if (e.key === 'End') {
                                targetIdx = navBtns.length - 1;
                            }

                            if (targetIdx !== -1) {
                                e.preventDefault();
                                e.stopPropagation();
                                navBtns[targetIdx].focus();
                                navBtns[targetIdx].click();
                            }
                        });
                    }
                });
            } catch (err) {}
        }
        setupAccessibleTabs();
        setTimeout(setupAccessibleTabs, 200);
        setTimeout(setupAccessibleTabs, 800);
    })();
    </script>
    """
    st_components.html(keyboard_script, height=0, width=0)

    return current


def set_active_tab(tab_name: str) -> None:
    """Helper to programmatically navigate to a tab and update query params."""
    resolved_name = TAB_ALIASES.get(tab_name, tab_name)
    if resolved_name in TABS_LIST:
        if resolved_name == "Home":
            st.session_state["home_now_offset"] = st.session_state.get("home_now_offset", 0) + 5
            st.session_state["home_upcoming_offset"] = st.session_state.get("home_upcoming_offset", 0) + 5
            st.session_state["home_reviews_offset"] = st.session_state.get("home_reviews_offset", 0) + 4
        elif resolved_name == "Movies":
            if not st.session_state.get("selected_movie_data"):
                st.session_state["movies_browse_offset"] = st.session_state.get("movies_browse_offset", 0) + 9
                st.session_state["selected_movie_idx"] = 0
        st.query_params["tab"] = resolved_name
        st.session_state["active_tab"] = resolved_name


def render_kpi_strip(
    total: int = 50000,
    pos: int = 25000,
    neg: int = 25000,
    mean_words: float = 231.0,
    median_words: int = 173,
) -> None:
    """Render the 4-number KPI strip."""
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Reviews</div>
                <div class="kpi-value">{total:,}</div>
                <div class="kpi-desc">Stanford IMDB benchmark</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 3px solid var(--pos);">
                <div class="kpi-label">Positive</div>
                <div class="kpi-value" style="color:var(--pos);">{pos:,}</div>
                <div class="kpi-desc">50.0% class balance</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 3px solid var(--neg);">
                <div class="kpi-label">Negative</div>
                <div class="kpi-value" style="color:var(--neg);">{neg:,}</div>
                <div class="kpi-desc">50.0% class balance</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Mean length</div>
                <div class="kpi-value">{int(round(mean_words))} words</div>
                <div class="kpi-desc">Median {median_words} words</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_pipeline_strip() -> None:
    """Render the 7-step NLP pipeline as a horizontal strip."""
    steps = [
        ("1. Ingest", "Raw reviews", "HTML tags & raw text strings"),
        ("2. Sanitize", "Strip tags", "Removes <br />, URLs & entities"),
        ("3. Normalize", "Lowercase", "Letters only, standard casing"),
        ("4. Tokenize", "NLTK tokens", "Tokenize & filter stopwords"),
        ("5. Lemmatize", "Base words", "WordNet morphological forms"),
        ("6. Vectorize", "Feature map", "TF-IDF (20k), Counts, or Seqs"),
        ("7. Evaluate", "Model scoring", "Inference & calibrated odds"),
    ]
    html = '<div class="pipeline-strip">'
    for num, name, desc in steps:
        html += f"""
        <div class="pipeline-step">
            <div class="pipeline-step-num">{num}</div>
            <div class="pipeline-step-name">{name}</div>
            <div class="pipeline-step-desc">{desc}</div>
        </div>
        """
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_empty_state(title: str, message: str) -> None:
    """Render a polite, calm empty state container."""
    st.markdown(
        f"""
        <div class="cinesense-card" style="text-align:center; padding: 2.5rem 1.5rem; background: var(--surface);">
            <div style="font-family: var(--font-heading); font-size: 1.15rem; font-weight: 600; color: var(--ink); margin-bottom: 0.35rem;">
                {title}
            </div>
            <div style="font-family: var(--font-body); font-size: 0.9rem; color: var(--muted); max-width: 480px; margin: 0 auto; line-height: 1.45;">
                {message}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =====================================================================
# Plotly Chart Generators (Using Shared Theme, Transparent BG, No Titles)
# =====================================================================

def plot_split_class_bar(pos_count: int = 25000, neg_count: int = 25000) -> go.Figure:
    """
    Replace two-bar chart with a single horizontal split bar.
    Equal halves share a center dividing edge.
    """
    theme = get_current_theme_tokens()
    total = pos_count + neg_count
    pos_pct = (pos_count / total) * 100 if total else 50.0
    neg_pct = (neg_count / total) * 100 if total else 50.0

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=["Balance"],
        x=[pos_count],
        name=f"Positive ({pos_count:,})",
        orientation="h",
        marker=dict(color=theme["pos"], line=dict(color=theme["line"], width=1)),
        text=f"Positive: {pos_count:,} ({pos_pct:.1f}%)",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(family="Inter, sans-serif", size=12, color="#FFFFFF"),
        hovertemplate="Positive: %{x:,} reviews (%{text})<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=["Balance"],
        x=[neg_count],
        name=f"Negative ({neg_count:,})",
        orientation="h",
        marker=dict(color=theme["neg"], line=dict(color=theme["line"], width=1)),
        text=f"Negative: {neg_count:,} ({neg_pct:.1f}%)",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(family="Inter, sans-serif", size=12, color="#FFFFFF"),
        hovertemplate="Negative: %{x:,} reviews (%{text})<extra></extra>",
    ))

    layout = get_plotly_layout(
        height=100,
        barmode="stack",
        margin=dict(l=10, r=10, t=10, b=25),
        showlegend=False,
    )
    layout["xaxis"] = dict(
        range=[0, total],
        showgrid=False,
        zeroline=False,
        tickvals=[0, pos_count, total],
        ticktext=["0", f"50% Split ({pos_count:,})", f"{total:,}"],
        tickfont=dict(family="IBM Plex Mono", size=10, color=theme["muted"]),
    )
    layout["yaxis"] = dict(showticklabels=False, showgrid=False)
    fig.update_layout(layout)
    return fig


def plot_length_histogram(df: pd.DataFrame) -> go.Figure:
    """Histogram comparing word count distributions for positive vs negative reviews with mean annotation."""
    theme = get_current_theme_tokens()
    fig = go.Figure()

    pos_lens = df[df["sentiment_clean"] == "positive"]["word_count"]
    neg_lens = df[df["sentiment_clean"] == "negative"]["word_count"]

    fig.add_trace(go.Histogram(
        x=pos_lens,
        name="Positive",
        nbinsx=45,
        marker_color=theme["pos"],
        opacity=0.65,
        hovertemplate="Positive: %{y} reviews (~%{x} words)<extra></extra>",
    ))
    fig.add_trace(go.Histogram(
        x=neg_lens,
        name="Negative",
        nbinsx=45,
        marker_color=theme["neg"],
        opacity=0.65,
        hovertemplate="Negative: %{y} reviews (~%{x} words)<extra></extra>",
    ))

    # Mean annotation at 231 words
    mean_val = 231.0
    fig.add_vline(
        x=mean_val,
        line_width=2,
        line_dash="dash",
        line_color=theme["accent"],
        annotation_text="Mean 231 words",
        annotation_position="top right",
        annotation_font=dict(color=theme["accent"], family="IBM Plex Mono", size=11),
    )

    layout = get_plotly_layout(height=280, barmode="overlay")
    layout["xaxis"]["title"] = "Word Count (HTML tags stripped)"
    layout["xaxis"]["range"] = [0, 900]
    layout["yaxis"]["title"] = "Review Frequency"
    fig.update_layout(layout)
    return fig


def plot_probability_meter(pos_prob: float, neg_prob: float) -> go.Figure:
    """Compact horizontal probability meter."""
    theme = get_current_theme_tokens()
    fig = go.Figure()
    pos_pct = round(pos_prob * 100, 1)
    neg_pct = round(neg_prob * 100, 1)

    fig.add_trace(go.Bar(
        y=["Score"],
        x=[pos_pct],
        name=f"Positive ({pos_pct}%)",
        orientation="h",
        marker=dict(color=theme["pos"]),
        text=f"{pos_pct}% Positive" if pos_pct >= 20 else "",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(family="Inter, sans-serif", size=11, color="#FFFFFF"),
        hoverinfo="none",
    ))
    fig.add_trace(go.Bar(
        y=["Score"],
        x=[neg_pct],
        name=f"Negative ({neg_pct}%)",
        orientation="h",
        marker=dict(color=theme["neg"]),
        text=f"{neg_pct}% Negative" if neg_pct >= 20 else "",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(family="Inter, sans-serif", size=11, color="#FFFFFF"),
        hoverinfo="none",
    ))
    fig.add_trace(go.Bar(
        y=["Score"],
        x=[neg_pct],
        name=f"Negative ({neg_pct}%)",
        orientation="h",
        marker=dict(color=LIGHT_THEME["neg"]),
        text=f"{neg_pct}% Negative" if neg_pct >= 20 else "",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(family="IBM Plex Sans", size=11, color="#FFFFFF"),
        hoverinfo="none",
    ))

    layout = get_plotly_layout(
        height=46,
        barmode="stack",
        margin=dict(l=0, r=0, t=4, b=4),
        showlegend=False,
    )
    layout["xaxis"] = dict(showgrid=False, showticklabels=False, range=[0, 100], zeroline=False)
    layout["yaxis"] = dict(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_layout(layout)
    return fig


def plot_distinctive_words_bar(
    top_features: Dict[str, List[Dict[str, Any]]],
    sentiment: str = "positive",
    top_n: int = 12,
) -> go.Figure:
    """
    Ranked horizontal bar chart of distinctive words per class.
    Excludes HTML artefacts ('br') and displays direct value labels.
    """
    theme = get_current_theme_tokens()
    items = top_features.get(sentiment, [])[:top_n]
    if not items:
        return go.Figure()

    terms = [item["term"] for item in reversed(items)]
    weights = [abs(item["weight"]) for item in reversed(items)]
    color = theme["pos"] if sentiment == "positive" else theme["neg"]

    fig = go.Figure(go.Bar(
        x=weights,
        y=terms,
        orientation="h",
        marker=dict(color=color),
        text=[f"{w:.2f}" for w in weights],
        textposition="outside",
        textfont=dict(family="IBM Plex Mono", color=theme["ink"], size=11),
        hovertemplate="<b>%{y}</b>: %{x:.3f} separation weight<extra></extra>",
    ))

    layout = get_plotly_layout(height=340, margin=dict(l=90, r=40, t=10, b=35))
    layout["xaxis"]["title"] = "TF-IDF Logistic Regression Magnitude"
    fig.update_layout(layout)
    return fig


def plot_top_features_divergent(top_features: Dict[str, List[Dict[str, Any]]], top_n: int = 12) -> go.Figure:
    """Divergent horizontal bar chart showing top positive and negative vocabulary coefficients."""
    theme = get_current_theme_tokens()
    pos_items = top_features.get("positive", [])[:top_n]
    neg_items = top_features.get("negative", [])[:top_n]

    terms = [item["term"] for item in reversed(pos_items)] + [item["term"] for item in neg_items]
    weights = [item["weight"] for item in reversed(pos_items)] + [item["weight"] for item in neg_items]
    colors = [theme["pos"] if w > 0 else theme["neg"] for w in weights]

    fig = go.Figure(go.Bar(
        x=weights,
        y=terms,
        orientation="h",
        marker=dict(color=colors),
        text=[f"{w:+.2f}" for w in weights],
        textposition="outside",
        textfont=dict(family="IBM Plex Mono", size=10, color=theme["ink"]),
        hoverinfo="x+y",
    ))

    layout = get_plotly_layout(height=480, margin=dict(l=100, r=40, t=10, b=40))
    layout["xaxis"]["title"] = "Coefficient Weight (Positive vs Negative Association)"
    layout["yaxis"]["autorange"] = "reversed"
    fig.update_layout(layout)
    return fig


def plot_benchmarks_bar_chart(comp_df: pd.DataFrame) -> go.Figure:
    """
    Grouped bar chart for benchmarks across models.
    Y-axis starts at 60% and clearly states this in the axis label.
    """
    theme = get_current_theme_tokens()
    fig = go.Figure()

    metric_series = [
        ("Accuracy (%)", theme["accent"]),
        ("Precision (%)", theme["pos"]),
        ("Recall (%)", "#58A6FF"),
        ("F1-Score (%)", "#BC8CFF"),
    ]

    for metric_col, col_color in metric_series:
        if metric_col in comp_df.columns:
            fig.add_trace(go.Bar(
                name=metric_col.replace(" (%)", ""),
                x=comp_df["Model"],
                y=comp_df[metric_col],
                text=comp_df[metric_col].apply(lambda v: f"{v:.1f}%"),
                textposition="outside",
                textfont=dict(family="IBM Plex Mono", size=10),
                marker_color=col_color,
            ))

    layout = get_plotly_layout(height=340, barmode="group", margin=dict(l=45, r=20, t=15, b=40))
    layout["yaxis"]["range"] = [60, 100]
    layout["yaxis"]["title"] = "Score (%) [Baseline starts at 60%]"
    layout["xaxis"]["title"] = "Model Architecture"
    layout["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    fig.update_layout(layout)
    return fig


def plot_roc_curves(models_dict: Dict[str, Any]) -> go.Figure:
    """Multi-model ROC curve comparison with chance diagonal."""
    theme = get_current_theme_tokens()
    fig = go.Figure()
    palette = [theme["accent"], "#58A6FF", theme["pos"]]
    idx = 0

    for model_key, meta in models_dict.items():
        if meta.get("status") == "available" and "roc_curve" in meta:
            rc = meta["roc_curve"]
            auc_val = rc.get("auc", 0.0)
            color = palette[idx % len(palette)]
            idx += 1

            fig.add_trace(go.Scatter(
                x=rc["fpr"],
                y=rc["tpr"],
                mode="lines",
                name=f"{meta.get('name', model_key)} (AUC = {auc_val:.3f})",
                line=dict(color=color, width=2.2),
            ))

    # Diagonal chance line
    fig.add_trace(go.Scatter(
        x=[0, 1],
        y=[0, 1],
        mode="lines",
        name="Chance baseline (0.50)",
        line=dict(color=theme["muted"], width=1.5, dash="dash"),
    ))

    layout = get_plotly_layout(height=340, margin=dict(l=45, r=20, t=15, b=40))
    layout["xaxis"]["title"] = "False Positive Rate (1 - Specificity)"
    layout["yaxis"]["title"] = "True Positive Rate (Sensitivity)"
    layout["xaxis"]["range"] = [0, 1]
    layout["yaxis"]["range"] = [0, 1.02]
    layout["legend"] = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    fig.update_layout(layout)
    return fig


def plot_confusion_matrix(cm: List[List[int]], model_name: str) -> go.Figure:
    """Annotated 2x2 confusion matrix with counts and percentages."""
    theme = get_current_theme_tokens()
    tn, fp = cm[0]
    fn, tp = cm[1]
    total = tn + fp + fn + tp

    z = [[tn, fp], [fn, tp]]
    text = [
        [f"True Neg (TN)<br><b>{tn:,}</b> ({tn/total*100:.1f}%)", f"False Pos (FP)<br><b>{fp:,}</b> ({fp/total*100:.1f}%)"],
        [f"False Neg (FN)<br><b>{fn:,}</b> ({fn/total*100:.1f}%)", f"True Pos (TP)<br><b>{tp:,}</b> ({tp/total*100:.1f}%)"],
    ]

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=["Predicted Negative", "Predicted Positive"],
        y=["Actual Negative", "Actual Positive"],
        text=text,
        texttemplate="%{text}",
        textfont=dict(family="Inter, sans-serif", size=12, color=theme["ink"]),
        colorscale=[
            [0.0, theme["surface"]],
            [0.5, theme["surface_2"]],
            [1.0, theme["accent_light"] if "accent_light" in theme else theme["accent"]],
        ],
        showscale=False,
    ))

    layout = get_plotly_layout(height=280, margin=dict(l=70, r=20, t=15, b=40))
    layout["xaxis"]["title"] = "Predicted Sentiment"
    layout["yaxis"]["title"] = "Actual Sentiment"
    fig.update_layout(layout)
    return fig



def render_context_intelligence_card(context_data: Dict[str, Any]) -> None:
    """Render cinematic context analysis, tone, aspects, and nuance breakdown."""
    is_fallback = context_data.get("is_fallback", False)
    engine_name = context_data.get("engine", "NLP Context Engine")
    summary = context_data.get("summary", "")
    tone = context_data.get("tone", "Measured")
    nuance = context_data.get("nuance", "")
    verdict = context_data.get("verdict", "Evaluated")
    aspects = context_data.get("aspects", [])
    status_msg = context_data.get("status_message", "")

    if not is_fallback:
        badge_html = '<span class="badge-neutral" style="color:var(--pos); background:var(--pos-bg); border-color:var(--pos-border); font-weight:600;">LIVE OPENROUTER LLM</span>'
    else:
        badge_html = '<span class="badge-neutral" style="color:var(--warn); background:var(--warn-bg); border-color:var(--warn-border); font-weight:600;">OFFLINE NLP ENGINE</span>'

    aspects_html = ""
    if aspects:
        aspects_html = '<div style="font-family:var(--font-mono); font-size:0.7rem; text-transform:uppercase; color:var(--muted); margin-top:0.6rem; margin-bottom:0.4rem;">Extracted Cinematic Aspects</div>'
        for asp in aspects:
            asp_sentiment = asp.get("sentiment", "Positive")
            if asp_sentiment.lower() == "positive":
                badge_class = "badge-pos"
            elif asp_sentiment.lower() == "negative":
                badge_class = "badge-neg"
            else:
                badge_class = "badge-neutral"

            aspects_html += f"""
            <div style="display:flex; justify-content:space-between; align-items:flex-start; padding:0.4rem 0.55rem; background:var(--surface-2); border-radius:4px; margin-bottom:0.35rem; border:1px solid var(--line);">
                <div style="max-width:75%;">
                    <strong style="font-family:var(--font-heading); font-size:0.85rem; color:var(--ink);">{asp.get('aspect', 'Aspect')}:</strong>
                    <span style="font-family:var(--font-body); font-size:0.82rem; color:var(--muted); margin-left:0.25rem;">{asp.get('detail', '')}</span>
                </div>
                <span class="{badge_class}" style="font-size:0.7rem; padding:0.1rem 0.4rem;">{asp_sentiment}</span>
            </div>
            """

    st.markdown(
        f"""
        <div class="cinesense-card" style="border-top: 3px solid var(--accent); margin-top: 1.25rem; margin-bottom: 1.25rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem; margin-bottom:0.65rem;">
                <div style="font-family:var(--font-heading); font-size:1.05rem; font-weight:600; color:var(--ink);">
                    Cinematic Context & NLP Intelligence
                </div>
                <div>{badge_html}</div>
            </div>
            <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--muted); margin-bottom:0.75rem;">
                Engine: <strong>{engine_name}</strong> &bull; {status_msg}
            </div>
            <div style="background:var(--surface-2); border-radius:4px; padding:0.75rem 0.9rem; margin-bottom:0.85rem; border-left:3px solid var(--accent);">
                <div style="font-family:var(--font-mono); font-size:0.7rem; text-transform:uppercase; color:var(--muted); margin-bottom:0.25rem;">Contextual Summary</div>
                <div style="font-family:var(--font-body); font-size:0.9rem; color:var(--ink); font-style:italic; line-height:1.45;">
                    "{summary}"
                </div>
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:0.5rem; margin-bottom:0.75rem;">
                <div style="background:var(--surface-2); padding:0.5rem 0.75rem; border-radius:4px; border:1px solid var(--line);">
                    <div style="font-family:var(--font-mono); font-size:0.68rem; text-transform:uppercase; color:var(--muted);">Tone & Mood</div>
                    <div style="font-family:var(--font-heading); font-size:0.92rem; font-weight:600; color:var(--ink); margin-top:0.15rem;">{tone}</div>
                </div>
                <div style="background:var(--surface-2); padding:0.5rem 0.75rem; border-radius:4px; border:1px solid var(--line);">
                    <div style="font-family:var(--font-mono); font-size:0.68rem; text-transform:uppercase; color:var(--muted);">Contextual Verdict</div>
                    <div style="font-family:var(--font-heading); font-size:0.92rem; font-weight:600; color:var(--ink); margin-top:0.15rem;">{verdict}</div>
                </div>
            </div>
            <div style="margin-bottom:0.75rem;">
                <div style="font-family:var(--font-mono); font-size:0.7rem; text-transform:uppercase; color:var(--muted); margin-bottom:0.2rem;">Nuance & Subtext</div>
                <div style="font-family:var(--font-body); font-size:0.85rem; color:var(--ink); line-height:1.4;">{nuance}</div>
            </div>
            {aspects_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def plot_lime_feature_bars(features: List[Tuple[str, float]], title: str = "") -> go.Figure:
    """Horizontal divergent bar chart for LIME word weights pushing Positive vs Negative."""
    theme = get_current_theme_tokens()
    if not features:
        fig = go.Figure()
        fig.update_layout(get_plotly_layout(height=180))
        return fig

    # Sort so negative are at top, positive at bottom (or vice versa)
    sorted_features = sorted(features, key=lambda x: x[1])
    terms = [str(item[0]) for item in sorted_features]
    weights = [float(item[1]) for item in sorted_features]
    colors = [theme["pos"] if w > 0 else theme["neg"] for w in weights]

    fig = go.Figure(go.Bar(
        x=weights,
        y=terms,
        orientation="h",
        marker=dict(color=colors),
        text=[f"{w:+.2f}" for w in weights],
        textposition="outside",
        textfont=dict(family="IBM Plex Mono", size=10, color=theme["ink"]),
        hoverinfo="x+y",
    ))

    layout = get_plotly_layout(height=max(220, len(features) * 26 + 60), margin=dict(l=100, r=40, t=15, b=40))
    layout["xaxis"]["title"] = "LIME Contribution Weight (Negative ← 0 → Positive)"
    layout["xaxis"]["zeroline"] = True
    layout["xaxis"]["zerolinecolor"] = theme["line"]
    layout["xaxis"]["zerolinewidth"] = 1.5
    fig.update_layout(layout)
    return fig


def plot_failure_patterns_bar(patterns: List[Dict[str, Any]], overall_error_rate: float) -> go.Figure:
    """Horizontal bar chart comparing failure pattern error rates against overall test baseline."""
    theme = get_current_theme_tokens()
    names = [p["pattern"] for p in reversed(patterns)]
    rates = [p["error_rate"] for p in reversed(patterns)]
    counts = [p["count"] for p in reversed(patterns)]

    colors = [
        theme["neg"] if r > overall_error_rate else theme["accent"]
        for r in rates
    ]

    fig = go.Figure(go.Bar(
        x=rates,
        y=names,
        orientation="h",
        marker=dict(color=colors),
        text=[f"{r:.1f}% (N={c:,})" for r, c in zip(rates, counts)],
        textposition="outside",
        textfont=dict(family="IBM Plex Mono", size=11, color=theme["ink"]),
        hoverinfo="x+y",
    ))

    # Add vertical dashed line for overall error rate baseline
    fig.add_vline(
        x=overall_error_rate,
        line_dash="dash",
        line_color=theme["muted"],
        line_width=1.5,
        annotation_text=f"Baseline ({overall_error_rate:.1f}%)",
        annotation_position="top right",
        annotation_font=dict(family="IBM Plex Mono", size=10, color=theme["muted"]),
    )
    layout = get_plotly_layout(height=260, margin=dict(l=220, r=90, t=25, b=40))
    layout["xaxis"]["title"] = "Subset Classification Error Rate (%)"
    layout["xaxis"]["ticksuffix"] = "%"
    fig.update_layout(layout)
    return fig


# =============================================================================
# Letterboxd-Style Community Reviews UI Components
# =============================================================================

def format_letterboxd_stars(rating: float) -> str:
    """
    Format numeric rating (0.5 to 5.0) as iconic Letterboxd stars with half-stars.
    Examples: 5.0 -> '★★★★★', 4.5 -> '★★★★½', 3.5 -> '★★★½', 1.0 -> '★'
    """
    try:
        r = float(rating)
    except (ValueError, TypeError):
        r = 5.0

    full = int(r)
    half = (r - full) >= 0.4
    stars = "★" * full
    if half:
        stars += "½"
    return stars if stars else "★"


def render_letterboxd_histogram(stats: Dict[str, Any]) -> str:
    """
    Render HTML for Letterboxd 5-star rating distribution mini histogram bars.
    """
    star_counts = stats.get("star_counts", {1: 0, 2: 0, 3: 0, 4: 0, 5: 0})
    max_c = max(star_counts.values()) if star_counts and max(star_counts.values()) > 0 else 1

    cols_html = []
    for star in [1, 2, 3, 4, 5]:
        cnt = star_counts.get(star, 0)
        h = max(5, int((cnt / max_c) * 30)) if cnt > 0 else 3
        cols_html.append(
            f'<div class="letterboxd-hist-col" title="{star} stars: {cnt} review(s)">'
            f'<div class="letterboxd-hist-bar" style="height:{h}px;"></div>'
            f'<div class="letterboxd-hist-label">{star}★</div>'
            f'</div>'
        )
    return f'<div class="letterboxd-histogram-container">{"".join(cols_html)}</div>'


def render_letterboxd_review_card(
    review: Dict[str, Any],
    key_prefix: str = "lb",
    show_film_tag: bool = False,
) -> None:
    """
    Render an individual review card styled in Letterboxd film editorial aesthetic.
    Includes reviewer monogram, star rating, liked heart, sentiment pill, review prose,
    and interactive like action.
    """
    from services.review_storage_service import like_review

    r_id = review.get("id", f"{key_prefix}_{hash(review.get('review_text', ''))}")
    author = review.get("author_name", "Anonymous Cinephile")
    handle = review.get("author_handle", "@cinephile")
    date_str = review.get("formatted_date", "Recently")
    rating_val = float(review.get("rating", 5.0))
    stars_str = format_letterboxd_stars(rating_val)
    is_liked = review.get("is_liked", False)
    spoilers = review.get("contains_spoilers", False)
    text = review.get("review_text", "")
    sentiment_label = review.get("sentiment_label", "POSITIVE").upper()
    confidence = float(review.get("sentiment_confidence", 90.0))
    model_name = review.get("model_used", "AI Model")
    likes = int(review.get("likes_count", 0))

    # Compute author initials
    names = author.strip().split()
    initials = "".join([n[0].upper() for n in names[:2]]) if names else "C"
    avatar_bg = review.get("avatar_color", "#1A4B5C")
    avatar_fg = review.get("avatar_fg", "#8BE9FD")

    # Sentiment styling
    is_pos = sentiment_label == "POSITIVE"
    badge_class = "badge-pos" if is_pos else "badge-neg"

    # Liked heart icon
    heart_html = '<span class="letterboxd-heart-icon" title="Liked by reviewer">🧡</span>' if is_liked else ""

    # Optional film title link
    film_tag_html = ""
    if show_film_tag and review.get("movie_title"):
        film_tag_html = (
            f'<div style="font-family:var(--font-heading); font-size:0.88rem; font-weight:600; color:var(--accent); margin-bottom:0.35rem;">'
            f'🎬 {html.escape(str(review.get("movie_title")))} <span style="font-size:0.75rem; color:var(--muted); font-weight:400;">({html.escape(str(review.get("movie_year", "")))})</span>'
            f'</div>'
        )

    spoiler_badge_html = (
        '<div class="letterboxd-spoiler-tag">⚠️ Contains Spoilers</div>' if spoilers else ""
    )

    clean_text = html.escape(str(text)).replace("\n", "<br />")
    clean_author = html.escape(str(author))
    clean_handle = html.escape(str(handle))
    clean_model = html.escape(str(model_name))

    card_html = f"""
    <div class="cinesense-letterboxd-card">
        {film_tag_html}
        <div class="letterboxd-card-header">
            <div class="letterboxd-user-block">
                <div class="letterboxd-avatar" style="background:{avatar_bg}; color:{avatar_fg};">
                    {initials}
                </div>
                <div class="letterboxd-user-info">
                    <span class="letterboxd-author-name">{clean_author}</span>
                    <div class="letterboxd-author-meta">
                        <span class="letterboxd-author-handle">{clean_handle}</span>
                        <span class="letterboxd-date-sep">&bull;</span>
                        <span class="letterboxd-watch-date">{date_str}</span>
                    </div>
                </div>
            </div>
            <div class="letterboxd-rating-row">
                <span class="letterboxd-stars-vibrant">{stars_str}</span>
                {heart_html}
                <span class="{badge_class}" style="font-size:0.72rem; padding:0.12rem 0.45rem;">
                    {sentiment_label} ({confidence:.0f}%)
                </span>
            </div>
        </div>
        {spoiler_badge_html}
        <div class="letterboxd-body">{clean_text}</div>
        <div class="letterboxd-footer">
            <div class="letterboxd-footer-likes">
                <span>♥</span> <span>{likes} helpful</span>
            </div>
            <div class="letterboxd-footer-model">
                Calibrated by <strong>{clean_model}</strong>
            </div>
        </div>
    </div>
    """
    render_html(card_html)

    # Interactive like button
    btn_col, _ = st.columns([1.5, 4])
    with btn_col:
        like_btn_key = f"btn_like_{key_prefix}_{r_id}"
        if st.button(f"♥ Helpful ({likes})", key=like_btn_key, use_container_width=True):
            like_review(r_id)
            st.rerun()


def render_letterboxd_reviews_section(
    movie: Dict[str, Any],
    allow_compose: bool = True,
    expanded_compose: bool = False,
) -> None:
    """
    Complete Letterboxd-style community review section for a movie:
    - Overall letterboxd rating stats, average stars, and histogram
    - 'Write a review' composer with star selector and instant sentiment classification
    - Filterable and sortable review stream
    """
    from services.prediction_service import get_available_models_list, predict_sentiment
    from services.review_storage_service import (
        get_movie_review_stats,
        get_reviews_for_movie,
        save_review,
    )

    m_id = movie.get("id")
    m_title = movie.get("title", "Untitled")
    m_year = movie.get("release_year") or (movie.get("release_date") or "")[:4] or "N/A"
    m_poster = movie.get("poster_url", "")

    stats = get_movie_review_stats(m_id, m_title)
    all_reviews = get_reviews_for_movie(m_id, m_title)
    total_reviews = stats.get("total_count", 0)
    avg_rating = stats.get("average_rating", 0.0)
    avg_stars_str = format_letterboxd_stars(avg_rating)
    pos_pct = stats.get("positive_percentage", 0.0)

    # Header with Letterboxd styling
    render_html(
        f"""
        <div class="cinesense-letterboxd-panel">
            <div class="letterboxd-stats-header">
                <div>
                    <div style="font-family:var(--font-mono); font-size:0.75rem; text-transform:uppercase; color:var(--muted); letter-spacing:0.04em; margin-bottom:0.25rem;">
                        Letterboxd Community Consensus
                    </div>
                    <div class="letterboxd-score-badge">
                        <span class="letterboxd-stars-primary">{avg_stars_str}</span>
                        <span class="letterboxd-score-val">{avg_rating:.1f}</span>
                        <span style="font-family:var(--font-body); font-size:0.9rem; color:var(--muted);">
                            / 5.0 &bull; {total_reviews} {'reviews' if total_reviews != 1 else 'review'}
                        </span>
                    </div>
                </div>
                <div style="display:flex; align-items:center; gap:1.25rem;">
                    <div style="text-align:right;">
                        <span class="badge-pos" style="font-size:0.75rem;">{pos_pct:.0f}% Positive AI Consensus</span>
                        <div style="font-family:var(--font-mono); font-size:0.72rem; color:var(--muted); margin-top:0.2rem;">
                            {stats.get('liked_percentage', 0):.0f}% marked with ❤️
                        </div>
                    </div>
                    {render_letterboxd_histogram(stats)}
                </div>
            </div>
        </div>
        """
    )

    # Review Composer
    if allow_compose:
        with st.expander(f"✍️ Log or Write a Review for {m_title}", expanded=expanded_compose):
            comp_c1, comp_c2 = st.columns([1.5, 1])
            with comp_c1:
                author_input = st.text_input(
                    "Your Name or Handle",
                    value=st.session_state.get("user_author_name", "Film Critic"),
                    placeholder="e.g. Alex Rivera or @cinephile",
                    key=f"compose_author_{m_id}",
                )
            with comp_c2:
                # Star rating selection
                rating_options = [5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0]
                rating_labels = {
                    r: f"{format_letterboxd_stars(r)} ({r} stars)" for r in rating_options
                }
                selected_stars = st.selectbox(
                    "Your Rating",
                    options=rating_options,
                    format_func=lambda r: rating_labels[r],
                    index=1,
                    key=f"compose_rating_{m_id}",
                )

            comp_meta1, comp_meta2, comp_meta3 = st.columns([1, 1, 1.2])
            with comp_meta1:
                is_liked_input = st.checkbox("❤️ Liked this film", value=True, key=f"compose_liked_{m_id}")
            with comp_meta2:
                is_spoiler_input = st.checkbox("⚠️ Contains spoilers", value=False, key=f"compose_spoiler_{m_id}")
            with comp_meta3:
                available_models = get_available_models_list()
                model_choices = {m["id"]: m["name"] for m in available_models if m.get("available")}
                default_m = "logistic_regression" if "logistic_regression" in model_choices else list(model_choices.keys())[0]
                eval_model_key = st.selectbox(
                    "AI Sentiment Model",
                    options=list(model_choices.keys()),
                    format_func=lambda k: model_choices[k],
                    index=list(model_choices.keys()).index(default_m) if default_m in model_choices else 0,
                    key=f"compose_model_{m_id}",
                )

            review_body = st.text_area(
                "Your Review",
                placeholder=f"Write your Letterboxd-style thoughts on {m_title}...",
                height=120,
                key=f"compose_body_{m_id}",
            )

            submit_col, _ = st.columns([1.8, 3])
            with submit_col:
                if st.button("Publish review", type="primary", use_container_width=True, key=f"btn_pub_rev_{m_id}"):
                    if not review_body.strip():
                        st.warning("Please enter review text before publishing.")
                    else:
                        with st.spinner("Analyzing sentiment and saving review..."):
                            pred = predict_sentiment(review_body.strip(), model_key=eval_model_key)
                            sentiment_label = pred.get("label", "POSITIVE")
                            conf_pct = pred.get("confidence_percentage", 90.0)

                            clean_handle = (
                                f"@{author_input.lower().replace(' ', '')}"
                                if author_input and not author_input.startswith("@")
                                else author_input
                            )

                            save_review(
                                movie_id=m_id,
                                movie_title=m_title,
                                movie_year=m_year,
                                movie_poster=m_poster,
                                author_name=author_input or "Anonymous Cinephile",
                                author_handle=clean_handle or "@cinephile",
                                rating=selected_stars,
                                is_liked=is_liked_input,
                                contains_spoilers=is_spoiler_input,
                                review_text=review_body.strip(),
                                sentiment_label=sentiment_label,
                                sentiment_confidence=conf_pct,
                                model_used=model_choices.get(eval_model_key, "Logistic Regression"),
                            )
                            # Persist author name preference
                            st.session_state["user_author_name"] = author_input
                            st.toast(f"Review published to Letterboxd community feed! ({sentiment_label})", icon="🎬")
                            st.rerun()

    # Filter & Sort controls
    if all_reviews:
        fcol1, fcol2 = st.columns([2.5, 1.5])
        with fcol1:
            st.markdown(
                f'<div class="cinesense-section-title" style="font-size:1.1rem; margin-top:0.5rem; margin-bottom:0.5rem;">'
                f'Reviews for {m_title} <span style="font-size:0.85rem; color:var(--muted); font-weight:400;">({len(all_reviews)})</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with fcol2:
            filter_choice = st.selectbox(
                "Filter & Sort",
                options=["Latest", "Highest Rated", "Lowest Rated", "Positive Only", "Negative Only"],
                key=f"sort_reviews_{m_id}",
                label_visibility="collapsed",
            )

        # Apply filtering & sorting
        displayed_reviews = list(all_reviews)
        if filter_choice == "Positive Only":
            displayed_reviews = [r for r in displayed_reviews if r.get("sentiment_label") == "POSITIVE"]
        elif filter_choice == "Negative Only":
            displayed_reviews = [r for r in displayed_reviews if r.get("sentiment_label") == "NEGATIVE"]
        elif filter_choice == "Highest Rated":
            displayed_reviews.sort(key=lambda r: float(r.get("rating", 0)), reverse=True)
        elif filter_choice == "Lowest Rated":
            displayed_reviews.sort(key=lambda r: float(r.get("rating", 0)))
        else:
            displayed_reviews.sort(key=lambda r: r.get("created_at", ""), reverse=True)

        if not displayed_reviews:
            st.info(f"No reviews match filter '{filter_choice}'.")
        else:
            for idx, rev in enumerate(displayed_reviews):
                render_letterboxd_review_card(rev, key_prefix=f"m_{m_id}_{idx}")
    else:
        render_html(
            f"""
            <div style="background:var(--bg); border:1px dashed var(--line); border-radius:6px; padding:1.5rem; text-align:center; margin-top:0.75rem;">
                <div style="font-size:1.5rem; margin-bottom:0.35rem;">🎬</div>
                <div style="font-family:var(--font-heading); font-size:1rem; font-weight:600; color:var(--ink);">
                    Be the first to review {m_title}
                </div>
                <div style="font-family:var(--font-body); font-size:0.85rem; color:var(--muted); margin-top:0.25rem;">
                    Log your thoughts above or analyze a review to populate the Letterboxd community consensus.
                </div>
            </div>
            """
        )


def render_letterboxd_watched_actions(
    movie: Dict[str, Any],
    key_prefix: str = "act",
    show_status_bar: bool = True,
) -> None:
    """
    Render dynamic Letterboxd actions bar: Watched status toggle, Liked heart, and personal star rating.
    All actions are dynamically persisted in data/user_watched_movies.json.
    """
    from services.review_storage_service import (
        get_watched_movie,
        is_movie_watched,
        mark_movie_as_watched,
        toggle_movie_liked,
        toggle_movie_watched,
    )

    m_id = movie.get("id")
    m_title = movie.get("title", "")
    m_year = movie.get("release_year") or (movie.get("release_date") or "")[:4] or "N/A"
    m_poster = movie.get("poster_url") or movie.get("poster") or ""

    watched_rec = get_watched_movie(m_id, m_title)
    is_watched = watched_rec is not None
    is_liked = watched_rec.get("is_liked", False) if watched_rec else False
    user_rating = watched_rec.get("rating") if watched_rec else None

    # Top Letterboxd status pill (optional if integrated into spotlight card)
    if show_status_bar:
        if is_watched:
            w_date = watched_rec.get("formatted_date", "Recently")
            w_cnt = watched_rec.get("watch_count", 1)
            cnt_badge = f" ({w_cnt}x logged)" if w_cnt > 1 else ""
            heart_badge = " &bull; Liked" if is_liked else ""
            rating_badge = f" &bull; {format_letterboxd_stars(user_rating)}" if user_rating else ""
            render_html(
                f"""
                <div class="letterboxd-action-bar">
                    <span class="letterboxd-watched-status-active">
                        <span style="font-weight:700;">✓</span> Watched on {w_date}{cnt_badge}{rating_badge}{heart_badge}
                    </span>
                    <span style="font-family:var(--font-mono); font-size:0.75rem; color:var(--muted);">
                        Logged in Diary
                    </span>
                </div>
                """
            )
        else:
            render_html(
                """
                <div class="letterboxd-action-bar">
                    <span class="letterboxd-watched-status-inactive">
                        Not in your watched diary yet
                    </span>
                    <span style="font-family:var(--font-mono); font-size:0.75rem; color:var(--muted);">
                        Mark watched below
                    </span>
                </div>
                """
            )

    # Interactive Action Buttons
    c_btn1, c_btn2, c_btn3 = st.columns([1.5, 1.2, 1.4], gap="small", vertical_alignment="center")

    with c_btn1:
        watch_btn_label = "Watched (Logged)" if is_watched else "Mark as watched"
        watch_btn_icon = ":material/check:" if is_watched else ":material/visibility:"
        if st.button(watch_btn_label, icon=watch_btn_icon, key=f"{key_prefix}_toggle_watched_{m_id}", use_container_width=True):
            now_watched = toggle_movie_watched({
                "id": m_id,
                "title": m_title,
                "release_year": m_year,
                "poster_url": m_poster,
            })
            if now_watched:
                st.toast(f"Logged '{m_title}' to your diary.")
            else:
                st.toast(f"Removed '{m_title}' from your diary.")
            st.rerun()

    with c_btn2:
        heart_label = "Liked" if is_liked else "Like"
        heart_icon = ":material/favorite:" if is_liked else ":material/favorite_border:"
        if st.button(heart_label, icon=heart_icon, key=f"{key_prefix}_toggle_liked_{m_id}", use_container_width=True):
            now_liked = toggle_movie_liked({
                "id": m_id,
                "title": m_title,
                "release_year": m_year,
                "poster_url": m_poster,
            })
            if now_liked:
                st.toast(f"Liked '{m_title}'.")
            else:
                st.toast(f"Unliked '{m_title}'.")
            st.rerun()

    with c_btn3:
        if is_watched:
            rating_opts = [5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0]
            curr_idx = rating_opts.index(user_rating) if user_rating in rating_opts else 1
            new_r = st.selectbox(
                "My Rating",
                options=rating_opts,
                index=curr_idx,
                format_func=lambda r: f"{format_letterboxd_stars(r)} ({r}★)",
                key=f"{key_prefix}_quick_rate_{m_id}",
                label_visibility="collapsed",
            )
            if new_r != user_rating:
                mark_movie_as_watched(
                    movie_id=m_id,
                    title=m_title,
                    year=m_year,
                    poster_url=m_poster,
                    rating=new_r,
                )
                st.toast(f"Rated '{m_title}' {new_r}★.")
                st.rerun()
        else:
            if st.button("Log & rate", icon=":material/star:", key=f"{key_prefix}_log_rate_{m_id}", use_container_width=True):
                mark_movie_as_watched(
                    movie_id=m_id,
                    title=m_title,
                    year=m_year,
                    poster_url=m_poster,
                    rating=5.0,
                )
                st.rerun()


def render_watched_movies_grid() -> None:
    """
    Render full interactive shelf of all dynamically logged watched movies.
    """
    from services.review_storage_service import (
        get_watched_stats,
        load_all_watched_movies,
        unmark_movie_as_watched,
    )

    watched_movies = load_all_watched_movies()
    stats = get_watched_stats()

    if not watched_movies:
        render_html(
            """
            <div style="background:var(--surface); border:1px dashed var(--line); border-radius:8px; padding:2rem; text-align:center;">
                <div style="font-size:2rem; margin-bottom:0.5rem;">👁️</div>
                <div style="font-family:var(--font-heading); font-size:1.15rem; font-weight:600; color:var(--ink);">
                    No movies logged in your diary yet
                </div>
                <div style="font-family:var(--font-body); font-size:0.9rem; color:var(--muted); margin-top:0.35rem;">
                    Select any title in 'Browse titles' or search for a film, then click <strong>'Mark as Watched'</strong> to start building your dynamic Letterboxd diary.
                </div>
            </div>
            """
        )
        return

    render_html(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem; flex-wrap:wrap; gap:0.5rem; border-bottom:1px solid var(--line); padding-bottom:0.75rem;">
            <div>
                <span class="badge-pos" style="font-size:0.8rem;">{stats['total_watched']} Films Watched</span>
                <span class="badge-neutral" style="font-size:0.8rem; margin-left:0.4rem;">{stats['liked_count']} Liked with 🧡</span>
            </div>
            <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--muted);">
                Dynamically stored in <code>data/user_watched_movies.json</code>
            </div>
        </div>
        """
    )

    n_cols = 4
    rows = [watched_movies[i : i + n_cols] for i in range(0, len(watched_movies), n_cols)]
    for r_idx, row in enumerate(rows):
        cols = st.columns(n_cols)
        for c_idx, m in enumerate(row):
            with cols[c_idx]:
                title = m.get("title", "Untitled")
                year = m.get("year", "N/A")
                poster = m.get("poster_url", "")
                w_date = m.get("formatted_date", "Logged")
                rating = m.get("rating")
                is_liked = m.get("is_liked", False)
                stars_html = f'<span style="color:#00e054; font-size:0.85rem;">{format_letterboxd_stars(rating)}</span>' if rating else ""
                heart_html = '<span style="color:#FF8000; font-size:0.85rem;">🧡</span>' if is_liked else ""

                img_html = (
                    f'<img src="{poster}" class="cinesense-poster-img" alt="{title}" loading="lazy" />'
                    if poster
                    else '<div class="cinesense-poster-placeholder"><span>🎬</span> No Poster</div>'
                )

                render_html(
                    f"""
                    <div class="cinesense-film-card">
                        <div class="cinesense-poster-frame">
                            {img_html}
                            <div class="cinesense-watched-poster-badge">👁️ Watched</div>
                        </div>
                        <div class="cinesense-card-content">
                            <div class="cinesense-film-title" title="{title}">{title}</div>
                            <div class="cinesense-film-meta">
                                <span>{year}</span>
                                <span>&bull;</span>
                                <span style="font-size:0.75rem;">{w_date}</span>
                            </div>
                            <div style="display:flex; align-items:center; gap:0.4rem; margin-top:0.25rem;">
                                {stars_html} {heart_html}
                            </div>
                        </div>
                    </div>
                    """
                )
                w_col1, w_col2 = st.columns([1, 1])
                with w_col1:
                    if st.button("Inspect film", key=f"watched_inspect_{m.get('movie_id', c_idx)}_{r_idx}_{c_idx}", use_container_width=True):
                        st.session_state["selected_movie_data"] = {
                            "id": m.get("movie_id"),
                            "title": title,
                            "release_year": year,
                            "poster_url": poster,
                        }
                        st.rerun()
                with w_col2:
                    if st.button("Unmark", key=f"watched_rm_{m.get('movie_id', c_idx)}_{r_idx}_{c_idx}", use_container_width=True):
                        unmark_movie_as_watched(m.get("movie_id"), title)
                        st.rerun()
                st.write("")



