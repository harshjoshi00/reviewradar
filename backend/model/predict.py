"""
predict.py — Prediction & Explanation Logic
Loads saved model artifacts and runs inference with LIME explanations.
"""

import os
import re
import pickle
import numpy as np
from scipy.sparse import hstack, csr_matrix

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.features import extract_handcrafted_features

# ─────────────────────────────────────────────
# Load Artifacts (once at startup)
# ─────────────────────────────────────────────
ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "artifacts")

_model = None
_vectorizer = None
_meta = None


def _load_artifacts():
    global _model, _vectorizer, _meta
    if _model is None:
        with open(os.path.join(ARTIFACTS_DIR, "model.pkl"), "rb") as f:
            _model = pickle.load(f)
        with open(os.path.join(ARTIFACTS_DIR, "vectorizer.pkl"), "rb") as f:
            _vectorizer = pickle.load(f)
        with open(os.path.join(ARTIFACTS_DIR, "meta.pkl"), "rb") as f:
            _meta = pickle.load(f)


def get_meta():
    _load_artifacts()
    return _meta


# ─────────────────────────────────────────────
# Text Cleaning
# ─────────────────────────────────────────────
def clean_text(text: str) -> str:
    text = str(text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\d+", " NUM ", text)           # Normalize numbers
    text = re.sub(r"[^\w\s!?.]", " ", text)
    text = re.sub(r"(.)\1{3,}", r"\1\1", text)    # Reduce repeated chars
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


# ─────────────────────────────────────────────
# Core Prediction
# ─────────────────────────────────────────────
def predict_review(text: str) -> dict:
    """
    Predicts whether a review is Fake or Genuine.
    Returns label, confidence, probabilities, and top contributing words.
    """
    _load_artifacts()

    cleaned = clean_text(text)

    # TF-IDF features
    tfidf_vec = _vectorizer.transform([cleaned])

    # Handcrafted features
    hc_vec = csr_matrix(extract_handcrafted_features(cleaned).reshape(1, -1))

    # Combined
    combined = hstack([tfidf_vec, hc_vec])

    # Predict
    proba = _model.predict_proba(combined)[0]
    pred_class = int(np.argmax(proba))

    fake_prob = float(proba[1])
    genuine_prob = float(proba[0])
    confidence = float(max(proba))

    label = "Fake" if pred_class == 1 else "Genuine"

    # Top contributing words via model coefficients
    top_words = _get_top_words(cleaned, pred_class)

    return {
        "label": label,
        "is_fake": pred_class == 1,
        "confidence": round(confidence * 100, 2),
        "fake_probability": round(fake_prob * 100, 2),
        "genuine_probability": round(genuine_prob * 100, 2),
        "top_words": top_words,
        "review_length": len(text.split()),
    }


# ─────────────────────────────────────────────
# Top Contributing Words (Lightweight LIME-like)
# ─────────────────────────────────────────────
def _get_top_words(cleaned_text: str, pred_class: int, top_n: int = 8) -> list:
    """
    Returns top words contributing to the prediction using model coefficients.
    """
    vocab = _vectorizer.vocabulary_
    coefs = _model.coef_[0]  # shape: (n_features,)

    words = cleaned_text.split()
    word_scores = []

    for word in set(words):
        if word in vocab:
            idx = vocab[word]
            score = coefs[idx]
            # Positive coef = leans Fake, Negative = leans Genuine
            contribution = score if pred_class == 1 else -score
            word_scores.append({
                "word": word,
                "score": round(float(contribution), 4),
                "direction": "fake" if score > 0 else "genuine",
            })

    # Sort by absolute contribution
    word_scores.sort(key=lambda x: abs(x["score"]), reverse=True)
    return word_scores[:top_n]


# ─────────────────────────────────────────────
# Batch Prediction
# ─────────────────────────────────────────────
def predict_batch(texts: list[str]) -> list[dict]:
    """Predict multiple reviews at once."""
    return [predict_review(t) for t in texts]
