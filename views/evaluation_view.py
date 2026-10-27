"""
Model Evaluation and Benchmarking View for CineSense.
Displays side-by-side performance metrics, interactive Plotly confusion matrices,
ROC curves, and diagnostic comparisons across all fitted models.
"""

import streamlit as st
from services.evaluation_service import (
    get_available_models_meta,
    get_comparison_dataframe,
    get_model_confusion_matrix,
    get_model_roc_curve,
    load_evaluation_summary,
)
from components.visualizations import (
    plot_confusion_matrix_heatmap,
    plot_model_comparison_bars,
    plot_multi_roc_curves,
)


"""
Model Evaluation and Benchmarking View for CineSense.
Displays side-by-side performance metrics, interactive Plotly confusion matrices,
ROC curves, and diagnostic comparisons across all fitted models.
"""

import streamlit as st
from services.evaluation_service import (
    get_available_models_meta,
    get_comparison_dataframe,
    get_formatted_comparison_dataframe,
    get_model_confusion_matrix,
    get_model_roc_curve,
    load_evaluation_summary,
)
from components.visualizations import (
    plot_confusion_matrix_heatmap,
    plot_model_comparison_bars,
    plot_multi_roc_curves,
)


def render_evaluation():
    st.markdown('<h2 class="editorial-heading">Model benchmarks</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="editorial-subheading">'
        'All models trained on the same 40,000 reviews and tested on 10,000 unseen ones, stratified by class, with no leakage.'
        '</p>',
        unsafe_allow_html=True,
    )

    summary, err = load_evaluation_summary()
    if not summary or "models" not in summary:
        st.error(err or "Evaluation metadata is unavailable.")
        return

    # Section: Metrics side by side
    st.markdown('<h3 class="editorial-heading" style="font-size:1.25rem;">Metrics side by side</h3>', unsafe_allow_html=True)
    comp_df = get_comparison_dataframe()
    formatted_df = get_formatted_comparison_dataframe(comp_df)
    if formatted_df is not None:
        st.dataframe(
            formatted_df[["Model", "Accuracy (%)", "Precision (%)", "Recall (%)", "F1-Score (%)", "ROC-AUC", "Feature Extraction"]],
            use_container_width=True,
            hide_index=True,
        )

        fig_bars = plot_model_comparison_bars(comp_df)
        st.plotly_chart(fig_bars, use_container_width=True)

    # Section: ROC curves
    st.markdown('<h3 class="editorial-heading" style="font-size:1.25rem; margin-top:2rem;">ROC curves</h3>', unsafe_allow_html=True)
    fig_roc = plot_multi_roc_curves(summary["models"])
    st.plotly_chart(fig_roc, use_container_width=True)

    # Section: Confusion matrix
    st.markdown('<h3 class="editorial-heading" style="font-size:1.25rem; margin-top:2rem;">Confusion matrix</h3>', unsafe_allow_html=True)
    models_meta = get_available_models_meta()
    model_keys = [k for k, v in models_meta.items() if v.get("status") == "available"]

    selected_key = st.selectbox(
        "Pick model to inspect confusion matrix",
        options=model_keys,
        format_func=lambda k: models_meta[k].get("name", k),
    )

    if selected_key:
        m_info = models_meta[selected_key]
        cm_data = get_model_confusion_matrix(selected_key)

        m_col1, m_col2 = st.columns([1.3, 1])
        with m_col1:
            if cm_data:
                fig_cm = plot_confusion_matrix_heatmap(cm_data, m_info.get("name", selected_key))
                st.plotly_chart(fig_cm, use_container_width=True)
            else:
                st.info("Confusion matrix data unavailable for this model.")

        with m_col2:
            st.markdown(
                f'<div class="cinesense-panel">'
                f'<div class="cinesense-panel-title">{m_info.get("name", selected_key)} Diagnostics</div>'
                f'<div class="cinesense-panel-body">'
                f'<strong>Feature Representation:</strong> {m_info.get("feature_extractor", "N/A")}<br>'
                f'<strong>Test Set Accuracy:</strong> {m_info.get("accuracy", 0)*100:.2f}%<br>'
                f'<strong>Precision (Positive Class):</strong> {m_info.get("precision", 0)*100:.2f}%<br>'
                f'<strong>Recall / Sensitivity:</strong> {m_info.get("recall", 0)*100:.2f}%<br>'
                f'<strong>F1 Harmonic Mean:</strong> {m_info.get("f1", 0)*100:.2f}%<br>'
                f'<strong>ROC Area Under Curve:</strong> {m_info.get("roc_auc", 0):.4f}<br>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Method Note
    st.markdown(
        """
        <div class="cinesense-panel" style="margin-top:1.5rem;">
            <div class="cinesense-panel-body" style="color:var(--text-primary); font-size:0.9rem;">
                <strong>Method.</strong> 80/20 stratified split. TF-IDF and count vocabularies (20,000 features, 1 to 2-grams)
                are fitted on the training set only. Decision threshold is 0.5 on all probabilities.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

