"""
Training and evaluation script for CineSense models.
Reproduces the exact NLP pipeline and splits from the research notebook:
- 80/20 train/test stratified split (random_state=42)
- TF-IDF + Logistic Regression
- CountVectorizer + Multinomial Naive Bayes
- PyTorch Bidirectional LSTM
- Saves all model artifacts, evaluation metrics, confusion matrices, and ROC data.
"""

import json
import os
import sys
import time
from typing import Dict, Any

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    auc,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_curve,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

# Ensure root path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.preprocessing import preprocess_text


def log(msg: str):
    print(msg, flush=True)


def run_training():
    log("=" * 60)
    log("[CineSense] Model Training & Evaluation Pipeline Initiated")
    log("=" * 60)

    data_path = os.path.join("data", "IMDB Dataset.csv")
    if not os.path.exists(data_path):
        log(f"ERROR: Dataset file not found at {data_path}")
        sys.exit(1)

    log(f"Loading dataset from {data_path}...")
    df = pd.read_csv(data_path)
    log(f"Loaded {len(df)} reviews. Distribution: {df['sentiment'].value_counts().to_dict()}")

    df["label"] = df["sentiment"].astype(str).str.strip().str.lower().map({"positive": 1, "negative": 0})
    if df["label"].isnull().any():
        log("Warning: some sentiment labels could not be mapped!")
        df = df.dropna(subset=["label"])

    cache_path = os.path.join("data", "preprocessed_cache.parquet")
    if os.path.exists(cache_path):
        log(f"Loading preprocessed text from cache: {cache_path}")
        df_cached = pd.read_parquet(cache_path)
        if len(df_cached) == len(df):
            df["clean_review"] = df_cached["clean_review"]
        else:
            log("Cache length mismatch; reprocessing with parallel workers...")
            t0 = time.time()
            clean_list = joblib.Parallel(n_jobs=4, batch_size=250)(
                joblib.delayed(preprocess_text)(t) for t in df["review"]
            )
            df["clean_review"] = clean_list
            log(f"Preprocessed {len(df)} reviews in {time.time()-t0:.1f}s")
            df[["clean_review"]].to_parquet(cache_path)
    else:
        log("Preprocessing 50,000 reviews with parallel workers...")
        t0 = time.time()
        clean_list = joblib.Parallel(n_jobs=4, batch_size=250)(
            joblib.delayed(preprocess_text)(t) for t in df["review"]
        )
        df["clean_review"] = clean_list
        log(f"Preprocessed {len(df)} reviews in {time.time()-t0:.1f}s")
        try:
            df[["clean_review"]].to_parquet(cache_path)
            log(f"Saved preprocessed cache to {cache_path}")
        except Exception as e:
            log(f"Note: Could not save parquet cache ({e}); proceeding with memory DataFrame.")

    X = np.array(df["clean_review"].tolist(), dtype=object)
    y = np.array(df["label"].tolist(), dtype=int)

    # Stratified 80/20 train/test split (exact notebook configuration)
    log("\nSplitting train/test (80/20, random_state=42, stratify=y)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    log(f"Train size: {len(X_train)} | Test size: {len(X_test)}")
    log(f"Train balance: 0={np.sum(y_train==0)}, 1={np.sum(y_train==1)}")
    log(f"Test balance : 0={np.sum(y_test==0)}, 1={np.sum(y_test==1)}")

    os.makedirs("models", exist_ok=True)

    # ---------------------------------------------------------
    # 1. TF-IDF + Logistic Regression
    # ---------------------------------------------------------
    log("\n--- Training Model 1: Logistic Regression (TF-IDF) ---")
    tfidf = TfidfVectorizer(max_features=20000, ngram_range=(1, 2), min_df=3)
    t0 = time.time()
    X_train_tfidf = tfidf.fit_transform(X_train)
    X_test_tfidf = tfidf.transform(X_test)
    log(f"TF-IDF fitted in {time.time()-t0:.1f}s. Shape: {X_train_tfidf.shape}")

    lr_model = LogisticRegression(max_iter=1000, C=1.0, solver="lbfgs", random_state=42)
    t0 = time.time()
    lr_model.fit(X_train_tfidf, y_train)
    log(f"Logistic Regression fitted in {time.time()-t0:.1f}s")

    y_pred_lr = lr_model.predict(X_test_tfidf)
    y_prob_lr = lr_model.predict_proba(X_test_tfidf)[:, 1]

    lr_acc = float(accuracy_score(y_test, y_pred_lr))
    lr_prec = float(precision_score(y_test, y_pred_lr))
    lr_rec = float(recall_score(y_test, y_pred_lr))
    lr_f1 = float(f1_score(y_test, y_pred_lr))
    lr_auc = float(roc_auc_score(y_test, y_prob_lr))
    lr_cm = confusion_matrix(y_test, y_pred_lr).tolist()

    fpr_lr, tpr_lr, thresh_lr = roc_curve(y_test, y_prob_lr)
    step_lr = max(1, len(fpr_lr) // 100)
    roc_lr = {
        "fpr": [float(v) for v in fpr_lr[::step_lr]],
        "tpr": [float(v) for v in tpr_lr[::step_lr]],
        "auc": round(lr_auc, 4),
    }

    log(f"Logistic Regression: Accuracy={lr_acc*100:.2f}%, F1={lr_f1*100:.2f}%, AUC={lr_auc:.4f}")

    # Top predictive features for Logistic Regression
    feature_names = np.array(tfidf.get_feature_names_out())
    coefs = lr_model.coef_[0]
    top_pos_idx = np.argsort(coefs)[-25:][::-1]
    top_neg_idx = np.argsort(coefs)[:25]

    top_features = {
        "positive": [
            {"term": str(feature_names[i]), "weight": round(float(coefs[i]), 4)}
            for i in top_pos_idx
        ],
        "negative": [
            {"term": str(feature_names[i]), "weight": round(float(coefs[i]), 4)}
            for i in top_neg_idx
        ],
    }

    joblib.dump(lr_model, os.path.join("models", "logistic_regression.joblib"))
    joblib.dump(tfidf, os.path.join("models", "tfidf_vectorizer.joblib"))
    with open(os.path.join("models", "top_features.json"), "w", encoding="utf-8") as f:
        json.dump(top_features, f, indent=2)

    # ---------------------------------------------------------
    # 2. CountVectorizer + Multinomial Naive Bayes
    # ---------------------------------------------------------
    log("\n--- Training Model 2: Multinomial Naive Bayes (CountVectorizer) ---")
    cv = CountVectorizer(max_features=20000, ngram_range=(1, 2), min_df=3)
    t0 = time.time()
    X_train_cv = cv.fit_transform(X_train)
    X_test_cv = cv.transform(X_test)
    log(f"CountVectorizer fitted in {time.time()-t0:.1f}s. Shape: {X_train_cv.shape}")

    nb_model = MultinomialNB(alpha=0.1)
    t0 = time.time()
    nb_model.fit(X_train_cv, y_train)
    log(f"Naive Bayes fitted in {time.time()-t0:.1f}s")

    y_pred_nb = nb_model.predict(X_test_cv)
    y_prob_nb = nb_model.predict_proba(X_test_cv)[:, 1]

    nb_acc = float(accuracy_score(y_test, y_pred_nb))
    nb_prec = float(precision_score(y_test, y_pred_nb))
    nb_rec = float(recall_score(y_test, y_pred_nb))
    nb_f1 = float(f1_score(y_test, y_pred_nb))
    nb_auc = float(roc_auc_score(y_test, y_prob_nb))
    nb_cm = confusion_matrix(y_test, y_pred_nb).tolist()

    fpr_nb, tpr_nb, thresh_nb = roc_curve(y_test, y_prob_nb)
    step_nb = max(1, len(fpr_nb) // 100)
    roc_nb = {
        "fpr": [float(v) for v in fpr_nb[::step_nb]],
        "tpr": [float(v) for v in tpr_nb[::step_nb]],
        "auc": round(nb_auc, 4),
    }

    log(f"Naive Bayes: Accuracy={nb_acc*100:.2f}%, F1={nb_f1*100:.2f}%, AUC={nb_auc:.4f}")

    joblib.dump(nb_model, os.path.join("models", "naive_bayes.joblib"))
    joblib.dump(cv, os.path.join("models", "count_vectorizer.joblib"))

    # ---------------------------------------------------------
    # 3. Deep Learning (BiLSTM) with PyTorch
    # ---------------------------------------------------------
    log("\n--- Model 3: Bidirectional LSTM ---")
    bilstm_metrics = None
    try:
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, TensorDataset

        log("PyTorch detected. Building vocabulary and sequence pipeline...")
        word_counts: Dict[str, int] = {}
        for text in X_train:
            for w in text.split():
                word_counts[w] = word_counts.get(w, 0) + 1

        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        vocab = {"<PAD>": 0, "<OOV>": 1}
        for w, _ in sorted_words[:19998]:
            vocab[w] = len(vocab)

        max_len = 200

        def text_to_seq(text: str) -> list:
            tokens = text.split()
            seq = [vocab.get(w, 1) for w in tokens[:max_len]]
            if len(seq) < max_len:
                seq = seq + [0] * (max_len - len(seq))
            return seq

        log("Encoding sequence tensors for BiLSTM...")
        X_train_seq = np.array([text_to_seq(t) for t in X_train[:15000]], dtype=np.int64)
        y_train_sub = y_train[:15000]
        X_test_seq = np.array([text_to_seq(t) for t in X_test], dtype=np.int64)

        class PyTorchBiLSTM(nn.Module):
            def __init__(self, vocab_size=20000, embed_dim=64, hidden_dim=64):
                super().__init__()
                self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
                self.lstm = nn.LSTM(
                    embed_dim, hidden_dim, batch_first=True, bidirectional=True
                )
                self.fc1 = nn.Linear(hidden_dim * 2, 64)
                self.dropout1 = nn.Dropout(0.4)
                self.fc2 = nn.Linear(64, 32)
                self.dropout2 = nn.Dropout(0.3)
                self.out = nn.Linear(32, 1)
                self.relu = nn.ReLU()
                self.sigmoid = nn.Sigmoid()

            def forward(self, x):
                embeds = self.embedding(x)
                out, _ = self.lstm(embeds)
                pooled = torch.max(out, dim=1)[0]
                h1 = self.relu(self.fc1(pooled))
                h1 = self.dropout1(h1)
                h2 = self.relu(self.fc2(h1))
                h2 = self.dropout2(h2)
                logits = self.out(h2)
                return self.sigmoid(logits)

        lstm_model = PyTorchBiLSTM(vocab_size=len(vocab))
        criterion = nn.BCELoss()
        optimizer = torch.optim.Adam(lstm_model.parameters(), lr=0.003)

        train_loader = DataLoader(
            TensorDataset(
                torch.tensor(X_train_seq),
                torch.tensor(y_train_sub, dtype=torch.float32).unsqueeze(1),
            ),
            batch_size=128,
            shuffle=True,
        )

        log("Training BiLSTM for 2 epochs...")
        lstm_model.train()
        for epoch in range(2):
            epoch_loss = 0.0
            for bx, by in train_loader:
                optimizer.zero_grad()
                pred = lstm_model(bx)
                loss = criterion(pred, by)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()
            log(f"Epoch {epoch+1}/2 - Loss: {epoch_loss/len(train_loader):.4f}")

        # Evaluate on test set in batches
        lstm_model.eval()
        test_preds = []
        with torch.no_grad():
            for i in range(0, len(X_test_seq), 256):
                batch_x = torch.tensor(X_test_seq[i : i + 256])
                batch_pred = lstm_model(batch_x).squeeze().numpy()
                test_preds.extend(batch_pred.tolist() if batch_pred.ndim > 0 else [float(batch_pred)])

        y_prob_lstm = np.array(test_preds)
        y_pred_lstm = (y_prob_lstm >= 0.5).astype(int)

        lstm_acc = float(accuracy_score(y_test, y_pred_lstm))
        lstm_prec = float(precision_score(y_test, y_pred_lstm))
        lstm_rec = float(recall_score(y_test, y_pred_lstm))
        lstm_f1 = float(f1_score(y_test, y_pred_lstm))
        lstm_auc = float(roc_auc_score(y_test, y_prob_lstm))
        lstm_cm = confusion_matrix(y_test, y_pred_lstm).tolist()

        fpr_lstm, tpr_lstm, _ = roc_curve(y_test, y_prob_lstm)
        step_lstm = max(1, len(fpr_lstm) // 100)
        roc_lstm = {
            "fpr": [float(v) for v in fpr_lstm[::step_lstm]],
            "tpr": [float(v) for v in tpr_lstm[::step_lstm]],
            "auc": round(lstm_auc, 4),
        }

        log(f"BiLSTM: Accuracy={lstm_acc*100:.2f}%, F1={lstm_f1*100:.2f}%, AUC={lstm_auc:.4f}")

        torch.save(lstm_model.state_dict(), os.path.join("models", "bilstm_model.pt"))
        with open(os.path.join("models", "bilstm_vocab.json"), "w", encoding="utf-8") as f:
            json.dump(vocab, f)

        bilstm_metrics = {
            "accuracy": round(lstm_acc, 4),
            "precision": round(lstm_prec, 4),
            "recall": round(lstm_rec, 4),
            "f1": round(lstm_f1, 4),
            "roc_auc": round(lstm_auc, 4),
            "confusion_matrix": lstm_cm,
            "roc_curve": roc_lstm,
            "status": "available",
            "framework": "PyTorch",
        }
    except Exception as e:
        log(f"BiLSTM training could not complete or was skipped: {e}")
        bilstm_metrics = {
            "status": "unavailable",
            "reason": str(e),
        }

    # ---------------------------------------------------------
    # Save Verified Evaluation Summary
    # ---------------------------------------------------------
    summary = {
        "test_sample_size": len(y_test),
        "split_config": {
            "test_size": 0.2,
            "random_state": 42,
            "stratified": True,
        },
        "models": {
            "logistic_regression": {
                "name": "Logistic Regression",
                "feature_extractor": "TF-IDF (1-2 ngrams, max 20,000 features)",
                "accuracy": round(lr_acc, 4),
                "precision": round(lr_prec, 4),
                "recall": round(lr_rec, 4),
                "f1": round(lr_f1, 4),
                "roc_auc": round(lr_auc, 4),
                "confusion_matrix": lr_cm,
                "roc_curve": roc_lr,
                "status": "available",
            },
            "naive_bayes": {
                "name": "Multinomial Naive Bayes",
                "feature_extractor": "CountVectorizer (1-2 ngrams, max 20,000 features, alpha=0.1)",
                "accuracy": round(nb_acc, 4),
                "precision": round(nb_prec, 4),
                "recall": round(nb_rec, 4),
                "f1": round(nb_f1, 4),
                "roc_auc": round(nb_auc, 4),
                "confusion_matrix": nb_cm,
                "roc_curve": roc_nb,
                "status": "available",
            },
        },
    }

    if bilstm_metrics:
        summary["models"]["bilstm"] = {
            "name": "Bidirectional LSTM",
            "feature_extractor": "Embedding (64) + BiLSTM (64) + GlobalMaxPooling + Dense",
            **bilstm_metrics,
        }

    eval_path = os.path.join("models", "evaluation_summary.json")
    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    log(f"\n[CineSense] All artifacts successfully saved to 'models/' directory!")
    log(f"Summary written to {eval_path}")


if __name__ == "__main__":
    run_training()
