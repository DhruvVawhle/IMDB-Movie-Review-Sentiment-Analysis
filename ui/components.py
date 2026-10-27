"""
Reusable UI components and Plotly chart generators for CineSense.
Adheres strictly to the calm, light-first analytics design system.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ui.theme import (
    FONT_BODY,
    FONT_HEADING,
    FONT_MONO,
    LIGHT_THEME,
    get_plotly_layout,
)
import streamlit.components.v1 as st_components

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
    col_left, col_right = st.columns([1.5, 1.3], gap="medium")

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
        b1, b2, b3 = st.columns([1.35, 1.35, 0.8], gap="small")

        with b1:
            if st.button("Analyze a review", type="primary", key="hdr_analyze_cta", use_container_width=True):
                set_active_tab("Analyzer")
                st.rerun()

        with b2:
            st.markdown('<div class="cinesense-ghost-btn">', unsafe_allow_html=True)
            if st.button("See model results", key="hdr_bench_cta", use_container_width=True):
                set_active_tab("Benchmarks")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with b3:
            curr_theme = st.session_state.get("theme_mode", "light")
            toggle_icon = ":material/dark_mode:" if curr_theme == "light" else ":material/light_mode:"
            toggle_label = "Dark" if curr_theme == "light" else "Light"
            st.markdown('<div class="cinesense-theme-toggle">', unsafe_allow_html=True)
            if st.button(toggle_label, icon=toggle_icon, key="hdr_theme_toggle", use_container_width=True):
                st.session_state["theme_mode"] = "dark" if curr_theme == "light" else "light"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)


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
    total = pos_count + neg_count
    pos_pct = (pos_count / total) * 100 if total else 50.0
    neg_pct = (neg_count / total) * 100 if total else 50.0

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=["Balance"],
        x=[pos_count],
        name=f"Positive ({pos_count:,})",
        orientation="h",
        marker=dict(color=LIGHT_THEME["pos"], line=dict(color="#FFFFFF", width=1)),
        text=f"Positive: {pos_count:,} ({pos_pct:.1f}%)",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(family="IBM Plex Sans", size=12, color="#FFFFFF"),
        hovertemplate="Positive: %{x:,} reviews (%{text})<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=["Balance"],
        x=[neg_count],
        name=f"Negative ({neg_count:,})",
        orientation="h",
        marker=dict(color=LIGHT_THEME["neg"], line=dict(color="#FFFFFF", width=1)),
        text=f"Negative: {neg_count:,} ({neg_pct:.1f}%)",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(family="IBM Plex Sans", size=12, color="#FFFFFF"),
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
        tickfont=dict(family="IBM Plex Mono", size=10, color=LIGHT_THEME["muted"]),
    )
    layout["yaxis"] = dict(showticklabels=False, showgrid=False)
    fig.update_layout(layout)
    return fig


def plot_length_histogram(df: pd.DataFrame) -> go.Figure:
    """Histogram comparing word count distributions for positive vs negative reviews with mean annotation."""
    fig = go.Figure()

    pos_lens = df[df["sentiment_clean"] == "positive"]["word_count"]
    neg_lens = df[df["sentiment_clean"] == "negative"]["word_count"]

    fig.add_trace(go.Histogram(
        x=pos_lens,
        name="Positive",
        nbinsx=45,
        marker_color=LIGHT_THEME["pos"],
        opacity=0.6,
        hovertemplate="Positive: %{y} reviews (~%{x} words)<extra></extra>",
    ))
    fig.add_trace(go.Histogram(
        x=neg_lens,
        name="Negative",
        nbinsx=45,
        marker_color=LIGHT_THEME["neg"],
        opacity=0.6,
        hovertemplate="Negative: %{y} reviews (~%{x} words)<extra></extra>",
    ))

    # Mean annotation at 231 words
    mean_val = 231.0
    fig.add_vline(
        x=mean_val,
        line_width=2,
        line_dash="dash",
        line_color=LIGHT_THEME["accent"],
        annotation_text="Mean 231 words",
        annotation_position="top right",
        annotation_font=dict(color=LIGHT_THEME["accent"], family="IBM Plex Mono", size=11),
    )

    layout = get_plotly_layout(height=280, barmode="overlay")
    layout["xaxis"]["title"] = "Word Count (HTML tags stripped)"
    layout["xaxis"]["range"] = [0, 900]
    layout["yaxis"]["title"] = "Review Frequency"
    fig.update_layout(layout)
    return fig


def plot_probability_meter(pos_prob: float, neg_prob: float) -> go.Figure:
    """Compact horizontal probability meter."""
    fig = go.Figure()
    pos_pct = round(pos_prob * 100, 1)
    neg_pct = round(neg_prob * 100, 1)

    fig.add_trace(go.Bar(
        y=["Score"],
        x=[pos_pct],
        name=f"Positive ({pos_pct}%)",
        orientation="h",
        marker=dict(color=LIGHT_THEME["pos"]),
        text=f"{pos_pct}% Positive" if pos_pct >= 20 else "",
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(family="IBM Plex Sans", size=11, color="#FFFFFF"),
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
    items = top_features.get(sentiment, [])[:top_n]
    if not items:
        return go.Figure()

    terms = [item["term"] for item in reversed(items)]
    weights = [abs(item["weight"]) for item in reversed(items)]
    color = LIGHT_THEME["pos"] if sentiment == "positive" else LIGHT_THEME["neg"]

    fig = go.Figure(go.Bar(
        x=weights,
        y=terms,
        orientation="h",
        marker=dict(color=color),
        text=[f"{w:.2f}" for w in weights],
        textposition="outside",
        textfont=dict(family="IBM Plex Mono", color=LIGHT_THEME["ink"], size=11),
        hovertemplate="<b>%{y}</b>: %{x:.3f} separation weight<extra></extra>",
    ))

    layout = get_plotly_layout(height=340, margin=dict(l=90, r=40, t=10, b=35))
    layout["xaxis"]["title"] = "TF-IDF Logistic Regression Magnitude"
    fig.update_layout(layout)
    return fig


def plot_top_features_divergent(top_features: Dict[str, List[Dict[str, Any]]], top_n: int = 12) -> go.Figure:
    """Divergent horizontal bar chart showing top positive and negative vocabulary coefficients."""
    pos_items = top_features.get("positive", [])[:top_n]
    neg_items = top_features.get("negative", [])[:top_n]

    terms = [item["term"] for item in reversed(pos_items)] + [item["term"] for item in neg_items]
    weights = [item["weight"] for item in reversed(pos_items)] + [item["weight"] for item in neg_items]
    colors = [LIGHT_THEME["pos"] if w > 0 else LIGHT_THEME["neg"] for w in weights]

    fig = go.Figure(go.Bar(
        x=weights,
        y=terms,
        orientation="h",
        marker=dict(color=colors),
        text=[f"{w:+.2f}" for w in weights],
        textposition="outside",
        textfont=dict(family="IBM Plex Mono", size=10, color=LIGHT_THEME["ink"]),
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
    fig = go.Figure()

    metric_series = [
        ("Accuracy (%)", LIGHT_THEME["accent"]),
        ("Precision (%)", LIGHT_THEME["pos"]),
        ("Recall (%)", "#2B6CB0"),
        ("F1-Score (%)", "#6B46C1"),
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
    fig = go.Figure()
    palette = [LIGHT_THEME["accent"], "#2B6CB0", LIGHT_THEME["pos"]]
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
        line=dict(color=LIGHT_THEME["muted"], width=1.5, dash="dash"),
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
        textfont=dict(family="IBM Plex Sans", size=12, color=LIGHT_THEME["ink"]),
        colorscale=[
            [0.0, "#FFFFFF"],
            [0.3, "#E8F4F1"],
            [1.0, "#BFE5DA"],
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
        badge_html = '<span class="badge-neutral" style="color:var(--pos); background:var(--pos-bg); border-color:var(--pos-border); font-weight:600;">🟢 LIVE OPENROUTER LLM</span>'
    else:
        badge_html = '<span class="badge-neutral" style="color:var(--warn); background:var(--warn-bg); border-color:var(--warn-border); font-weight:600;">🟡 OFFLINE NLP ENGINE</span>'

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
            <div style="display:flex; justify-content:space-between; align-items:flex-start; padding:0.4rem 0.55rem; background:var(--bg); border-radius:4px; margin-bottom:0.35rem; border:1px solid var(--line);">
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
            <div style="background:var(--bg); border-radius:6px; padding:0.75rem 0.9rem; margin-bottom:0.85rem; border-left:3px solid var(--accent);">
                <div style="font-family:var(--font-mono); font-size:0.7rem; text-transform:uppercase; color:var(--muted); margin-bottom:0.25rem;">Contextual Summary</div>
                <div style="font-family:var(--font-body); font-size:0.9rem; color:var(--ink); font-style:italic; line-height:1.45;">
                    "{summary}"
                </div>
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:0.5rem; margin-bottom:0.75rem;">
                <div style="background:var(--bg); padding:0.5rem 0.75rem; border-radius:4px; border:1px solid var(--line);">
                    <div style="font-family:var(--font-mono); font-size:0.68rem; text-transform:uppercase; color:var(--muted);">Tone & Mood</div>
                    <div style="font-family:var(--font-heading); font-size:0.92rem; font-weight:600; color:var(--ink); margin-top:0.15rem;">{tone}</div>
                </div>
                <div style="background:var(--bg); padding:0.5rem 0.75rem; border-radius:4px; border:1px solid var(--line);">
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
    if not features:
        fig = go.Figure()
        fig.update_layout(get_plotly_layout(height=180))
        return fig

    # Sort so negative are at top, positive at bottom (or vice versa)
    sorted_features = sorted(features, key=lambda x: x[1])
    terms = [str(item[0]) for item in sorted_features]
    weights = [float(item[1]) for item in sorted_features]
    colors = [LIGHT_THEME["pos"] if w > 0 else LIGHT_THEME["neg"] for w in weights]

    fig = go.Figure(go.Bar(
        x=weights,
        y=terms,
        orientation="h",
        marker=dict(color=colors),
        text=[f"{w:+.2f}" for w in weights],
        textposition="outside",
        textfont=dict(family="IBM Plex Mono", size=10, color=LIGHT_THEME["ink"]),
        hoverinfo="x+y",
    ))

    layout = get_plotly_layout(height=max(220, len(features) * 26 + 60), margin=dict(l=100, r=40, t=15, b=40))
    layout["xaxis"]["title"] = "LIME Contribution Weight (Negative ← 0 → Positive)"
    layout["xaxis"]["zeroline"] = True
    layout["xaxis"]["zerolinecolor"] = LIGHT_THEME["line"]
    layout["xaxis"]["zerolinewidth"] = 1.5
    fig.update_layout(layout)
    return fig


def plot_failure_patterns_bar(patterns: List[Dict[str, Any]], overall_error_rate: float) -> go.Figure:
    """Horizontal bar chart comparing failure pattern error rates against overall test baseline."""
    names = [p["pattern"] for p in reversed(patterns)]
    rates = [p["error_rate"] for p in reversed(patterns)]
    counts = [p["count"] for p in reversed(patterns)]

    colors = [
        LIGHT_THEME["neg"] if r > overall_error_rate else LIGHT_THEME["accent"]
        for r in rates
    ]

    fig = go.Figure(go.Bar(
        x=rates,
        y=names,
        orientation="h",
        marker=dict(color=colors),
        text=[f"{r:.1f}% (N={c:,})" for r, c in zip(rates, counts)],
        textposition="outside",
        textfont=dict(family="IBM Plex Mono", size=11, color=LIGHT_THEME["ink"]),
        hoverinfo="x+y",
    ))

    # Add vertical dashed line for overall error rate baseline
    fig.add_vline(
        x=overall_error_rate,
        line_dash="dash",
        line_color=LIGHT_THEME["muted"],
        line_width=1.5,
        annotation_text=f"Baseline ({overall_error_rate:.1f}%)",
        annotation_position="top right",
        annotation_font=dict(family="IBM Plex Mono", size=10, color=LIGHT_THEME["muted"]),
    )

    layout = get_plotly_layout(height=260, margin=dict(l=220, r=90, t=25, b=40))
    layout["xaxis"]["title"] = "Subset Classification Error Rate (%)"
    layout["xaxis"]["ticksuffix"] = "%"
    fig.update_layout(layout)
    return fig

