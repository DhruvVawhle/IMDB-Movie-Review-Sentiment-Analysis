# CineSense — Movie Review Intelligence

[![Streamlit](https://img.shields.io/badge/Streamlit-1.66-FF4B4B.svg)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

> **Deployed Application URL:** `https://cinesense-sentiment.streamlit.app` *(Placeholder — update upon deployment)*

---

## 1. What the App Does

**CineSense** is an interactive NLP intelligence dashboard and sentiment classification workbench. It allows users to paste any movie review and evaluate whether three different machine learning architectures read it as **Positive** or **Negative**:

- **Interactive Sentiment Analysis:** Real-time inference across Logistic Regression (TF-IDF), Multinomial Naive Bayes (Bag of Words), and a Bidirectional LSTM (PyTorch neural sequence model).
- **Inline Word Highlighting via LIME:** Explainability module that computes local word attributions. Influential words are highlighted directly inside the review text (green background with solid underline for positive; red background with dotted underline for negative; opacity scaled to attribution weight; tooltip title showing exact score delta).
- **Architectural Comparison Mode:** Side-by-side verdict cards, posterior confidence meters, and calibrated probabilities.
- **Empirical Error Analysis:** Offline evaluation across 10,000 unseen test reviews, auditing inter-model consensus, misclassifications, and syntactic failure patterns (negations, contrastive transitions, and lengthy reviews).
- **Corpus Explorer & NLP Pipeline Audit:** Searchable 50,000-review dataset viewer and step-by-step lexical tokenization inspector.

---

## 2. Interface Preview

```
+---------------------------------------------------------------------------------------+
|  CineSense                                                [Analyze] [Model Results]  |
|  Paste a movie review and see whether three models read it as positive or negative.   |
+---------------------------------------------------------------------------------------+
|  Home | Movies | Analyzer | Project | Dataset | Benchmarks | NLP pipeline             |
+---------------------------------------------------------------------------------------+
|  [Input Review]                               [Model Evaluation & Explanations]      |
|  "A truly remarkable cinematic achievement.   POSITIVE SENTIMENT (91.2% Conf)         |
|   Flawless direction and stunning cast."      [====================|.........]        |
|                                                                                       |
|  Inline Word Highlighting:                    Words that moved the score:             |
|  A truly [remarkable] cinematic [achievement]. remarkable (+0.12)  ==============     |
|  [Flawless] direction and stunning cast.       flawless   (+0.13)  ===============    |
+---------------------------------------------------------------------------------------+
```

*(Screenshot placeholder: `assets/cinesense_preview.png`)*

---

## 3. Setup and Run Steps

### Prerequisites
- Python 3.10 to 3.14+
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DhruvVawhle/IMDB-Movie-Review-Sentiment-Analysis.git
   cd "IMDB-Movie-Review-Sentiment-Analysis"
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   # macOS / Linux:
   source .venv/bin/activate
   ```

3. **Install pinned dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Secrets (Optional TMDB Integration):**
   Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
   Add your TMDB API Key if you want live movie posters and metadata in the Movies tab. The core sentiment analysis works out-of-the-box without an API key.

5. **Generate Offline Test Predictions (for Error Analysis):**
   ```bash
   python scripts/export_predictions.py
   ```

6. **Launch the Streamlit Application:**
   ```bash
   streamlit run app.py
   ```

---

## 4. Model Benchmark Results

All models were evaluated on the held-out **10,000 unseen stratified test reviews** (random_state=42) from the 50,000 Stanford IMDB dataset with zero data leakage.

| Architecture | Representation / Features | Accuracy (%) | Precision (%) | Recall (%) | F1-Score (%) | ROC-AUC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | TF-IDF (1–2 ngrams, 20K features) | **89.78%** | 88.92% | **90.88%** | **89.89%** | **0.9634** |
| **Multinomial Naive Bayes** | CountVectorizer (1–2 ngrams, 20K, $\alpha=0.1$) | 86.90% | 86.49% | 87.46% | 86.97% | 0.9302 |
| **Bidirectional LSTM** | Embedding (64) + BiLSTM (64) + MaxPool + Dense | 83.30% | **89.59%** | 75.36% | 81.86% | 0.9313 |

*Note: Logistic Regression with TF-IDF attains top accuracy and ROC-AUC, serving as our most stable production baseline.*

---

## 5. Limitations

Please note the operational boundaries and technical constraints of these models:

1. **English only:** The NLP pipeline (tokenization, stopword lists, and WordNet lemmatizers) is designed exclusively for English text. Submissions in other languages will produce invalid tokens.
2. **IMDB-only training:** All three models were trained exclusively on the Stanford 50,000 IMDB movie review dataset. Generalization to other platforms (Letterboxd, Rotten Tomatoes, Twitter/X) may exhibit distribution shift.
3. **Sarcasm and negation errors:** Sarcastic phrasing (*"A masterclass in how to waste two hours"*) and multi-clause nested negations remain known challenges for bag-of-words and linear n-gram classifiers.
4. **No neutral class:** The classification task is formulated as strictly binary (**Positive** vs. **Negative**). Ambivalent or neutral (5/10) reviews are forced into one of the two polar classes.
5. **Results on non-IMDB text are experimental:** Inferences on domains outside long-form movie reviews (e.g. consumer products, tweets, customer service feedback) are strictly experimental.

---

## 6. Citations & Credits

- **Stanford IMDB Dataset:** Maas, A. L., Daly, R. E., Pham, P. T., Huang, D., Ng, A. Y., & Potts, C. (2011). *Learning Word Vectors for Sentiment Analysis*. Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics (ACL 2011).
- **The Movie Database (TMDB):** Movie metadata, posters, and cast listings are provided by the TMDB API. *This product uses the TMDB API but is not endorsed or certified by TMDB.*
- **LIME:** Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). *"Why Should I Trust You?": Explaining the Predictions of Any Classifier*. ACM SIGKDD 2016.
