"""
Automated smoke test to verify all tabs and components render cleanly.
"""

import os
import sys

# Ensure root directory is on path
CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import pandas as pd
from ui.theme import inject_css, get_plotly_layout
from ui.components import (
    render_footer,
    render_header,
    render_navigation,
    render_kpi_strip,
    render_pipeline_strip,
    render_empty_state,
    plot_split_class_bar,
    plot_length_histogram,
    plot_probability_meter,
    plot_distinctive_words_bar,
    plot_top_features_divergent,
    plot_benchmarks_bar_chart,
    plot_roc_curves,
    plot_confusion_matrix,
)
from services.data_service import get_dataset_statistics, load_imdb_dataset
from services.evaluation_service import (
    get_comparison_dataframe,
    get_formatted_comparison_dataframe,
    get_model_confusion_matrix,
    load_evaluation_summary,
    load_top_predictive_features,
)
from services.prediction_service import predict_sentiment, compare_all_models
from ui.tabs.movies import FALLBACK_MOVIES, fetch_tmdb_movies

print("1. Testing Theme & Plotly Layout...")
layout = get_plotly_layout(height=300)
assert layout["font"]["color"] == "#14202B"
print("   Theme OK.")

print("2. Testing Split Bar & Histogram...")
stats = get_dataset_statistics()
fig_bar = plot_split_class_bar(stats["positive_count"], stats["negative_count"])
assert fig_bar is not None
df, _ = load_imdb_dataset(limit=100)
fig_hist = plot_length_histogram(df)
assert fig_hist is not None
print("   Split bar & histogram OK.")

print("3. Testing Probability Meter & Model Prediction...")
res = predict_sentiment("A truly extraordinary masterpiece with stunning cinematography.", model_key="logistic_regression")
assert res["success"] is True
fig_prob = plot_probability_meter(res["positive_probability"], res["negative_probability"])
assert fig_prob is not None
comp_res = compare_all_models("A phenomenal film!")
assert comp_res["success"] is True
print("   Prediction and probability meter OK.")

print("4. Testing Benchmarks & Confusion Matrix...")
comp_df = get_comparison_dataframe()
formatted_df = get_formatted_comparison_dataframe(comp_df)
assert formatted_df is not None
fig_bench = plot_benchmarks_bar_chart(comp_df)
assert fig_bench is not None
summary, _ = load_evaluation_summary()
fig_roc = plot_roc_curves(summary["models"])
assert fig_roc is not None
cm = get_model_confusion_matrix("logistic_regression")
fig_cm = plot_confusion_matrix(cm, "Logistic Regression")
assert fig_cm is not None
print("   Benchmarks, ROC, and confusion matrix OK.")

print("5. Testing Pipeline & Distinctive Features...")
top_feats, _ = load_top_predictive_features()
fig_distinct = plot_distinctive_words_bar(top_feats, sentiment="positive")
assert fig_distinct is not None
fig_diverge = plot_top_features_divergent(top_feats, top_n=10)
assert fig_diverge is not None
print("   Pipeline and feature charts OK.")

print("6. Testing Movies fallback catalog...")
assert len(FALLBACK_MOVIES) >= 6
for m in FALLBACK_MOVIES:
    assert "title" in m and "audience_score" in m and "sample_review" in m
print("   Movies catalog OK.")

print("7. Testing OpenRouter NLP & Fallback Engine...")
from services.llm_context_service import analyze_movie_context, get_openrouter_api_key
assert get_openrouter_api_key() is not None

# Test live or fallback
ctx = analyze_movie_context("A breathtaking intellectual spectacle with stunning visuals and deep performances.", movie_title="Inception")
assert "summary" in ctx
assert "tone" in ctx
assert "aspects" in ctx
assert "verdict" in ctx
assert "engine" in ctx
assert len(ctx["aspects"]) > 0

# Test forced fallback
fallback_ctx = analyze_movie_context("A colossal waste of time and disjointed screenplay.", movie_title="Flop", force_fallback=True)
assert fallback_ctx["is_fallback"] is True
assert "Local NLP Engine" in fallback_ctx["engine"]
assert len(fallback_ctx["aspects"]) > 0
print("   OpenRouter NLP Context & Heuristic Fallback Engine OK.")

print("8. Testing Home Tab & TMDB now_playing / upcoming services...")
from services.tmdb_service import get_movies_by_category_and_region
from ui.tabs.home import render_home_tab
from ui.components import TABS_LIST, set_active_tab
assert TABS_LIST == ["Home", "Movies", "Analyzer", "Project", "Dataset", "Benchmarks", "NLP pipeline"]

np_all = get_movies_by_category_and_region("now_playing", "All")
assert len(np_all) > 0
for m in np_all[:3]:
    assert "poster_url" in m and "title" in m and "formatted_date" in m and "region_label" in m

up_ind = get_movies_by_category_and_region("upcoming", "Indian")
assert len(up_ind) > 0
print("   Home Tab & TMDB now_playing / upcoming OK.")

print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")

