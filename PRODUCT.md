# Product Context — CineSense: Movie Review Intelligence

## Product Vision & Objective
CineSense is an interactive, AI-powered movie review sentiment analysis and exploration platform built for college data science evaluations under the RGPL syllabus topic: "Build text/image/video/audio-based Data Science applications — Sentiment Analysis".
It elevates an academic Jupyter notebook exploration of the 50,000 IMDB Movie Review benchmark dataset into an art-directed, reliable, production-quality analytical web application.

## Core Problem Statement
Unstructured film reviews contain rich qualitative opinions that are challenging to quantify and synthesize manually. While baseline ML models (Logistic Regression, Naive Bayes) and deep-learning architectures (BiLSTM) achieve high accuracy on benchmark datasets, standard academic submissions often stop at raw notebook metrics or disconnected toy scripts. CineSense bridges this gap by offering:
1. Production-grade real-time inference with calibrated confidence explanations.
2. Transparent explainability via feature attribution (top predictive n-grams).
3. Live exploratory data analysis of the 50,000 review corpus.
4. Rigorous side-by-side model benchmarking using verified held-out evaluation metrics.
5. Educational breakdown of each phase in the modern NLP pipeline.

## Target Audience
- **Academic Evaluators & Professors:** Assessing code quality, ML rigor, reproducible train/test methodology, statistical metrics, and architecture.
- **Students & Peer Researchers:** Exploring how classical n-gram NLP compares with neural architectures on binary sentiment tasks.
- **Film Analysts & Casual Reviewers:** Testing custom movie reviews, observing vocabulary signals, and inspecting model confidence.

## Key Capabilities & Surface Workflows
- **Editorial Overview Dashboard:** Dataset statistics, verified sentiment balance, word count distributions, and benchmark summary.
- **Interactive Sentiment Analyzer:** Live multiline review input, real-time word/character telemetry, pre-loaded curated review samples, single/comparison model inference, calibrated confidence interpretation, and probability breakdown.
- **Dataset Explorer:** Searchable, filterable table over the 50K IMDB corpus, length analysis, vocabulary exploration, and filtered CSV export.
- **Model Evaluation & Comparison:** Exact confusion matrices, ROC curves, precision/recall/F1/AUC tables, and side-by-side metrics on the 10,000 held-out test split.
- **NLP Insights Pipeline:** Interactive walkthrough of cleaning, tokenization, lemmatization, vectorization, and Logistic Regression feature weight inspection.

## Technical Constraints & Boundaries
- **Environment Compatibility:** Strict handling of Python 3.14+, ensuring scikit-learn and NLTK models execute independently without brittle deep learning coupling.
- **No Fabricated Inference:** All predictions stem from fitted, persisted artifacts. Missing models fail safely with transparent explanations.
- **Academic Fidelity:** The original Jupyter notebook (`IMDB - Movie Sentiment Analysis.ipynb`) is preserved untouched for archival parity.
- **Zero Test Leakage:** 80/20 train/test split with `random_state=42` and stratification is strictly maintained across vectorizers and evaluation services.

