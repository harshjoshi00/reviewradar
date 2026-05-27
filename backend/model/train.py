"""
train.py -- Model Training Script for Fake Review Detection
Run this once to train and save the model.

Usage:
    python backend/model/train.py
"""

import os
import re
import pickle
import warnings
import sys
import time
import numpy as np
import pandas as pd
from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)

# Fix Windows terminal encoding for Python 3.7+
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Import handcrafted features
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.features import extract_handcrafted_features

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────
DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "Dataset",
    "fake reviews dataset.csv",
)
ARTIFACTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "artifacts"
)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)


# ──────────────────────────────────────────────────────
# STEP 1: Load Dataset
# ──────────────────────────────────────────────────────
print("=" * 60)
print("  FAKE REVIEW DETECTION — MODEL TRAINING (v2.0)")
print("=" * 60)
print()

print("[1/10] Loading dataset...")
df = pd.read_csv(DATASET_PATH)
print(f"   OK - Loaded {len(df):,} reviews")
print(f"   Label distribution:\n{df['label'].value_counts().to_string()}\n")

# CG = Computer Generated = Fake = 1
# OR = Original = Genuine = 0
df["label_binary"] = (df["label"] == "CG").astype(int)


# ──────────────────────────────────────────────────────
# STEP 2: Clean Text (IMPROVED)
# ──────────────────────────────────────────────────────
def clean_text(text: str) -> str:
    text = str(text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\d+", " NUM ", text)           # Normalize numbers
    text = re.sub(r"[^\w\s!?.]", " ", text)
    text = re.sub(r"(.)\1{3,}", r"\1\1", text)    # Reduce repeated chars
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


print("[2/10] Cleaning text...")
df["clean_text"] = df["text_"].apply(clean_text)
df = df.dropna(subset=["clean_text"])
df = df[df["clean_text"].str.len() > 5]
print(f"   OK - {len(df):,} reviews after cleaning\n")


# ──────────────────────────────────────────────────────
# STEP 3: Train/Test Split
# ──────────────────────────────────────────────────────
X_text = df["clean_text"].values
y = df["label_binary"].values

X_train_text, X_test_text, y_train, y_test = train_test_split(
    X_text, y, test_size=0.2, random_state=42, stratify=y
)
print(f"[3/10] Train: {len(X_train_text):,} | Test: {len(X_test_text):,}\n")


# ──────────────────────────────────────────────────────
# STEP 4: TF-IDF Vectorization (UPGRADED)
# ──────────────────────────────────────────────────────
print("[4/10] Fitting TF-IDF vectorizer (30K features, trigrams)...")
tfidf = TfidfVectorizer(
    max_features=30000,
    ngram_range=(1, 3),
    sublinear_tf=True,
    min_df=2,
    max_df=0.95,
    strip_accents="unicode",
    analyzer="word",
    token_pattern=r"\w{2,}",
)
X_train_tfidf = tfidf.fit_transform(X_train_text)
X_test_tfidf = tfidf.transform(X_test_text)
print(f"   OK - Vocabulary size: {len(tfidf.vocabulary_):,}\n")


# ──────────────────────────────────────────────────────
# STEP 5: Handcrafted Features (EXPANDED — 25 features)
# ──────────────────────────────────────────────────────
print("[5/10] Extracting handcrafted features (25 features)...")
X_train_hc = csr_matrix(
    np.vstack(pd.Series(X_train_text).apply(extract_handcrafted_features).values)
)
X_test_hc = csr_matrix(
    np.vstack(pd.Series(X_test_text).apply(extract_handcrafted_features).values)
)
print(f"   OK - {X_train_hc.shape[1]} handcrafted features extracted\n")


# ──────────────────────────────────────────────────────
# STEP 6: Combine Features
# ──────────────────────────────────────────────────────
print("[6/10] Combining features...")
X_train_combined = hstack([X_train_tfidf, X_train_hc])
X_test_combined = hstack([X_test_tfidf, X_test_hc])
print(f"   OK - Total features: {X_train_combined.shape[1]:,}\n")


# ──────────────────────────────────────────────────────
# STEP 7: Hyperparameter Tuning with GridSearchCV
# ──────────────────────────────────────────────────────
print("[7/10] Hyperparameter tuning with GridSearchCV (5-fold CV)...")
print("       This may take 3-5 minutes. Please wait...\n")

param_grid = {
    "C": [0.5, 1.0, 5.0, 10.0],
    "solver": ["lbfgs", "liblinear"],
    "penalty": ["l2"],
    "max_iter": [2000],
}

start_time = time.time()

grid = GridSearchCV(
    LogisticRegression(class_weight="balanced", random_state=42),
    param_grid,
    cv=5,
    scoring="roc_auc",
    n_jobs=1,
    verbose=1,
)
grid.fit(X_train_combined, y_train)
model = grid.best_estimator_

elapsed = time.time() - start_time
print(f"\n   OK - Best params: {grid.best_params_}")
print(f"   OK - Best CV AUC: {grid.best_score_:.4f}")
print(f"   OK - Tuning took {elapsed:.1f}s\n")


# ──────────────────────────────────────────────────────
# STEP 8: Cross-Validation for Robust Metrics
# ──────────────────────────────────────────────────────
print("[8/10] Running 5-fold cross-validation on best model...")
cv_accuracy = cross_val_score(model, X_train_combined, y_train, cv=5, scoring="accuracy", n_jobs=1)
cv_auc = cross_val_score(model, X_train_combined, y_train, cv=5, scoring="roc_auc", n_jobs=1)
print(f"   5-Fold CV Accuracy: {cv_accuracy.mean()*100:.2f}% ± {cv_accuracy.std()*100:.2f}%")
print(f"   5-Fold CV ROC-AUC:  {cv_auc.mean():.4f} ± {cv_auc.std():.4f}\n")


# ──────────────────────────────────────────────────────
# STEP 9: Evaluate on Test Set
# ──────────────────────────────────────────────────────
print("[9/10] Evaluating on test set...")
y_pred = model.predict(X_test_combined)
y_proba = model.predict_proba(X_test_combined)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_proba)

