# 🎯 Improve Model Accuracy: ~88% → 92%+

Your current model uses **Logistic Regression + TF-IDF (15K features) + 13 handcrafted features** and achieves ~88% accuracy / ~0.94 AUC. Here's a concrete plan to push it higher.

## Current Bottlenecks Identified

| Area | Current Setting | Problem |
|------|----------------|---------|
| TF-IDF | `max_features=15000`, `ngram_range=(1,2)` | Missing trigrams and char-level n-grams |
| Handcrafted Features | 13 features | Missing sentiment, readability, and structural signals |
| Model | Single LogisticRegression, `C=5.0` | No hyperparameter tuning, no cross-validation |
| Text Cleaning | Basic regex | No stopword removal, no lemmatization |
| Evaluation | Single train/test split | No k-fold cross-validation for robust metrics |

---

## Proposed Changes

### 1. Feature Engineering — [features.py](file:///d:/Fake Review Detection/backend/model/features.py)

#### [MODIFY] [features.py](file:///d:/Fake Review Detection/backend/model/features.py)

Add **12 new handcrafted features** (13 → 25 total):

| # | New Feature | Why It Helps |
|---|------------|--------------|
| 1 | `digit_ratio` | Fake reviews often lack specific numbers |
| 2 | `punctuation_density` | Over-punctuation signals fakeness |
| 3 | `repeated_char_count` | e.g. "sooooo goooood" — common in fake reviews |
| 4 | `url_count` | Genuine reviews rarely contain URLs |
| 5 | `emoji_count` | Pattern difference between fake/genuine |
| 6 | `stopword_ratio` | Fake reviews use fewer stopwords |
| 7 | `capital_word_ratio` | ALL CAPS WORDS ratio |
| 8 | `avg_syllables_per_word` | Readability proxy |
| 9 | `sentence_complexity` | Words per sentence variance |
| 10 | `hedge_word_count` | "maybe", "perhaps", "kind of" — genuine signal |
| 11 | `urgency_word_count` | "buy now", "hurry", "limited" — fake signal |
| 12 | `review_specificity` | Presence of specific details (numbers, dimensions, colors) |

---

### 2. TF-IDF Upgrade — [train.py](file:///d:/Fake Review Detection/backend/model/train.py)

#### [MODIFY] [train.py](file:///d:/Fake Review Detection/backend/model/train.py)

**Changes to vectorizer:**

```diff
 tfidf = TfidfVectorizer(
-    max_features=15000,
-    ngram_range=(1, 2),
+    max_features=30000,
+    ngram_range=(1, 3),
     sublinear_tf=True,
-    min_df=3,
+    min_df=2,
+    max_df=0.95,
     strip_accents="unicode",
     analyzer="word",
     token_pattern=r"\w{2,}",
 )
```

**What this does:**
- **30K features** → captures more discriminative terms
- **Trigrams** `(1,3)` → catches "I love this", "highly recommend this"
- **`max_df=0.95`** → removes words appearing in >95% of reviews (noise)
- **`min_df=2`** → slightly more inclusive of rare but discriminative terms

---

### 3. Hyperparameter Tuning with GridSearchCV — [train.py](file:///d:/Fake Review Detection/backend/model/train.py)

Replace the single `LogisticRegression(C=5.0)` with a grid search over multiple configurations:

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    "C": [0.5, 1.0, 5.0, 10.0],
    "solver": ["lbfgs", "liblinear"],
    "penalty": ["l2"],
    "max_iter": [2000],
}

grid = GridSearchCV(
    LogisticRegression(class_weight="balanced", random_state=42),
    param_grid,
    cv=5,
    scoring="roc_auc",
    n_jobs=-1,
    verbose=1,
)
grid.fit(X_train_combined, y_train)
model = grid.best_estimator_
```

> [!IMPORTANT]
> GridSearchCV will take **3–5 minutes** instead of ~30 seconds. It runs 5-fold CV across 8 parameter combos = 40 fits. This is a one-time training cost.

---

### 4. Cross-Validation for Robust Evaluation — [train.py](file:///d:/Fake Review Detection/backend/model/train.py)

Add stratified k-fold cross-validation to report stable metrics:

```python
from sklearn.model_selection import cross_val_score

cv_scores = cross_val_score(model, X_train_combined, y_train, cv=5, scoring="accuracy")
print(f"  5-Fold CV Accuracy: {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%")
```

---

### 5. Enhanced Text Cleaning — [train.py](file:///d:/Fake Review Detection/backend/model/train.py) and [predict.py](file:///d:/Fake Review Detection/backend/model/predict.py)

Minor improvements to `clean_text()`:

```diff
 def clean_text(text: str) -> str:
     text = str(text)
     text = re.sub(r"http\S+", "", text)
+    text = re.sub(r"\d+", " NUM ", text)          # Normalize numbers
     text = re.sub(r"[^\w\s!?.]", " ", text)
+    text = re.sub(r"(.)\1{3,}", r"\1\1", text)    # Reduce repeated chars
     text = re.sub(r"\s+", " ", text)
     return text.strip().lower()
```

---

## Summary of All File Changes

| File | Changes |
|------|---------|
| [features.py](file:///d:/Fake Review Detection/backend/model/features.py) | Add 12 new handcrafted features (13 → 25) |
| [train.py](file:///d:/Fake Review Detection/backend/model/train.py) | Upgrade TF-IDF (30K, trigrams), add GridSearchCV, add cross-validation, improve text cleaning |
| [predict.py](file:///d:/Fake Review Detection/backend/model/predict.py) | Sync `clean_text()` with training changes |

---

## Expected Improvement

| Metric | Before | After (Expected) |
|--------|--------|-------------------|
| Accuracy | ~88% | **91–93%** |
| ROC-AUC | ~0.94 | **0.96–0.97** |
| Training Time | ~30 sec | ~3–5 min (one-time) |
| Prediction Speed | instant | still instant (same model type) |

---

## Verification Plan

### Automated Tests
1. Run the improved `train.py` and compare metrics printed to console
2. Verify the new model loads correctly via `predict.py`
3. Test the `/predict` endpoint with sample reviews

### Manual Verification
- Compare accuracy, AUC, precision, recall, and F1 before and after
- Test edge cases: very short reviews, all-caps reviews, reviews with URLs

---

## Open Questions

> [!IMPORTANT]
> **Training time**: GridSearchCV with 5-fold CV will take **3–5 minutes**. Is that acceptable?

> [!NOTE]
> **Optional advanced upgrade**: Should I also add an **ensemble model** (e.g., combining Logistic Regression + SGD Classifier + Random Forest with soft voting)? This could push accuracy to ~94% but adds complexity and increases model file size.
