"""
NLP Pipeline Tab for CineSense.
Toggles between 'Try the steps' (interactive 2x2 grid showing the 4 cleaning stages)
and 'Word weights' (top positive and negative fitted vocabulary coefficients as bars).
"""

import streamlit as st
from services.evaluation_service import load_top_predictive_features
from services.preprocessing import get_pipeline_breakdown
from ui.components import plot_top_features_divergent


def render_pipeline_tab() -> None:
    st.markdown(
        '<p class="cinesense-takeaway" style="font-size:1.05rem; color:var(--ink); margin-bottom: 1.25rem;">'
        'Inspect how unstructured review text is cleaned and vectorized, or analyze the top lexical coefficients that influence model predictions.'
        '</p>',
        unsafe_allow_html=True,
    )

    # Toggle between 'Try the steps' and 'Word weights'
    view_options = ["Try the steps", "Word weights"]
    if hasattr(st, "segmented_control"):
        selected_view = st.segmented_control(
            "Pipeline View Mode",
            options=view_options,
            default="Try the steps",
            label_visibility="collapsed",
        )
        if not selected_view:
            selected_view = "Try the steps"
    else:
        selected_view = st.radio(
            "Pipeline View Mode",
            options=view_options,
            horizontal=True,
            label_visibility="collapsed",
        )

    st.write("")

    if selected_view == "Try the steps":
        st.markdown('<div class="cinesense-section-title" style="margin-top:0;">Interactive 4-stage pipeline sandbox</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="cinesense-takeaway">Type or edit a sample text containing HTML markup, punctuation, and mixed sentiment to observe each transformation stage.</div>',
            unsafe_allow_html=True,
        )

        sample_input = st.text_input(
            "Sandbox sentence",
            value="<p>This movie was ABSOLUTELY wonderful! Visit http://imdb.com for 10/10 reviews! But the ending was terrible and boring.</p>",
            label_visibility="collapsed",
        )

        if sample_input.strip():
            breakdown = get_pipeline_breakdown(sample_input)

            # Four stages in a 2x2 grid
            row1_c1, row1_c2 = st.columns(2)
            with row1_c1:
                st.markdown(
                    f"""
                    <div class="cinesense-card" style="min-height: 140px;">
                        <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--accent); font-weight:600; margin-bottom:0.25rem;">
                            Stage 1: Strip HTML & URLs
                        </div>
                        <div style="font-family:var(--font-heading); font-size:0.95rem; font-weight:600; color:var(--ink); margin-bottom:0.4rem;">
                            Sanitize Markup
                        </div>
                        <div style="font-family:var(--font-mono); font-size:0.82rem; background:var(--bg); padding:0.4rem 0.6rem; border-radius:4px; color:var(--ink); word-break:break-all;">
                            {breakdown['html_and_url_cleaned']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with row1_c2:
                st.markdown(
                    f"""
                    <div class="cinesense-card" style="min-height: 140px;">
                        <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--accent); font-weight:600; margin-bottom:0.25rem;">
                            Stage 2: Lowercase & Letters Only
                        </div>
                        <div style="font-family:var(--font-heading); font-size:0.95rem; font-weight:600; color:var(--ink); margin-bottom:0.4rem;">
                            Normalize Text
                        </div>
                        <div style="font-family:var(--font-mono); font-size:0.82rem; background:var(--bg); padding:0.4rem 0.6rem; border-radius:4px; color:var(--ink); word-break:break-all;">
                            {breakdown['normalized']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            row2_c1, row2_c2 = st.columns(2)
            with row2_c1:
                tokens_display = ", ".join(breakdown.get("filtered_tokens_sample", []))
                st.markdown(
                    f"""
                    <div class="cinesense-card" style="min-height: 140px;">
                        <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--accent); font-weight:600; margin-bottom:0.25rem;">
                            Stage 3: Tokenize & Drop Stopwords
                        </div>
                        <div style="font-family:var(--font-heading); font-size:0.95rem; font-weight:600; color:var(--ink); margin-bottom:0.4rem;">
                            Token Filtering
                        </div>
                        <div style="font-family:var(--font-mono); font-size:0.82rem; background:var(--bg); padding:0.4rem 0.6rem; border-radius:4px; color:var(--ink); word-break:break-all;">
                            {tokens_display or '(No tokens remaining)'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with row2_c2:
                st.markdown(
                    f"""
                    <div class="cinesense-card" style="min-height: 140px;">
                        <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--accent); font-weight:600; margin-bottom:0.25rem;">
                            Stage 4: Lemmatize (WordNet)
                        </div>
                        <div style="font-family:var(--font-heading); font-size:0.95rem; font-weight:600; color:var(--ink); margin-bottom:0.4rem;">
                            Morphological Base Forms
                        </div>
                        <div style="font-family:var(--font-mono); font-size:0.82rem; background:var(--bg); padding:0.4rem 0.6rem; border-radius:4px; color:var(--ink); word-break:break-all;">
                            {breakdown['lemmatized_text']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Sentiment Anchors in Sandbox Sentence
            top_feats, err = load_top_predictive_features()
            if top_feats:
                pos_dict = {item["term"]: item["weight"] for item in top_feats.get("positive", [])}
                neg_dict = {item["term"]: item["weight"] for item in top_feats.get("negative", [])}

                tokens = breakdown.get("lemmatized_tokens", [])
                pos_matches = []
                neg_matches = []

                for t in tokens:
                    if t in pos_dict:
                        pos_matches.append((t, pos_dict[t]))
                    if t in neg_dict:
                        neg_matches.append((t, neg_dict[t]))

                for i in range(len(tokens) - 1):
                    bg = f"{tokens[i]} {tokens[i+1]}"
                    if bg in pos_dict:
                        pos_matches.append((bg, pos_dict[bg]))
                    if bg in neg_dict:
                        neg_matches.append((bg, neg_dict[bg]))

                st.markdown('<div class="cinesense-section-title" style="font-size:1.05rem; margin-top:1.25rem;">Detected vocabulary sentiment anchors</div>', unsafe_allow_html=True)
                st.markdown(
                    '<div class="cinesense-takeaway">Recognized n-grams from the 20,000-feature TF-IDF matrix present in your sandbox text.</div>',
                    unsafe_allow_html=True,
                )

                anch_c1, anch_c2 = st.columns(2)
                with anch_c1:
                    st.markdown('<div style="font-family:var(--font-heading); font-size:0.95rem; font-weight:600; color:var(--pos); margin-bottom:0.35rem;">Pushes toward positive</div>', unsafe_allow_html=True)
                    if pos_matches:
                        chips_html = ""
                        for term, w in sorted(pos_matches, key=lambda x: x[1], reverse=True):
                            chips_html += f'<span class="feature-chip pos">{term} (+{w:.2f})</span> '
                        st.markdown(chips_html, unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="cinesense-takeaway">No strong positive vocabulary anchors found in this sentence.</div>', unsafe_allow_html=True)

                with anch_c2:
                    st.markdown('<div style="font-family:var(--font-heading); font-size:0.95rem; font-weight:600; color:var(--neg); margin-bottom:0.35rem;">Pushes toward negative</div>', unsafe_allow_html=True)
                    if neg_matches:
                        chips_html = ""
                        for term, w in sorted(neg_matches, key=lambda x: x[1]):
                            chips_html += f'<span class="feature-chip neg">{term} ({w:.2f})</span> '
                        st.markdown(chips_html, unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="cinesense-takeaway">No strong negative vocabulary anchors found in this sentence.</div>', unsafe_allow_html=True)

    else:
        # Word weights view
        st.markdown('<div class="cinesense-section-title" style="margin-top:0;">Fitted logistic regression coefficients</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="cinesense-takeaway">Top n-gram terms ranked by log-odds weights. Positive weights drive prediction toward positive sentiment, negative weights drive negative sentiment.</div>',
            unsafe_allow_html=True,
        )

        top_feats, err = load_top_predictive_features()
        if top_feats:
            n_features = st.slider("Number of top features per polarity", min_value=10, max_value=25, value=15, step=5)
            fig_divergent = plot_top_features_divergent(top_feats, top_n=n_features)
            st.plotly_chart(fig_divergent, use_container_width=True)
        else:
            st.info("Top predictive features data not found.")

