# 📡 ReviewRadar - Fake Review Detection System

> Spot fake product reviews instantly using ML and NLP — paste any review, get an AI-powered verdict with confidence score and word-level explanations.

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61dafb?style=flat-square&logo=react)](https://react.dev)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-orange?style=flat-square)](https://scikit-learn.org)

---

## 🔬 How It Works

```
Raw Text → Cleaning → TF-IDF (30K features) → 25 Handcrafted Features → Logistic Regression → Prediction
```

1. **Text Preprocessing** — Cleans URLs, normalizes numbers, reduces repeated characters
2. **TF-IDF Vectorization** — 30,000 n-gram features (unigram + bigram + trigram)
3. **Handcrafted Features** — 25 linguistic signals: caps ratio, stopword ratio, hedge words, urgency words, readability, specificity, etc.
4. **Logistic Regression** — Hyperparameter-tuned with GridSearchCV, balanced class weights
5. **Explainability** — Top contributing words extracted from model coefficients

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + Vite |
| Styling | Vanilla CSS (Dark Theme, Glassmorphism) |
| Backend | FastAPI + Uvicorn |
| ML | scikit-learn (Logistic Regression + GridSearchCV) |
| NLP | TF-IDF Vectorizer (30K features, trigrams) |
| Explainability | Model Coefficient Analysis |

---

## ⚙️ Setup & Running

> Run all commands from the **project root**. You need **two terminal windows**.

### Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |

### Quick Start

```powershell
# Terminal 1 — Backend
.\venv\Scripts\Activate.ps1
.\venv\Scripts\python.exe backend\model\train.py          # Run once
.\venv\Scripts\uvicorn.exe backend.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

> **First time?** Create venv first:
> ```powershell
> python -m venv venv
> .\venv\Scripts\Activate.ps1
> pip install -r backend\requirements.txt
> cd frontend && npm install
> ```

- 🌐 Frontend: **http://localhost:5173**
- 🔧 Backend: **http://localhost:8000**
- 📖 API Docs: **http://localhost:8000/docs**

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/predict` | Analyze single review |
| POST | `/batch` | Analyze up to 50 reviews |
| GET | `/stats` | Session analytics |
| GET | `/model-info` | Model metadata |

---

## 📦 Dataset

[Fake Reviews Dataset](https://www.kaggle.com/datasets/mexwell/fake-reviews-dataset) by mexwell — 72K+ labeled Amazon reviews (`CG` = Fake, `OR` = Genuine).

---

## 👨‍💻 Author

Built as a resume portfolio project demonstrating full-stack ML engineering skills.
