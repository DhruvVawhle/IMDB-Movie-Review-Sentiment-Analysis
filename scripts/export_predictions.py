"""
CineSense — Test Split Predictions Exporter
Standalone utility that loads the saved model artifacts, evaluates on the
stratified 10,000 test split (zero data leakage, exactly matching training split),
and writes data/test_predictions.csv for downstream Error Analysis.
Does not retrain anything.
"""

import os
import sys
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# Ensure root directory is on sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.prediction_service import load_artifacts
from services.preprocessing import clean_html_and_urls, preprocess_text


def export_test_predictions(
    data_path: str = os.path.join("data", "IMDB Dataset.csv"),
    output_path: str = os.path.join("data", "test_predictions.csv"),
    cache_path: str = os.path.join("data", "preprocessed_cache.parquet"),
) -> None:
    print("=" * 60)
    print("[CineSense] Exporting Test Split Model Predictions")
    print("=" * 60)

    if not os.path.exists(data_path):
        print(f"ERROR: Dataset not found at {data_path}")
        sys.exit(1)

    print(f"Loading raw dataset from {data_path}...")
    df = pd.read_csv(data_path)
    df["label"] = df["sentiment"].astype(str).str.strip().str.lower().map({"positive": 1, "negative": 0})
    if df["label"].isnull().any():
        df = df.dropna(subset=["label"])

    print(f"Total reviews: {len(df):,}")

    # Recreate the exact stratified 80/20 train/test split from training
    train_idx, test_idx = train_test_split(
        df.index, test_size=0.2, random_state=42, stratify=df["label"]
    )
    test_df = df.loc[test_idx].copy().reset_index(drop=True)
    test_df["review_id"] = test_df.index
    print(f"Test split size: {len(test_df):,} reviews (stratified random_state=42)")

    # Load preprocessed clean text
    if os.path.exists(cache_path):
        print(f"Loading preprocessed tokens from {cache_path}...")
        df_clean = pd.read_parquet(cache_path)
        test_df["clean_review"] = df_clean.loc[test_idx].values.ravel()
    else:
        print("Preprocessed cache not found; running preprocessing on test reviews...")
        test_df["clean_review"] = [preprocess_text(t) for t in test_df["review"]]

    # 1. Evaluate Logistic Regression
    print("\n[1/3] Predicting with Logistic Regression...")
    lr_model, tfidf, lr_err = load_artifacts("logistic_regression")
    if lr_err or lr_model is None or tfidf is None:
        raise RuntimeError(f"Failed to load Logistic Regression: {lr_err}")

    t0 = time.time()
    X_test_tfidf = tfidf.transform(test_df["clean_review"])
    lr_probs = lr_model.predict_proba(X_test_tfidf)[:, 1]
    lr_preds = (lr_probs >= 0.5).astype(int)
    print(f"Logistic Regression evaluated in {time.time() - t0:.2f}s (Accuracy: {(lr_preds == test_df['label']).mean() * 100:.2f}%)")

    # 2. Evaluate Naive Bayes
    print("\n[2/3] Predicting with Multinomial Naive Bayes...")
    nb_model, cv, nb_err = load_artifacts("naive_bayes")
    if nb_err or nb_model is None or cv is None:
        raise RuntimeError(f"Failed to load Naive Bayes: {nb_err}")

    t0 = time.time()
    X_test_cv = cv.transform(test_df["clean_review"])
    nb_probs = nb_model.predict_proba(X_test_cv)[:, 1]
    nb_preds = (nb_probs >= 0.5).astype(int)
    print(f"Naive Bayes evaluated in {time.time() - t0:.2f}s (Accuracy: {(nb_preds == test_df['label']).mean() * 100:.2f}%)")

    # 3. Evaluate BiLSTM
    print("\n[3/3] Predicting with PyTorch BiLSTM...")
    import torch
    lstm_model, vocab, lstm_err = load_artifacts("bilstm")
    if lstm_err or lstm_model is None or vocab is None:
        raise RuntimeError(f"Failed to load BiLSTM: {lstm_err}")

    t0 = time.time()
    max_len = 200
    seqs = []
    for clean_text in test_df["clean_review"]:
        tokens = str(clean_text).split()[:max_len]
        seq = [vocab.get(w, 1) for w in tokens]
        if len(seq) < max_len:
            seq = seq + [0] * (max_len - len(seq))
        seqs.append(seq)
    
    seq_tensor = torch.tensor(seqs, dtype=torch.int64)
    lstm_probs_list = []
    batch_size = 256
    lstm_model.eval()
    with torch.no_grad():
        for b_start in range(0, len(seq_tensor), batch_size):
            b_x = seq_tensor[b_start : b_start + batch_size]
            b_pred = lstm_model(b_x).squeeze(-1).cpu().numpy()
            if b_pred.ndim == 0:
                b_pred = np.array([float(b_pred)])
            lstm_probs_list.extend(b_pred.tolist())
    
    lstm_probs = np.array(lstm_probs_list, dtype=float)
    lstm_preds = (lstm_probs >= 0.5).astype(int)
    print(f"BiLSTM evaluated in {time.time() - t0:.2f}s (Accuracy: {(lstm_preds == test_df['label']).mean() * 100:.2f}%)")

    # Strip HTML tags from review text
    print("\nCleaning review text (stripping HTML tags)...")
    clean_raw_texts = [clean_html_and_urls(str(t)).strip() for t in test_df["review"]]

    # Construct export DataFrame
    out_df = pd.DataFrame({
        "review_id": test_df["review_id"],
        "text": clean_raw_texts,
        "label": test_df["label"].astype(int),
        "lr_pred": lr_preds,
        "lr_prob": np.round(lr_probs, 4),
        "lr_pos_prob": np.round(lr_probs, 4),
        "nb_pred": nb_preds,
        "nb_prob": np.round(nb_probs, 4),
        "nb_pos_prob": np.round(nb_probs, 4),
        "lstm_pred": lstm_preds,
        "lstm_prob": np.round(lstm_probs, 4),
        "lstm_pos_prob": np.round(lstm_probs, 4),
    })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    out_df.to_csv(output_path, index=False)
    print(f"\nSUCCESS: Exported {len(out_df):,} test predictions to {output_path}")
    print(f"Columns: {list(out_df.columns)}")


if __name__ == "__main__":
    export_test_predictions()

