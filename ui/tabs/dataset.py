"""
Dataset Explorer Tab for CineSense.
One-row filter bar (search, sentiment, rows per page), pill badges for sentiment,
Previous/Next pagination with 'Page X of Y', CSV export, and ranked horizontal bar charts
of the most distinctive words per class (replacing noisy word clouds).
"""

import streamlit as st
import pandas as pd
from services.data_service import filter_dataset, load_imdb_dataset
from services.evaluation_service import load_top_predictive_features
from ui.components import plot_distinctive_words_bar


def render_dataset_tab() -> None:
    st.markdown(
        '<p class="cinesense-takeaway" style="font-size:1.05rem; color:var(--ink); margin-bottom: 1.25rem;">'
        'Explore, filter, and inspect the 50,000 Stanford IMDB benchmark reviews. HTML tags (&lt;br /&gt;) are stripped during ingestion.'
        '</p>',
        unsafe_allow_html=True,
    )

    df_full, err = load_imdb_dataset()
    if df_full is None:
        st.error(f"Unable to load dataset: {err}")
        return

    # 1. Filters in ONE row (search, sentiment, rows per page)
    f_search, f_sent, f_size = st.columns([2.4, 1.2, 1.2])
    with f_search:
        search_query = st.text_input(
            "Search text",
            placeholder="Search keyword (e.g. Nolan, masterpiece, boring)...",
            label_visibility="collapsed",
        )
    with f_sent:
        sentiment_filter = st.selectbox(
            "Sentiment",
            options=["all", "positive", "negative"],
            format_func=lambda x: "All sentiments" if x == "all" else f"{x.capitalize()} only",
            label_visibility="collapsed",
        )
    with f_size:
        page_size = st.selectbox(
            "Rows per page",
            options=[10, 25, 50, 100],
            index=1,
            format_func=lambda x: f"{x} rows / page",
            label_visibility="collapsed",
        )

    filtered_df = filter_dataset(
        df_full,
        sentiment_filter=sentiment_filter,
        search_query=search_query,
    )

    total_filtered = len(filtered_df)
    total_pages = max(1, (total_filtered + page_size - 1) // page_size)

    # Manage pagination state
    if "dataset_page" not in st.session_state:
        st.session_state["dataset_page"] = 1
    if st.session_state["dataset_page"] > total_pages:
        st.session_state["dataset_page"] = total_pages

    current_page = st.session_state["dataset_page"]

    # Table takeaway sentence
    st.markdown(
        f'<div class="cinesense-takeaway" style="margin-top:0.75rem;">'
        f'Displaying <strong>{total_filtered:,}</strong> matching reviews out of 50,000 total benchmark samples '
        f'(Page {current_page} of {total_pages}).'
        f'</div>',
        unsafe_allow_html=True,
    )

    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, total_filtered)
    page_df = filtered_df.iloc[start_idx:end_idx].copy()

    # Add pill badge representation
    page_df["sentiment_badge"] = page_df["sentiment_clean"].apply(
        lambda s: "POS" if s == "positive" else "NEG"
    )

    display_df = page_df[["sentiment_badge", "word_count", "char_count", "review"]]

    # Dataframe rendering
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "sentiment_badge": st.column_config.TextColumn("Class", width="small"),
            "word_count": st.column_config.NumberColumn("Words", width="small"),
            "char_count": st.column_config.NumberColumn("Chars", width="small"),
            "review": st.column_config.TextColumn("Review text", width="large"),
        },
    )

    # 2. Pagination bar: Previous, "Page X of Y", Next, and CSV Download in one row
    col_prev, col_info, col_next, col_download = st.columns([1, 1.8, 1, 2.5])
    with col_prev:
        if st.button("← Previous", disabled=(current_page <= 1), use_container_width=True):
            st.session_state["dataset_page"] = max(1, current_page - 1)
            st.rerun()
    with col_info:
        st.markdown(
            f'<div style="text-align:center; font-family:var(--font-mono); font-size:0.85rem; padding-top:0.4rem; color:var(--muted);">'
            f'Page {current_page} of {total_pages}'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col_next:
        if st.button("Next →", disabled=(current_page >= total_pages), use_container_width=True):
            st.session_state["dataset_page"] = min(total_pages, current_page + 1)
            st.rerun()
    with col_download:
        export_df = filtered_df.head(5000)[["review", "sentiment", "word_count"]]
        csv_bytes = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Filtered CSV (Up to 5k)",
            data=csv_bytes,
            file_name="cinesense_filtered_reviews.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # 3. Ranked horizontal bar charts of most distinctive words (replaces word clouds)
    st.markdown('<div class="cinesense-section-title" style="margin-top:2rem;">Most distinctive vocabulary per class</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cinesense-takeaway">Separation weights from fitted Logistic Regression coefficients. Word clouds have been replaced by quantitative ranked bar charts, eliminating residual &lt;br /&gt; tags.</div>',
        unsafe_allow_html=True,
    )

    top_feats, err = load_top_predictive_features()
    if top_feats:
        c_pos, c_neg = st.columns(2)
        with c_pos:
            st.markdown(
                '<div style="font-family:var(--font-heading); font-size:1rem; font-weight:600; color:var(--pos); margin-bottom:0.25rem;">'
                'Positive class distinctive terms'
                '</div>',
                unsafe_allow_html=True,
            )
            fig_pos = plot_distinctive_words_bar(top_feats, sentiment="positive", top_n=12)
            st.plotly_chart(fig_pos, use_container_width=True)

        with c_neg:
            st.markdown(
                '<div style="font-family:var(--font-heading); font-size:1rem; font-weight:600; color:var(--neg); margin-bottom:0.25rem;">'
                'Negative class distinctive terms'
                '</div>',
                unsafe_allow_html=True,
            )
            fig_neg = plot_distinctive_words_bar(top_feats, sentiment="negative", top_n=12)
            st.plotly_chart(fig_neg, use_container_width=True)
    else:
        st.info("Predictive feature statistics unavailable.")

