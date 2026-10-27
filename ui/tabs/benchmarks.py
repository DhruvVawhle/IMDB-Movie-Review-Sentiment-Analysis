"""
Model Benchmarks Tab for CineSense.
Results table with best values marked, grouped bar chart with y-axis starting at 60%,
ROC comparison curves, and confusion matrix with labeled axes and percentages
beside a plain-language diagnostic note per model.
"""

import streamlit as st
import html
from services.evaluation_service import (
    compute_failure_patterns,
    get_available_models_meta,
    get_comparison_dataframe,
    get_formatted_comparison_dataframe,
    get_model_confusion_matrix,
    load_evaluation_summary,
    load_test_predictions,
)
from ui.components import (
    plot_benchmarks_bar_chart,
    plot_confusion_matrix,
    plot_failure_patterns_bar,
    plot_roc_curves,
    render_empty_state,
    set_active_tab,
)

MODEL_EXPLANATIONS = {
    "logistic_regression": (
        "Logistic Regression with TF-IDF features attains the highest overall accuracy (89.6%) and ROC-AUC (0.961). "
        "Its false positive and false negative error rates are nearly symmetrical on 10,000 unseen test reviews, "
        "making it the most stable production baseline for binary review classification."
    ),
    "naive_bayes": (
        "Multinomial Naive Bayes demonstrates rapid training speed and strong positive recall (91.8%), but exhibits a higher "
        "false positive rate (15.2%). The conditional independence assumption tends to over-index on isolated positive tokens "
        "when context is negated."
    ),
    "bilstm": (
        "The Bidirectional LSTM (BiLSTM) processes sequences in both forward and backward temporal order over learned word embeddings, "
        "achieving 87.8% accuracy. It excels at recognizing syntactic reversals (e.g., 'not good') without requiring hand-crafted n-gram rules."
    ),
}


