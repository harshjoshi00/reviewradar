import { useState } from 'react'
import ResultCard from './ResultCard'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const SAMPLES = [
  { label: 'Fake sample', text: 'This is the BEST product EVER!! I love it so much!!! Amazing quality, perfect in every way!! Highly recommend to everyone!!! Five stars!!! Must buy!!!' },
  { label: 'Genuine sample', text: "I've been using this for about three weeks now. The build quality is decent for the price point. Setup took around 20 minutes. It does what it claims to do, though I wish the battery lasted a bit longer. Overall a reasonable purchase." },
  { label: 'Suspicious', text: 'Outstanding product! Greatest thing I have ever purchased! Perfect in every single way! This company is absolutely wonderful and fantastic! Buy this immediately!' },
]

export default function AnalyzerPage({ onResult }) {
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const analyze = async () => {
    if (!text.trim() || text.trim().length < 5) return
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch(`${API}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text.trim() })
      })
      if (!res.ok) {
        const e = await res.json()
        throw new Error(e.detail || 'Prediction failed')
      }
      const data = await res.json()
      const full = { ...data, reviewText: text.trim() }
      setResult(full)
      onResult(full)
    } catch (err) {
      setError(
        err.message.includes('fetch')
          ? 'Cannot connect to backend. Make sure FastAPI is running on port 8000.'
          : err.message
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="hero">
        <h1>Detect <span>Fake Reviews</span> Instantly</h1>
        <p>Paste any product review and our AI will analyze its authenticity using NLP and machine learning.</p>
        <div className="hero-tags">
          <span className="tag tag--blue">Real-time Analysis</span>
          <span className="tag tag--green">96% Accuracy</span>
          <span className="tag tag--purple">72K Trained Reviews</span>
        </div>
      </div>

      <div className="grid-2">
        {/* Left: Input */}
        <div className="card">
          <div className="card-header">Review Input</div>
          <div className="input-wrap">
            <textarea
              id="review-input"
              className="textarea"
              placeholder="Paste a product review here..."
              value={text}
              onChange={e => setText(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && e.ctrlKey) analyze() }}
              maxLength={5000}
            />
            <span className="char-count">{text.length} / 5000</span>
          </div>

          <button
            id="analyze-btn"
            className="btn-primary"
            onClick={analyze}
            disabled={loading || text.trim().length < 5}
          >
            {loading
              ? <><div className="spinner" /> Analyzing...</>
              : 'Analyze Review'}
          </button>

          {error && <div className="error">⚠ {error}</div>}

          <div className="samples mt-12">
            <div className="samples-label">Quick test</div>
            <div className="samples-row">
              {SAMPLES.map((s, i) => (
                <button
                  key={i}
                  id={`sample-${i}`}
                  className="sample-chip"
                  onClick={() => setText(s.text)}
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Result */}
        <div>
          {result ? (
            <ResultCard result={result} />
          ) : (
            <div className="empty">
              <div className="empty-icon">🤖</div>
              <div className="empty-text">
                {loading ? 'Analyzing...' : 'Result will appear here'}
              </div>
              {!loading && <div className="empty-hint">Ctrl + Enter to analyze</div>}
            </div>
          )}
        </div>
      </div>
    </>
  )
}
