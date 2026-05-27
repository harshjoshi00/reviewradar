export default function ResultCard({ result }) {
  const fake = result.is_fake
  const cls = fake ? 'result--fake' : 'result--genuine'

  return (
    <div className={`result ${cls}`}>
      {/* Verdict */}
      <div className="verdict">
        <div className="verdict-badge">{fake ? '🚨' : '✅'}</div>
        <div className="verdict-text">
          <h2>{fake ? 'Fake Review' : 'Genuine Review'}</h2>
          <p>{fake
            ? 'Likely computer-generated or deceptive'
            : 'Appears to be authentic and human-written'}
          </p>
        </div>
      </div>

      {/* Confidence */}
      <div className="conf">
        <div className="conf-row">
          <span className="conf-label">Confidence</span>
          <span className="conf-val">{result.confidence}%</span>
        </div>
        <div className="conf-track">
          <div className="conf-fill" style={{ width: `${result.confidence}%` }} />
        </div>
      </div>

      {/* Probabilities */}
      <div className="probs">
        <div className="prob prob--fake">
          <div className="prob-num">{result.fake_probability}%</div>
          <div className="prob-label">Fake</div>
        </div>
        <div className="prob prob--genuine">
          <div className="prob-num">{result.genuine_probability}%</div>
          <div className="prob-label">Genuine</div>
        </div>
      </div>

      {/* Info */}
      <div className="info-row">
        <div className="info-box">
          <div className="info-num">{result.review_length}</div>
          <div className="info-label">Words</div>
        </div>
        <div className="info-box">
          <div className="info-num">{fake ? '⚠ Suspicious' : '● Authentic'}</div>
          <div className="info-label">Pattern</div>
        </div>
      </div>

      {/* Key Signals */}
      {result.top_words?.length > 0 && (
        <div>
          <div className="signals-title">Key Signals</div>
          <div className="signals-list">
            {result.top_words.map((w, i) => (
              <span
                key={i}
                className={`signal ${w.direction === 'fake' ? 'signal--fake' : 'signal--genuine'}`}
                title={`Score: ${w.score}`}
              >
                <span className="signal-dot" />
                {w.word}
              </span>
            ))}
          </div>
          <div className="signals-legend">
            Red = leans fake · Green = leans genuine
          </div>
        </div>
      )}
    </div>
  )
}
