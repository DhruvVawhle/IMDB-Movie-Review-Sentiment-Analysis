"""
Overview Tab for CineSense.
Presents one-line intro, single CTA, 4-number KPI strip, class balance split bar,
length histogram, model results table with highlighted best values, and 7-step pipeline strip.
"""

import streamlit as st
from services.data_service import get_dataset_statistics, load_imdb_dataset
from services.evaluation_service import get_formatted_comparison_dataframe
from ui.components import (
    plot_length_histogram,
    plot_split_class_bar,
    render_kpi_strip,
    render_pipeline_strip,
    set_active_tab,
)


def render_overview_tab() -> None:
    # 1. One-line intro
    st.markdown(
        '<p class="cinesense-takeaway" style="font-size:1.05rem; color:var(--ink); margin-bottom: 1.25rem;">'
        'Benchmark sentiment analytics on 50,000 Stanford IMDB reviews across three natural language architectures.'
        '</p>',
        unsafe_allow_html=True,
    )

    # Single Call-to-Action button
    col_cta, _ = st.columns([1.5, 4])
    with col_cta:
        if st.button("Analyze a review →", type="primary", use_container_width=True):
            set_active_tab("Analyzer")
            st.rerun()

    st.write("")

    # 2. 4-number KPI strip
    stats = get_dataset_statistics()
    render_kpi_strip(
        total=stats.get("total_samples", 50000),
        pos=stats.get("positive_count", 25000),
        neg=stats.get("negative_count", 25000),
        mean_words=stats.get("avg_word_count", 231.0),
        median_words=stats.get("median_word_count", 173),
    )

    st.write("")

    # 3. Class balance split bar (replaces two-bar chart)
    st.markdown('<div class="cinesense-section-title">Class balance</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cinesense-takeaway">Equal 50% split across 25,000 positive and 25,000 negative reviews sharing a central dividing edge.</div>',
        unsafe_allow_html=True,
    )
    fig_split = plot_split_class_bar(stats.get("positive_count", 25000), stats.get("negative_count", 25000))
    st.plotly_chart(fig_split, use_container_width=True)

    # 4. Review length distribution histogram
    st.markdown('<div class="cinesense-section-title">Review length distribution</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cinesense-takeaway">Reviews are short with a mean of 231 words and a long positive-skewed tail extending beyond 800 words.</div>',
        unsafe_allow_html=True,
    )
    df_sample, _ = load_imdb_dataset(limit=5000)
    if df_sample is not None:
        fig_hist = plot_length_histogram(df_sample)
        st.plotly_chart(fig_hist, use_container_width=True)

    # 5. Model results table
    st.markdown('<div class="cinesense-section-title">Model benchmark results</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cinesense-takeaway">Logistic Regression with TF-IDF attains the top accuracy (89.6%) and ROC-AUC (0.961) on 10,000 unseen test reviews (best column values marked with ▲).</div>',
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
        st.info("Evaluation metrics unavailable. Please verify model weights are trained.")

    # 6. 7-step pipeline as horizontal strip
    st.markdown('<div class="cinesense-section-title">NLP processing pipeline</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cinesense-takeaway">Standard seven-stage transformation applied to convert raw HTML review text into calibrated sentiment odds.</div>',
        unsafe_allow_html=True,
    )
    render_pipeline_strip()

    # 7. Model limitations & operational scope
    st.write("")
    with st.expander("Model limitations & operational scope", expanded=False):
        st.markdown(
            """
            <div style="font-family:var(--font-body); font-size:0.9rem; line-height:1.6; color:var(--ink);">
                <ul>
                    <li><strong>English only:</strong> The NLP preprocessing pipeline (tokenization, stopword removal, and WordNet lemmatization) is built exclusively for English reviews. Non-English submissions will produce uncalibrated tokens.</li>
                    <li><strong>IMDB-only training:</strong> Models were trained on the Stanford 50,000 IMDB dataset. Vocabulary and style differences from other platforms (Letterboxd, Rotten Tomatoes, Twitter/X) may cause distribution shift.</li>
                    <li><strong>Sarcasm and negation errors:</strong> Sarcastic remarks ("Truly a masterpiece of bad cinema") and multi-clause negations can mislead linear bag-of-words and TF-IDF representations.</li>
                    <li><strong>No neutral class:</strong> The classification task is formulated as strictly binary (Positive vs Negative). Ambivalent or neutral (5/10) reviews are forced into one of the two classes.</li>
                    <li><strong>Results on non-IMDB text are experimental:</strong> Generalization to out-of-domain text (e.g. consumer product reviews, customer support tickets) is experimental and not guaranteed.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

