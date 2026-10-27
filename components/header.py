"""
Header and Navigation Component for CineSense.
"""

import streamlit as st


def render_header():
    """Render top brand editorial banner."""
    st.markdown(
        """
        <div class="cinesense-brand">
            <h1 class="cinesense-title">CineSense</h1>
            <span class="cinesense-edition">Movie review intelligence</span>
        </div>
        <p class="cinesense-subtitle">
            Sentiment analysis on 50,000 IMDB reviews, comparing three models. Academic data science project (RGPL syllabus).
        </p>
        """,
        unsafe_allow_html=True,
    )


def render_navigation() -> str:
    """Render horizontal navigation selector with persistent session state."""
    pages = {
        "overview": "Overview Dashboard",
        "analyzer": "Sentiment Analyzer",
        "explorer": "Dataset Explorer",
        "evaluation": "Model Benchmarks",
        "insights": "NLP Insights",
    }

    current = st.session_state.get("nav_page", "overview")
    if current not in pages:
        current = "overview"

    # Navigation buttons in clean horizontal layout
    cols = st.columns(len(pages))
    for i, (key, label) in enumerate(pages.items()):
        with cols[i]:
            btn_type = "primary" if key == current else "secondary"
            if st.button(label, key=f"nav_{key}", type=btn_type, use_container_width=True):
                st.session_state["nav_page"] = key
                st.rerun()

    st.write("")  # deliberate spacing
    return st.session_state.get("nav_page", "overview")