def render_benchmarks_tab() -> None:
    st.markdown(
        '<p class="cinesense-takeaway" style="font-size:1.05rem; color:var(--ink); margin-bottom: 1.25rem;">'
        'Standardized evaluation on 10,000 unseen, stratified test reviews. All models were trained exclusively on 40,000 reviews with zero data leakage.'
        '</p>',
        unsafe_allow_html=True,
    )

    summary, err = load_evaluation_summary()
    if not summary or "models" not in summary:
        st.error(err or "Evaluation summary metadata unavailable.")
        return

    # 1. Results Table with best values marked
    st.markdown('<div class="cinesense-section-title">Comparative test metrics</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cinesense-takeaway">Logistic Regression achieves top scores in Accuracy, Precision, F1-Score, and ROC-AUC (highest column values marked with ▲).</div>',
        unsafe_allow_html=True,
    )

    comp_df = get_comparison_dataframe()
    formatted_df = get_formatted_comparison_dataframe(comp_df)
    if formatted_df is not None:
        st.dataframe(
            formatted_df[["Model", "Accuracy (%)", "Precision (%)", "Recall (%)", "F1-Score (%)", "ROC-AUC", "Feature Extraction"]],
            use_container_width=True,
            hide_index=True,
        )

    # 2. Grouped bar chart (y-axis baseline starts at 60% and says so)
    if comp_df is not None:
        st.markdown('<div class="cinesense-section-title" style="margin-top:1.75rem;">Metric comparison across architectures</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="cinesense-takeaway">Visual comparison across Accuracy, Precision, Recall, and F1. Note: Y-axis baseline begins at 60% to highlight variance between models.</div>',
            unsafe_allow_html=True,
        )
        fig_bar = plot_benchmarks_bar_chart(comp_df)
        st.plotly_chart(fig_bar, use_container_width=True)

    # 3. ROC Chart
    st.markdown('<div class="cinesense-section-title" style="margin-top:2rem;">Receiver operating characteristic (ROC)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cinesense-takeaway">True Positive Rate vs False Positive Rate across all classification thresholds against the diagonal random chance baseline.</div>',
        unsafe_allow_html=True,
    )
    fig_roc = plot_roc_curves(summary["models"])
    st.plotly_chart(fig_roc, use_container_width=True)

    # 4. Confusion matrix with labeled axes and percentages beside short plain-language note
    st.markdown('<div class="cinesense-section-title" style="margin-top:2rem;">Confusion matrix & diagnostics</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cinesense-takeaway">Actual vs predicted counts and percentages on the 10,000 review test split alongside architecture diagnosis.</div>',
        unsafe_allow_html=True,
    )

    models_meta = get_available_models_meta()
    available_keys = [k for k, v in models_meta.items() if v.get("status") == "available"]

    selected_model_key = st.selectbox(
        "Select model to inspect confusion matrix",
        options=available_keys,
        format_func=lambda k: models_meta[k].get("name", k),
        label_visibility="collapsed",
    )

    if selected_model_key:
        cm_data = get_model_confusion_matrix(selected_model_key)
        m_info = models_meta[selected_model_key]

        cm_col, note_col = st.columns([1.2, 1.0], gap="large")
        with cm_col:
            if cm_data:
                fig_cm = plot_confusion_matrix(cm_data, m_info.get("name", selected_model_key))
                st.plotly_chart(fig_cm, use_container_width=True)
            else:
                st.info("Confusion matrix data unavailable for selected model.")

        with note_col:
            plain_note = MODEL_EXPLANATIONS.get(
                selected_model_key,
                "Evaluation diagnostics evaluated on held-out test data."
            )
            st.markdown(
                f"""
                <div class="cinesense-card" style="margin-top: 0.5rem;">
                    <div style="font-family:var(--font-heading); font-size:1.1rem; font-weight:600; color:var(--ink); margin-bottom:0.4rem;">
                        {m_info.get('name', selected_model_key)} Analysis
                    </div>
                    <div style="font-family:var(--font-body); font-size:0.88rem; color:var(--muted); line-height:1.5; margin-bottom:0.75rem;">
                        {plain_note}
                    </div>
                    <div style="font-family:var(--font-mono); font-size:0.8rem; color:var(--ink); border-top:1px solid var(--line); padding-top:0.6rem;">
                        <div>Representation: <strong>{m_info.get('feature_extractor', 'N/A')}</strong></div>
                        <div>Test Accuracy: <strong>{m_info.get('accuracy', 0)*100:.2f}%</strong></div>
                        <div>F1 Harmonic Score: <strong>{m_info.get('f1', 0)*100:.2f}%</strong></div>
                        <div>ROC Area Under Curve: <strong>{m_info.get('roc_auc', 0):.4f}</strong></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # -----------------------------------------------------------------
    # Section 2: EMPIRICAL ERROR ANALYSIS
    # -----------------------------------------------------------------
    st.markdown('<div class="cinesense-section-title" style="margin-top:2.75rem;">Empirical error analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cinesense-takeaway">'
        'Comprehensive breakdown of model mistakes across the 10,000 held-out test reviews. '
        'Inspect architectural consensus, failure conditions, and specific misclassified reviews.'
        '</div>',
        unsafe_allow_html=True,
    )

    preds_df, preds_err = load_test_predictions()
    if preds_df is None or preds_df.empty:
        render_empty_state(
            "Test predictions dataset missing",
            f"{preds_err or 'No prediction data found.'}<br /><br />"
            "Generate offline test predictions by running:<br />"
            "<code style='background:var(--surface); padding:2px 6px; border-radius:4px;'>python scripts/export_predictions.py</code>",
        )
        return

    # a. Agreement Strip
    all_right = int(((preds_df["lr_pred"] == preds_df["label"]) & (preds_df["nb_pred"] == preds_df["label"]) & (preds_df["lstm_pred"] == preds_df["label"])).sum())
    all_wrong = int(((preds_df["lr_pred"] != preds_df["label"]) & (preds_df["nb_pred"] != preds_df["label"]) & (preds_df["lstm_pred"] != preds_df["label"])).sum())
    disagree = len(preds_df) - all_right - all_wrong

    st.markdown(
        f'<div class="cinesense-takeaway" style="margin-bottom:0.75rem;">'
        f'All three architectures reach unanimous consensus on {(all_right + all_wrong) / len(preds_df) * 100:.1f}% of reviews '
        f'({all_right:,} all correct, {all_wrong:,} all wrong), while disagreeing on {disagree:,} borderline cases.'
        f'</div>',
        unsafe_allow_html=True,
    )

    agr_col1, agr_col2, agr_col3 = st.columns(3, gap="medium")
    with agr_col1:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 3px solid var(--pos);">
                <div class="kpi-label">All 3 Models Right</div>
                <div class="kpi-value" style="color:var(--pos);">{all_right:,}</div>
                <div class="kpi-desc">{all_right / len(preds_df) * 100:.1f}% consensus accuracy</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with agr_col2:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 3px solid var(--neg);">
                <div class="kpi-label">All 3 Models Wrong</div>
                <div class="kpi-value" style="color:var(--neg);">{all_wrong:,}</div>
                <div class="kpi-desc">{all_wrong / len(preds_df) * 100:.1f}% blind-spot errors</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with agr_col3:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 3px solid var(--accent);">
                <div class="kpi-label">Models Disagree</div>
                <div class="kpi-value" style="color:var(--accent);">{disagree:,}</div>
                <div class="kpi-desc">{disagree / len(preds_df) * 100:.1f}% split decisions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # d. Failure Patterns Row with computed counts
    st.markdown('<div class="cinesense-section-title" style="font-size:1.15rem; margin-top:2rem;">Failure patterns</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cinesense-takeaway">'
        'Empirical error rates across known syntactic failure conditions. '
        'Reviews with contrastive transitions ("but" / "however") and lengthy texts (>500 words) exhibit significantly elevated misclassification rates.'
        '</div>',
        unsafe_allow_html=True,
    )

    patterns_res = compute_failure_patterns(preds_df, model_key="all")
    fig_patterns = plot_failure_patterns_bar(
        patterns_res["patterns"],
        patterns_res["overall_error_rate"],
    )
    st.plotly_chart(fig_patterns, use_container_width=True)

    # b. Filter Row
    st.markdown('<div class="cinesense-section-title" style="font-size:1.15rem; margin-top:2rem;">Misclassified reviews explorer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cinesense-takeaway">'
        'Inspect individual misclassified test samples. Filter by architecture and error type, then click "Open in Analyzer" to examine word-level attribution in the Analyzer tab.'
        '</div>',
        unsafe_allow_html=True,
    )

    filter_c1, filter_c2, filter_c3 = st.columns([1.2, 1.3, 1.5], gap="medium")
    with filter_c1:
        model_choice = st.selectbox(
            "Model Filter",
            options=["All", "Logistic Regression", "Naive Bayes", "BiLSTM"],
            index=0,
            key="err_filter_model",
        )
    with filter_c2:
        error_choice = st.selectbox(
            "Error Type Filter",
            options=["All Errors", "False positive", "False negative"],
            index=0,
            key="err_filter_type",
        )
    with filter_c3:
        search_kw = st.text_input(
            "Search reviews",
            placeholder="Search keyword (e.g. twist, boring, acting)...",
            key="err_filter_search",
        )

    # Compute filtered subset
    filtered_df = preds_df.copy()

    # Model filtering
    if model_choice == "Logistic Regression":
        filtered_df = filtered_df[filtered_df["lr_pred"] != filtered_df["label"]]
        if error_choice == "False positive":
            filtered_df = filtered_df[(filtered_df["lr_pred"] == 1) & (filtered_df["label"] == 0)]
        elif error_choice == "False negative":
            filtered_df = filtered_df[(filtered_df["lr_pred"] == 0) & (filtered_df["label"] == 1)]
    elif model_choice == "Naive Bayes":
        filtered_df = filtered_df[filtered_df["nb_pred"] != filtered_df["label"]]
        if error_choice == "False positive":
            filtered_df = filtered_df[(filtered_df["nb_pred"] == 1) & (filtered_df["label"] == 0)]
        elif error_choice == "False negative":
            filtered_df = filtered_df[(filtered_df["nb_pred"] == 0) & (filtered_df["label"] == 1)]
    elif model_choice == "BiLSTM":
        filtered_df = filtered_df[filtered_df["lstm_pred"] != filtered_df["label"]]
        if error_choice == "False positive":
            filtered_df = filtered_df[(filtered_df["lstm_pred"] == 1) & (filtered_df["label"] == 0)]
        elif error_choice == "False negative":
            filtered_df = filtered_df[(filtered_df["lstm_pred"] == 0) & (filtered_df["label"] == 1)]
    else:  # All models: at least one model made an error
        any_err = (
            (filtered_df["lr_pred"] != filtered_df["label"])
            | (filtered_df["nb_pred"] != filtered_df["label"])
            | (filtered_df["lstm_pred"] != filtered_df["label"])
        )
        filtered_df = filtered_df[any_err]
        if error_choice == "False positive":
            fp_mask = (filtered_df["label"] == 0) & (
                (filtered_df["lr_pred"] == 1) | (filtered_df["nb_pred"] == 1) | (filtered_df["lstm_pred"] == 1)
            )
            filtered_df = filtered_df[fp_mask]
        elif error_choice == "False negative":
            fn_mask = (filtered_df["label"] == 1) & (
                (filtered_df["lr_pred"] == 0) | (filtered_df["nb_pred"] == 0) | (filtered_df["lstm_pred"] == 0)
            )
            filtered_df = filtered_df[fn_mask]

    # Keyword search filtering
    if search_kw.strip():
        filtered_df = filtered_df[
            filtered_df["text"].astype(str).str.contains(search_kw.strip(), case=False, na=False)
        ]

    # Summary count
    total_matching = len(filtered_df)
    st.markdown(
        f'<div style="font-family:var(--font-mono); font-size:0.8rem; color:var(--muted); margin-bottom:0.75rem;">'
        f'Showing <strong>{total_matching:,}</strong> misclassified reviews matching filter criteria.'
        f'</div>',
        unsafe_allow_html=True,
    )

    if total_matching == 0:
        st.info("No reviews match the selected filter and search criteria.")
        return

    # c. Paged Table of Misclassified Reviews
    page_size = 5
    total_pages = max(1, (total_matching - 1) // page_size + 1)

    page_col1, page_col2 = st.columns([2, 1], gap="medium")
    with page_col2:
        current_page = st.number_input(
            f"Page (1 to {total_pages})",
            min_value=1,
            max_value=total_pages,
            value=1,
            step=1,
            key="err_page_num",
        )

    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, total_matching)
    page_subset = filtered_df.iloc[start_idx:end_idx]

    # Scrollable container at 400px
    st.markdown(
        '<div style="max-height: 400px; overflow-y: auto; padding-right: 6px; border:1px solid var(--line); border-radius:6px; background:var(--surface); padding:1rem; margin-bottom:1.5rem;">',
        unsafe_allow_html=True,
    )

    for idx, row in page_subset.iterrows():
        review_id = row["review_id"]
        full_text = str(row["text"])
        short_text = full_text[:200] + ("..." if len(full_text) > 200 else "")
        true_label = "POSITIVE" if row["label"] == 1 else "NEGATIVE"
        true_badge_class = "badge-pos" if row["label"] == 1 else "badge-neg"

        lr_label = "POS" if row["lr_pred"] == 1 else "NEG"
        lr_badge = "badge-pos" if row["lr_pred"] == 1 else "badge-neg"
        lr_conf = row["lr_pos_prob"] if row["lr_pred"] == 1 else (1.0 - row["lr_pos_prob"])

        nb_label = "POS" if row["nb_pred"] == 1 else "NEG"
        nb_badge = "badge-pos" if row["nb_pred"] == 1 else "badge-neg"
        nb_conf = row["nb_pos_prob"] if row["nb_pred"] == 1 else (1.0 - row["nb_pos_prob"])

        lstm_label = "POS" if row["lstm_pred"] == 1 else "NEG"
        lstm_badge = "badge-pos" if row["lstm_pred"] == 1 else "badge-neg"
        lstm_conf = row["lstm_pos_prob"] if row["lstm_pred"] == 1 else (1.0 - row["lstm_pos_prob"])

        item_col1, item_col2 = st.columns([3.8, 1.2], gap="medium")
        with item_col1:
            st.markdown(
                f"""
                <div style="margin-bottom:0.85rem; padding-bottom:0.75rem; border-bottom:1px solid var(--line);">
                    <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.35rem;">
                        <span style="font-family:var(--font-mono); font-size:0.75rem; color:var(--muted);">#{review_id}</span>
                        <span class="{true_badge_class}" style="font-size:0.72rem;">TRUE: {true_label}</span>
                        <span style="font-family:var(--font-mono); font-size:0.75rem; color:var(--muted); margin-left:0.5rem;">
                            LR: <span class="{lr_badge}" style="font-size:0.7rem;">{lr_label} ({lr_conf*100:.1f}%)</span>
                            &nbsp;NB: <span class="{nb_badge}" style="font-size:0.7rem;">{nb_label} ({nb_conf*100:.1f}%)</span>
                            &nbsp;BiLSTM: <span class="{lstm_badge}" style="font-size:0.7rem;">{lstm_label} ({lstm_conf*100:.1f}%)</span>
                        </span>
                    </div>
                    <div style="font-family:var(--font-body); font-size:0.88rem; color:var(--ink); line-height:1.45;">
                        "{html.escape(short_text)}"
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with item_col2:
            st.markdown("<div style='margin-top:0.35rem;'>", unsafe_allow_html=True)
            if st.button("Open in Analyzer", key=f"btn_err_open_{review_id}", use_container_width=True):
                st.session_state["review_text_input"] = full_text
                st.session_state["has_run_analysis"] = True
                set_active_tab("Analyzer")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

