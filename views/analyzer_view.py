"""
Interactive Sentiment Analyzer View for CineSense.
Primary workflow allowing custom review entry, example loading,
real-time inference, confidence calibration, feature attribution, and model comparison.
"""

import streamlit as st
from services.prediction_service import (
    compare_all_models,
    get_available_models_list,
    predict_sentiment,
    validate_review_input,
)
from components.visualizations import plot_prediction_probabilities

PRESET_REVIEWS = {
    "Rave Review (Positive)": (
        "A truly remarkable cinematic achievement. The direction is flawless, the performances are deeply "
        "affecting, and the emotional resonance lingered long after the credits rolled. Easily one of the finest films of the decade."
    ),
    "Critical Pan (Negative)": (
        "A colossal waste of time and talent. The screenplay is disjointed and filled with tired cliches, the pacing drags "
        "aimlessly, and the dialogue feels insultingly artificial. Terribly disappointing from start to finish."
    ),
    "Nuanced Mixed Assessment": (
        "Visually striking with gorgeous cinematography and solid practical effects, but unfortunately hampered by a weak "
        "and predictable second act. Worth a watch for film enthusiasts, but far from a masterpiece."
    ),
    "Short Informal Remark": (
        "Decent Saturday evening popcorn movie. Fun action scenes, though nothing memorable."
    ),
}


