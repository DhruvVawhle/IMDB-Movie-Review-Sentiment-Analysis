"""
Natural Language Processing Insights View for CineSense.
Breaks down the 7-stage NLP pipeline, offers an interactive text transformation sandbox,
and presents top predictive features from fitted Logistic Regression coefficients.
"""

import streamlit as st
from services.evaluation_service import load_top_predictive_features
from services.preprocessing import get_pipeline_breakdown
from components.visualizations import plot_top_features_chart


"""
Natural Language Processing Insights View for CineSense.
Breaks down the NLP pipeline steps, offers an interactive text transformation sandbox,
and presents which words push the model toward positive or negative labels.
"""

import streamlit as st
from services.evaluation_service import load_top_predictive_features
from services.preprocessing import get_pipeline_breakdown
from components.visualizations import plot_top_features_chart


def render_insights():
    st.markdown('<h2 class="editorial-heading">NLP pipeline</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="editorial-subheading">'
        'See what each cleaning step does to a sentence, then see which words push the model toward each label.'
        '</p>',
        unsafe_allow_html=True,
    )

    sample_sandbox_text = st.text_input(
        "Sandbox text",
        value="<p>This movie was ABSOLUTELY wonderful! Visit http://imdb.com for 10/10 reviews! But the ending was terrible and boring.</p>",
    )

    if sample_sandbox_text:
        breakdown = get_pipeline_breakdown(sample_sandbox_text)

        s1, s2 = st.columns(2)
        with s1:
            st.markdown(
                f'<div class="cinesense-panel">'
                f'<div class="cinesense-panel-title">1. Strip HTML, entities, URLs</div>'
                f'<div class="cinesense-panel-body"><code>{breakdown["html_and_url_cleaned"]}</code></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="cinesense-panel">'
                f'<div class="cinesense-panel-title">2. Lowercase, letters only</div>'
                f'<div class="cinesense-panel-body"><code>{breakdown["normalized"]}</code></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        with s2:
            st.markdown(
                f'<div class="cinesense-panel">'
                f'<div class="cinesense-panel-title">3. Tokens, stopwords removed</div>'
                f'<div class="cinesense-panel-body">'
                f'<code>{", ".join(breakdown["filtered_tokens_sample"])}</code>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="cinesense-panel">'
                f'<div class="cinesense-panel-title">4. Lemmatized, and stemmed for comparison</div>'
                f'<div class="cinesense-panel-body">'
                f'<strong>Lemmatized:</strong> <code>{breakdown["lemmatized_text"]}</code><br>'
                f'<strong>Stemmed:</strong> <code>{breakdown["stemmed_text"]}</code>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="cinesense-panel" style="margin-top:0.5rem; margin-bottom:1.5rem;">'
            '<div class="cinesense-panel-body" style="color:var(--text-primary); font-size:0.9rem;">'
            'Lemmatization keeps real words ("wonderful" stays "wonderful"), while stemming chops them '
            '("wonderful" becomes "wonder"). Real words make the n-gram features readable.'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # Words pushing toward positive / negative in sandbox sentence
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

            # Check bigrams too
            for i in range(len(tokens) - 1):
                bg = f"{tokens[i]} {tokens[i+1]}"
                if bg in pos_dict:
                    pos_matches.append((bg, pos_dict[bg]))
                if bg in neg_dict:
                    neg_matches.append((bg, neg_dict[bg]))

            col_pos_push, col_neg_push = st.columns(2)
            with col_pos_push:
                st.markdown('<h4 style="color:var(--sentiment-pos-fg); font-weight:600; font-size:1.05rem;">Pushes toward positive</h4>', unsafe_allow_html=True)
                if pos_matches:
                    chips_html = ""
                    for term, w in sorted(pos_matches, key=lambda x: x[1], reverse=True):
                        chips_html += f'<span class="term-chip positive">{term} (+{w:.2f})</span> '
                    st.markdown(chips_html, unsafe_allow_html=True)
                else:
                    st.markdown('<p style="font-size:0.85rem; color:var(--text-dim);">No strong positive anchors detected in this sentence.</p>', unsafe_allow_html=True)

            with col_neg_push:
                st.markdown('<h4 style="color:var(--sentiment-neg-fg); font-weight:600; font-size:1.05rem;">Pushes toward negative</h4>', unsafe_allow_html=True)
                if neg_matches:
                    chips_html = ""
                    for term, w in sorted(neg_matches, key=lambda x: x[1]):
                        chips_html += f'<span class="term-chip negative">{term} ({w:.2f})</span> '
                    st.markdown(chips_html, unsafe_allow_html=True)
                else:
                    st.markdown('<p style="font-size:0.85rem; color:var(--text-dim);">No strong negative anchors detected in this sentence.</p>', unsafe_allow_html=True)

    # Global Model Coefficients / Predictive Vocabulary Weights
    st.markdown('<h3 class="editorial-heading" style="font-size:1.25rem; margin-top:2.5rem;">Distinctive Model Vocabulary Weights</h3>', unsafe_allow_html=True)
    top_feats, err = load_top_predictive_features()
    if top_feats:
        top_n = st.slider("Number of Salient Features to Display", min_value=10, max_value=25, value=15, step=5)
        fig_feats = plot_top_features_chart(top_feats, top_n=top_n)
        st.plotly_chart(fig_feats, use_container_width=True)
    else:
        st.info("Feature weights not found. Please run model training first.")

