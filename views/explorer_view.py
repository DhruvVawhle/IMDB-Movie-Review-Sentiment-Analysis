"""
Dataset Explorer View for CineSense.
Allows searching, filtering, paginated exploration, distinctive word separation,
and CSV exporting over the 50,000 review IMDB dataset.
"""

import streamlit as st
import pandas as pd
from services.data_service import filter_dataset, get_dataset_statistics, load_imdb_dataset
from services.evaluation_service import load_top_predictive_features
from components.visualizations import (
    generate_wordcloud_image,
    plot_distinctive_words_bar,
    plot_review_length_distribution,
)


def render_explorer():
    st.markdown('<h2 class="editorial-heading">Dataset explorer</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="editorial-subheading">'
        'Search, filter and page through the labeled reviews. Examples below are sample rows.'
        '</p>',
        unsafe_allow_html=True,
    )

    df_full, err = load_imdb_dataset()
    if df_full is None:
        st.error(f"Unable to load dataset: {err}")
        return

    # Filter Bar
    c_search, c_sent, c_limit = st.columns([2.5, 1.2, 1.3])
    with c_search:
        search_query = st.text_input("Search text", placeholder="Filter by keyword (e.g. 'masterpiece', 'disappointing')...")
    with c_sent:
        sentiment_filter = st.selectbox("Sentiment", options=["all", "positive", "negative"], format_func=lambda x: x.capitalize())
    with c_limit:
        page_size = st.selectbox("Rows per page", options=[10, 25, 50, 100], index=1)

    # Apply filters
    filtered_df = filter_dataset(
        df_full,
        sentiment_filter=sentiment_filter,
        search_query=search_query,
    )

    total_filtered = len(filtered_df)
    st.markdown(
        f'<p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.75rem;">'
        f'Showing <strong>{total_filtered:,}</strong> matching reviews out of 50,000 total.'
        f'</p>',
        unsafe_allow_html=True,
    )

    # Pagination controls
    total_pages = max(1, (total_filtered + page_size - 1) // page_size)
    page_col1, page_col2, page_col3 = st.columns([1, 2, 1])
    with page_col2:
        current_page = st.number_input(
            f"Page (1 to {total_pages})",
            min_value=1,
            max_value=total_pages,
            value=1,
            step=1,
        )

    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, total_filtered)

    display_df = filtered_df.iloc[start_idx:end_idx][["sentiment", "word_count", "char_count", "review"]]
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "sentiment": st.column_config.TextColumn("Sentiment", width="small"),
            "word_count": st.column_config.NumberColumn("Words", width="small"),
            "char_count": st.column_config.NumberColumn("Characters", width="small"),
            "review": st.column_config.TextColumn("Review Content", width="large"),
        },
    )

    # CSV Export Button
    export_df = filtered_df.head(5000)[["review", "sentiment", "word_count"]]
    csv_bytes = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"Download Filtered Results as CSV (Up to 5,000 rows)",
        data=csv_bytes,
        file_name="cinesense_imdb_filtered_reviews.csv",
        mime="text/csv",
    )

    # Section: Most distinctive words
    st.markdown('<h2 class="editorial-heading" style="font-size:1.35rem; margin-top:2.5rem;">Most distinctive words</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="editorial-subheading">'
        'Ranked by how strongly each word separates the classes. These replace the word clouds, which are hard to read and hide the numbers.'
        '</p>',
        unsafe_allow_html=True,
    )

    # Data issue callout
    st.markdown(
        """
        <div class="cinesense-panel" style="border-left: 3px solid var(--accent-amber); margin-bottom: 1.25rem;">
            <div class="cinesense-panel-body" style="color: var(--text-primary); font-size: 0.9rem;">
                <strong>Data issue to fix:</strong> the word clouds were dominated by <code>br</code>, left over from <code>&lt;br /&gt;</code> tags.
                Strip tags before counting words and it disappears from both charts.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    top_feats, err = load_top_predictive_features()
    if top_feats:
        c_pos, c_neg = st.columns(2)
        with c_pos:
            st.markdown('<h4 style="color:var(--sentiment-pos-fg); font-weight:600; margin-bottom:0.25rem;">Positive reviews</h4>', unsafe_allow_html=True)
            fig_pos = plot_distinctive_words_bar(top_feats, sentiment="positive", top_n=12)
            st.plotly_chart(fig_pos, use_container_width=True)

        with c_neg:
            st.markdown('<h4 style="color:var(--sentiment-neg-fg); font-weight:600; margin-bottom:0.25rem;">Negative reviews</h4>', unsafe_allow_html=True)
            fig_neg = plot_distinctive_words_bar(top_feats, sentiment="negative", top_n=12)
            st.plotly_chart(fig_neg, use_container_width=True)
    else:
        st.info("Distinctive feature statistics not found.")

    # Review length distribution
    with st.expander("Explore Review Length Distributions (Word Count Histogram)"):
        fig_len = plot_review_length_distribution(filtered_df if len(filtered_df) > 100 else df_full)
        st.plotly_chart(fig_len, use_container_width=True)