print()
print("=" * 60)
print("  MODEL EVALUATION RESULTS (v2.0 — Improved)")
print("=" * 60)
print(f"  Test Accuracy : {accuracy * 100:.2f}%")
print(f"  Test ROC-AUC  : {auc:.4f}")
print(f"  CV Accuracy   : {cv_accuracy.mean()*100:.2f}% ± {cv_accuracy.std()*100:.2f}%")
print(f"  CV ROC-AUC    : {cv_auc.mean():.4f} ± {cv_auc.std():.4f}")
print(f"  Best Params   : {grid.best_params_}")
print()
print(classification_report(y_test, y_pred, target_names=["Genuine (OR)", "Fake (CG)"]))
cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:")
print(f"  True Genuine:  {cm[0][0]:,}  |  False Fake:  {cm[0][1]:,}")
print(f"  False Genuine: {cm[1][0]:,}  |  True Fake:   {cm[1][1]:,}")
print("=" * 60)


# ──────────────────────────────────────────────────────
# STEP 10: Save Artifacts
# ──────────────────────────────────────────────────────
print("\n[10/10] Saving artifacts...")

model_path = os.path.join(ARTIFACTS_DIR, "model.pkl")
vectorizer_path = os.path.join(ARTIFACTS_DIR, "vectorizer.pkl")
meta_path = os.path.join(ARTIFACTS_DIR, "meta.pkl")

with open(model_path, "wb") as f:
    pickle.dump(model, f)

with open(vectorizer_path, "wb") as f:
    pickle.dump(tfidf, f)

meta = {
    "accuracy": round(accuracy * 100, 2),
    "auc": round(auc, 4),
    "cv_accuracy": round(cv_accuracy.mean() * 100, 2),
    "cv_accuracy_std": round(cv_accuracy.std() * 100, 2),
    "cv_auc": round(cv_auc.mean(), 4),
    "train_size": len(X_train_text),
    "test_size": len(X_test_text),
    "vocabulary_size": len(tfidf.vocabulary_),
    "handcrafted_features": X_train_hc.shape[1],
    "total_features": X_train_combined.shape[1],
    "best_params": grid.best_params_,
    "label_map": {"CG": "Fake", "OR": "Genuine"},
    "version": "2.0",
}
with open(meta_path, "wb") as f:
    pickle.dump(meta, f)

print(f"   Model saved   -> {model_path}")
print(f"   Vectorizer    -> {vectorizer_path}")
print(f"   Meta info     -> {meta_path}")
print("\n>>> Training complete! Run the FastAPI server next.")
