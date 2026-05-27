import { useState, useEffect } from 'react'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function AboutPage() {
  const [info, setInfo] = useState(null)

  useEffect(() => {
    fetch(`${API}/model-info`)
      .then(r => r.json())
      .then(setInfo)
      .catch(() => {})
  }, [])

  const features = [
    { icon: '🧠', title: 'TF-IDF + Logistic Regression', desc: 'Trained on 72K reviews with 15K n-gram features.' },
    { icon: '🔬', title: '13 Linguistic Features', desc: 'Caps ratio, superlatives, generic phrases, and more.' },
    { icon: '💡', title: 'Explainability', desc: 'Shows exactly which words drove each prediction.' },
    { icon: '⚡', title: 'FastAPI Backend', desc: 'Sub-100ms predictions with Pydantic validation.' },
    { icon: '📊', title: 'Live Analytics', desc: 'Session dashboard with charts and history.' },
    { icon: '🗃️', title: 'Kaggle Dataset', desc: '40K+ labeled reviews across product categories.' },
  ]

  const stack = [
    { layer: 'Frontend', tech: 'React + Vite', color: '#61dafb' },
    { layer: 'Styling', tech: 'Vanilla CSS', color: '#a78bfa' },
    { layer: 'Backend', tech: 'FastAPI', color: '#10b981' },
    { layer: 'ML Model', tech: 'scikit-learn', color: '#f59e0b' },
    { layer: 'NLP', tech: 'TF-IDF', color: '#6366f1' },
    { layer: 'XAI', tech: 'Coefficients', color: '#f43f5e' },
  ]

  const pipeline = [
    'Raw Text', 'Cleaning', 'TF-IDF', 'Features', 'LR Model', 'Prediction'
  ]

  return (
    <>
      <div className="hero">
        <h1>How <span>It Works</span></h1>
        <p>End-to-end ML pipeline from raw text to intelligent predictions.</p>
      </div>

      {/* Model Performance */}
      {info && (
        <div className="card mb-24">
          <div className="card-header" style={{ justifyContent: 'center' }}>Model Performance</div>
          <div className="perf-strip">
            <div className="perf-item">
              <div className="perf-num" style={{ color: 'var(--green)' }}>{info.accuracy}%</div>
              <div className="perf-label">Accuracy</div>
            </div>
            <div className="perf-divider" />
            <div className="perf-item">
              <div className="perf-num" style={{ color: 'var(--blue)' }}>{(info.auc * 100).toFixed(1)}%</div>
              <div className="perf-label">ROC-AUC</div>
            </div>
            <div className="perf-divider" />
            <div className="perf-item">
              <div className="perf-num" style={{ color: 'var(--purple)' }}>{(info.train_size / 1000).toFixed(0)}K</div>
              <div className="perf-label">Training Set</div>
            </div>
          </div>
        </div>
      )}

      {/* Pipeline */}
      <div className="card mb-24">
        <div className="card-header">ML Pipeline</div>
        <div className="pipeline">
          {pipeline.map((step, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div className="pipeline-step">{step}</div>
              {i < pipeline.length - 1 && <span className="pipeline-arrow">→</span>}
            </div>
          ))}
        </div>
      </div>

      {/* Features */}
      <div className="section-heading mb-16">Key Features</div>
      <div className="features mb-24">
        {features.map((f, i) => (
          <div key={i} className="feature">
            <div className="feature-icon">{f.icon}</div>
            <div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Tech Stack */}
      <div className="card">
        <div className="card-header">Technology Stack</div>
        <div className="stack-grid">
          {stack.map((s, i) => (
            <div key={i} className="stack-item" style={{ borderLeftColor: s.color }}>
              <div className="stack-layer">{s.layer}</div>
              <div className="stack-tech" style={{ color: s.color }}>{s.tech}</div>
            </div>
          ))}
        </div>

        <div className="credit">
          <div className="credit-title">Dataset Credit</div>
          <div className="credit-body">
            Trained on the <strong>Fake Reviews Dataset</strong> by mexwell on Kaggle — 
            72K+ labeled Amazon reviews (CG = Fake, OR = Genuine).
          </div>
        </div>
      </div>
    </>
  )
}