def render_analyzer():
    st.markdown('<h2 class="editorial-heading">Analyze a review</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="editorial-subheading">'
        'Paste a review and pick a model. Results update when you press Analyze.'
        '</p>',
        unsafe_allow_html=True,
    )

    available_models = get_available_models_list()
    valid_model_choices = {m["id"]: m["name"] for m in available_models if m["available"]}

    if not valid_model_choices:
        st.error("No trained models are currently available. Please run model training first.")
        return

    # Configuration controls
    ctrl_col1, ctrl_col2 = st.columns([2, 1.2])
    with ctrl_col1:
        selected_model_id = st.selectbox(
            "Pick a model",
            options=list(valid_model_choices.keys()),
            format_func=lambda x: valid_model_choices[x],
            help="Select the machine learning algorithm to perform inference.",
        )
    with ctrl_col2:
        compare_mode = st.checkbox(
            "Compare all three",
            value=False,
            help="Execute inference across Logistic Regression, Naive Bayes, and BiLSTM simultaneously.",
        )

    # Preset Review Loader
    st.markdown('<p style="font-size:0.85rem; font-weight:600; color:var(--text-primary); margin-bottom:0.35rem;">Examples</p>', unsafe_allow_html=True)
    preset_cols = st.columns(len(PRESET_REVIEWS))
    for i, (name, text) in enumerate(PRESET_REVIEWS.items()):
        with preset_cols[i]:
            if st.button(name, key=f"preset_{i}", use_container_width=True):
                st.session_state["review_text_input"] = text

    # Text Input Area
    current_text = st.session_state.get("review_text_input", "")
    review_input = st.text_area(
        "Review text",
        value=current_text,
        height=160,
        placeholder="Type or paste any movie review here (e.g. 'A truly remarkable cinematic achievement with mesmerizing acting...')...",
        key="review_area",
    )

    # Telemetry Counters & Note
    char_count = len(review_input)
    word_count = len(review_input.split())
    st.markdown(
        f'<div style="display:flex; justify-content:space-between; align-items:center; margin-top:-0.35rem; margin-bottom:1rem;">'
        f'<span style="font-size:0.8rem; color:var(--text-dim);">'
        f'Preview scoring uses a small word list so this page works on its own. In the Streamlit app, results come from your trained models.'
        f'</span>'
        f'<span style="font-family:var(--font-mono); font-size:0.8rem; color:var(--text-dim);">'
        f'{word_count:,} words | {char_count:,} chars'
        f'</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    col_btn, col_clear = st.columns([1.2, 4])
    with col_btn:
        analyze_clicked = st.button("Analyze Review", type="primary", use_container_width=True)
    with col_clear:
        if st.button("Clear Input", use_container_width=False):
            st.session_state["review_text_input"] = ""
            st.rerun()

    # Trigger inference on button click or existing analyzed review
    if analyze_clicked:
        st.session_state["review_text_input"] = review_input

        is_valid, err_msg = validate_review_input(review_input)
        if not is_valid:
            st.warning(err_msg)
            return

        with st.spinner("Executing natural language preprocessing and model inference..."):
            if compare_mode:
                # Comparison execution
                comp_res = compare_all_models(review_input)
                if not comp_res.get("success"):
                    st.error(comp_res.get("error", "Comparison failed."))
                    return

                st.markdown('<h3 class="editorial-heading" style="font-size:1.3rem;">Comparative Model Predictions</h3>', unsafe_allow_html=True)
                results_dict = comp_res.get("results", {})

                cols = st.columns(len(results_dict))
                for idx, (m_id, m_data) in enumerate(results_dict.items()):
                    with cols[idx]:
                        is_pos = m_data["is_positive"]
                        verdict_class = "positive" if is_pos else "negative"
                        pill_class = "positive" if is_pos else "negative"
                        st.markdown(
                            f'<div class="verdict-card {verdict_class}">'
                            f'<div class="verdict-pill {pill_class}">{m_data["label"]}</div>'
                            f'<div class="stat-label">{m_data["name"]}</div>'
                            f'<div class="verdict-headline">{m_data["confidence"]:.1f}%</div>'
                            f'<div class="verdict-subtext">Positive Probability: {m_data["positive_prob"]*100:.1f}%<br>'
                            f'Negative Probability: {m_data["negative_prob"]*100:.1f}%</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

            # Single Model Detailed Prediction
            result = predict_sentiment(review_input, model_key=selected_model_id)

            if not result.get("success"):
                st.error(result.get("error", "Inference failed."))
                return

            is_positive = result["is_positive"]
            label = result["label"]
            verdict_class = "positive" if is_positive else "negative"
            pill_class = "positive" if is_positive else "negative"
            confidence_pct = result["confidence_percentage"]

            st.markdown(
                f'<div class="verdict-card {verdict_class}">'
                f'<div class="verdict-pill {pill_class}">{label} SENTIMENT</div>'
                f'<div class="verdict-headline">{label} &nbsp;({confidence_pct:.1f}% Confidence)</div>'
                f'<div class="verdict-subtext">'
                f'Evaluated using <strong>{valid_model_choices[selected_model_id]}</strong>. '
                f'The model assigns <strong>{result["positive_probability"]*100:.1f}%</strong> probability to positive polarity and '
                f'<strong>{result["negative_probability"]*100:.1f}%</strong> to negative polarity.'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Probability Distribution Bar
            st.markdown('<p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.25rem;">Posterior Probability Distribution:</p>', unsafe_allow_html=True)
            prob_fig = plot_prediction_probabilities(result["positive_probability"], result["negative_probability"])
            st.plotly_chart(prob_fig, use_container_width=True)

            # Calibrated Confidence Explanation
            st.markdown(
                f'<div class="cinesense-panel">'
                f'<div class="cinesense-panel-title">Statistical Confidence vs. Predicted Probability</div>'
                f'<div class="cinesense-panel-body">{result["calibration_explanation"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Feature Attribution Breakdown (Logistic Regression)
            if selected_model_id == "logistic_regression" and result.get("active_features"):
                st.markdown('<h3 class="editorial-heading" style="font-size:1.15rem;">Active Vocabulary Influencing This Review</h3>', unsafe_allow_html=True)
                st.markdown(
                    '<p style="font-size:0.85rem; color:var(--text-muted);">'
                    'These lexical terms were recognized in your review by the fitted TF-IDF vocabulary. '
                    'Positive weights increase positive probability, while negative weights favor negative polarity.'
                    '</p>',
                    unsafe_allow_html=True,
                )

                chips_html = ""
                for feat in result["active_features"]:
                    t_class = "positive" if feat["weight"] > 0 else "negative"
                    prefix = "+" if feat["weight"] > 0 else ""
                    chips_html += f'<span class="term-chip {t_class}">{feat["term"]} ({prefix}{feat["weight"]})</span>'
                st.markdown(chips_html, unsafe_allow_html=True)

            # Preprocessed Text Inspection
            with st.expander("Inspect Preprocessed Lexical Tokens"):
                st.write("**Cleaned Normalized Text:**")
                st.code(result.get("clean_text", ""))
                st.write(f"Total informative tokens after stopwords & lemmatization: **{result.get('token_count', 0)}**")

