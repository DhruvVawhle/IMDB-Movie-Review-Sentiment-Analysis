"""
Overview Dashboard View for CineSense.
Presents editorial introduction, verified dataset characteristics,
model benchmark summary, and workflow navigation.
"""

import streamlit as st
from services.data_service import get_dataset_statistics, load_imdb_dataset
from services.evaluation_service import get_comparison_dataframe, load_evaluation_summary
from components.visualizations import plot_sentiment_distribution, plot_review_length_distribution


"""
Overview Dashboard View for CineSense.
Presents editorial introduction, verified dataset characteristics,
model benchmark summary, and workflow navigation.
"""

import streamlit as st
from services.data_service import get_dataset_statistics, load_imdb_dataset
from services.evaluation_service import get_comparison_dataframe, get_formatted_comparison_dataframe, load_evaluation_summary
from components.visualizations import plot_sentiment_distribution, plot_review_length_distribution


def render_overview():
    st.markdown('<h2 class="editorial-heading">CineSense — Movie review intelligence</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="editorial-subheading">'
        'Sentiment analysis on 50,000 IMDB reviews, comparing three models. Academic data science project (RGPL syllabus).'
        '</p>',
        unsafe_allow_html=True,
    )

    # "Try it on your own review" Callout Banner
    st.markdown(
        """
        <div class="cinesense-panel" style="border-left: 3px solid var(--accent-amber); margin-bottom: 1.5rem;">
            <div class="cinesense-panel-title" style="color: var(--accent-amber); font-size: 1.05rem;">
                Try it on your own review
            </div>
            <div class="cinesense-panel-body">
                Paste any movie review and see what Logistic Regression, Naive Bayes and BiLSTM each predict.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_try, _ = st.columns([1.5, 3])
    with col_try:
        if st.button("Launch Review Analyzer →", use_container_width=True, type="primary"):
            st.session_state["nav_page"] = "analyzer"
            st.rerun()

    # KPI Summary Cards
    stats = get_dataset_statistics()
    st.write("")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-label">Reviews</div>'
            f'<div class="stat-value">{stats["total_samples"]:,}</div>'
            f'<div class="stat-desc">Stanford IMDB benchmark</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-label">Positive</div>'
            f'<div class="stat-value" style="color:var(--sentiment-pos-fg);">{stats["positive_count"]:,}</div>'
            f'<div class="stat-desc">{stats["pos_percentage"]:.0f}%</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-label">Negative</div>'
            f'<div class="stat-value" style="color:var(--sentiment-neg-fg);">{stats["negative_count"]:,}</div>'
            f'<div class="stat-desc">{stats["neg_percentage"]:.0f}%</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-label">Mean length</div>'
            f'<div class="stat-value">{stats["avg_word_count"]:.0f} words</div>'
            f'<div class="stat-desc">Median {stats["median_word_count"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Section: Reviews are short, and skewed long
    st.markdown('<h2 class="editorial-heading" style="font-size:1.35rem; margin-top:1.5rem;">Reviews are short, and skewed long</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="editorial-subheading">'
        'Most reviews run 100 to 250 words, with a long tail past 1,000. The classes are perfectly balanced, so accuracy is a fair headline metric.'
        '</p>',
        unsafe_allow_html=True,
    )
    df, _ = load_imdb_dataset(limit=5000)
    if df is not None:
        fig_len = plot_review_length_distribution(df)
        st.plotly_chart(fig_len, use_container_width=True)

    # Section: Class balance
    st.markdown('<h2 class="editorial-heading" style="font-size:1.35rem; margin-top:1.5rem;">Class balance</h2>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="editorial-subheading">'
        f'Positive <strong>{stats["positive_count"]:,}</strong> &nbsp;|&nbsp; Negative <strong>{stats["negative_count"]:,}</strong><br>'
        f'<span style="font-size:0.85rem; color:var(--text-dim);">'
        f'One bar replaces the two-bar chart. Equal halves are easier to compare when they share an edge.'
        f'</span>'
        f'</p>',
        unsafe_allow_html=True,
    )
    fig_dist = plot_sentiment_distribution(stats["positive_count"], stats["negative_count"])
    st.plotly_chart(fig_dist, use_container_width=True)

    # Section: Model results
    st.markdown('<h2 class="editorial-heading" style="font-size:1.35rem; margin-top:1.5rem;">Model results</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="editorial-subheading">'
        'Scored on 10,000 held-out reviews. A triangle marks the best value in each column.'
        '</p>',
        unsafe_allow_html=True,
    )
    comp_df = get_formatted_comparison_dataframe()
    if comp_df is not None:
        st.dataframe(
            comp_df[["Model", "Accuracy (%)", "Precision (%)", "Recall (%)", "F1-Score (%)", "ROC-AUC", "Feature Extraction"]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Model results not found. Please verify fitted models are present.")

    # Section: How a review becomes a prediction
    st.markdown('<h2 class="editorial-heading" style="font-size:1.35rem; margin-top:2rem;">How a review becomes a prediction</h2>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 0.75rem; margin-top: 0.5rem; margin-bottom: 1.5rem;">
            <div class="cinesense-panel" style="margin-bottom:0;">
                <div class="cinesense-panel-title">1. Ingest</div>
                <div class="cinesense-panel-body">Raw text with HTML tags and links</div>
            </div>
            <div class="cinesense-panel" style="margin-bottom:0;">
                <div class="cinesense-panel-title">2. Sanitize</div>
                <div class="cinesense-panel-body">Strip markup, entities and URLs</div>
            </div>
            <div class="cinesense-panel" style="margin-bottom:0;">
                <div class="cinesense-panel-title">3. Normalize</div>
                <div class="cinesense-panel-body">Lowercase, letters only</div>
            </div>
            <div class="cinesense-panel" style="margin-bottom:0;">
                <div class="cinesense-panel-title">4. Tokenize</div>
                <div class="cinesense-panel-body">NLTK tokens, drop stopwords</div>
            </div>
            <div class="cinesense-panel" style="margin-bottom:0;">
                <div class="cinesense-panel-title">5. Lemmatize</div>
                <div class="cinesense-panel-body">WordNet base forms</div>
            </div>
            <div class="cinesense-panel" style="margin-bottom:0;">
                <div class="cinesense-panel-title">6. Vectorize</div>
                <div class="cinesense-panel-body">TF-IDF, counts, or sequences</div>
            </div>
            <div class="cinesense-panel" style="margin-bottom:0;">
                <div class="cinesense-panel-title">7. Evaluate</div>
                <div class="cinesense-panel-body">Calibrated odds on held-out data</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

