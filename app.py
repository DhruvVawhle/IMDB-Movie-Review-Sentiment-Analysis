"""
CineSense — Movie Review Intelligence
Main Application Entry Point and Tab Router.
"""

import os
import sys
import streamlit as st

# Ensure root directory is on Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from ui.theme import inject_css
from ui.components import render_footer, render_header, render_navigation
from services.prediction_service import preload_all_models
from ui.tabs.home import render_home_tab
from ui.tabs.overview import render_overview_tab
from ui.tabs.analyzer import render_analyzer_tab
from ui.tabs.movies import render_movies_tab
from ui.tabs.dataset import render_dataset_tab
from ui.tabs.benchmarks import render_benchmarks_tab
from ui.tabs.pipeline import render_pipeline_tab

# Configure Streamlit page defaults
st.set_page_config(
    page_title="CineSense — Movie Review Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def main() -> None:
    # Preload model artifacts into st.cache_resource so first click is instantaneous
    preload_all_models()

    # 1. Inject single unified CSS block with Google Fonts & design tokens
    inject_css()

    # 2. Render top header wordmark and subtitle
    render_header()

    # 3. Render underline tab bar synced with st.query_params
    active_tab = render_navigation()

    # 4. Route to active tab view
    if active_tab == "Home":
        render_home_tab()
    elif active_tab == "Movies":
        render_movies_tab()
    elif active_tab in ("Analyzer", "Analyze a review"):
        render_analyzer_tab()
    elif active_tab in ("Project", "Overview"):
        render_overview_tab()
    elif active_tab == "Dataset":
        render_dataset_tab()
    elif active_tab in ("Benchmarks", "Model benchmarks"):
        render_benchmarks_tab()
    elif active_tab == "NLP pipeline":
        render_pipeline_tab()
    else:
        render_home_tab()

    # 5. Editorial, accessible footer with TMDB and dataset citations
    render_footer()


if __name__ == "__main__":
    main()
