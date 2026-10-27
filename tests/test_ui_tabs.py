"""
Integration tests for Streamlit UI tabs.
Ensures every tab renders without uncaught exceptions.
"""

import os
import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app.py"))


@pytest.mark.parametrize("tab_name", [
    "Overview",
    "Analyze a review",
    "Movies",
    "Dataset",
    "Model benchmarks",
    "NLP pipeline",
])
def test_tab_renders_without_exceptions(tab_name):
    at = AppTest.from_file(APP_PATH, default_timeout=60)
    at.query_params["tab"] = tab_name
    at.run()
    assert not at.exception, f"Tab '{tab_name}' raised an exception: {at.exception}"

