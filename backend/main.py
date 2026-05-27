"""
main.py — FastAPI Backend for Fake Review Detection System
Run with: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from model.predict import predict_review, predict_batch, get_meta

# ─────────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────────
app = FastAPI(
    title="Fake Review Detection API",
    description="AI-powered API to detect fake vs genuine product reviews.",
    version="1.0.0",
)

# Allow React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session stats
_session_stats = {
    "total_analyzed": 0,
    "total_fake": 0,
    "total_genuine": 0,
    "recent": [],  # last 50 results
}


# ─────────────────────────────────────────────
# Request / Response Models
# ─────────────────────────────────────────────
class ReviewRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=5000, description="Review text to analyze")


class BatchRequest(BaseModel):
    reviews: list[str] = Field(..., min_length=1, max_length=50)


class PredictionResult(BaseModel):
    label: str
    is_fake: bool
    confidence: float
    fake_probability: float
    genuine_probability: float
    top_words: list
    review_length: int


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "message": "Fake Review Detection API is running 🚀",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "timestamp": time.time()}


@app.post("/predict", response_model=PredictionResult, tags=["Prediction"])
def predict(request: ReviewRequest):
    """
    Analyze a single review and return fake/genuine prediction with confidence.
    """
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Review text cannot be empty.")

    try:
        result = predict_review(text)
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Model not trained yet. Please run: python model/train.py",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

    # Update session stats
    _session_stats["total_analyzed"] += 1
    if result["is_fake"]:
        _session_stats["total_fake"] += 1
    else:
        _session_stats["total_genuine"] += 1

    _session_stats["recent"].append({
        "text_preview": text[:80] + ("..." if len(text) > 80 else ""),
        "label": result["label"],
        "confidence": result["confidence"],
        "is_fake": result["is_fake"],
    })
    # Keep only last 50
    if len(_session_stats["recent"]) > 50:
        _session_stats["recent"] = _session_stats["recent"][-50:]

    return result


@app.post("/batch", tags=["Prediction"])
def batch_predict(request: BatchRequest):
    """
    Analyze multiple reviews in one request (max 50).
    """
    if len(request.reviews) > 50:
        raise HTTPException(status_code=400, detail="Max 50 reviews per batch request.")

    try:
        results = predict_batch(request.reviews)
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Model not trained yet. Please run: python model/train.py",
        )

    fake_count = sum(1 for r in results if r["is_fake"])
    return {
        "total": len(results),
        "fake_count": fake_count,
        "genuine_count": len(results) - fake_count,
        "results": results,
    }


@app.get("/stats", tags=["Analytics"])
def get_stats():
    """
    Returns session analytics — total reviews analyzed, fake/genuine counts.
    """
    total = _session_stats["total_analyzed"]
    fake = _session_stats["total_fake"]
    genuine = _session_stats["total_genuine"]

    return {
        "total_analyzed": total,
        "total_fake": fake,
        "total_genuine": genuine,
        "fake_percentage": round((fake / total * 100), 1) if total > 0 else 0,
        "genuine_percentage": round((genuine / total * 100), 1) if total > 0 else 0,
        "recent": list(reversed(_session_stats["recent"][-10:])),
    }


@app.get("/model-info", tags=["Analytics"])
def model_info():
    """
    Returns model metadata — accuracy, training size, etc.
    """
    try:
        meta = get_meta()
        return meta
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Model not trained yet. Run: python model/train.py",
        )


@app.delete("/stats/reset", tags=["Analytics"])
def reset_stats():
    """Reset session statistics."""
    _session_stats["total_analyzed"] = 0
    _session_stats["total_fake"] = 0
    _session_stats["total_genuine"] = 0
    _session_stats["recent"] = []
    return {"message": "Stats reset successfully."}
