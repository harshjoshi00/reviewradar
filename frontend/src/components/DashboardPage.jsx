import { useEffect, useRef } from 'react'

export default function DashboardPage({ stats }) {
  const canvasRef = useRef(null)
  const total = stats.total || 0
  const fk = stats.fake || 0
  const gn = stats.genuine || 0
  const fkPct = total > 0 ? Math.round((fk / total) * 100) : 0
  const gnPct = total > 0 ? Math.round((gn / total) * 100) : 0
  const avgConf = stats.recent?.length
    ? Math.round(stats.recent.reduce((a, r) => a + r.confidence, 0) / stats.recent.length)
    : 0

  // Canvas donut
  useEffect(() => {
    const c = canvasRef.current
    if (!c) return
    const ctx = c.getContext('2d')
    const s = c.width, cx = s / 2, cy = s / 2
    const outer = s * 0.42, width = s * 0.13
    ctx.clearRect(0, 0, s, s)

    // Background ring
    ctx.beginPath()
    ctx.arc(cx, cy, outer - width / 2, 0, Math.PI * 2)
    ctx.strokeStyle = 'rgba(255,255,255,0.04)'
    ctx.lineWidth = width
    ctx.lineCap = 'round'
    ctx.stroke()

    if (total === 0) {
      ctx.fillStyle = 'rgba(161,161,170,0.5)'
      ctx.font = `600 ${s * 0.09}px Inter`
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText('No data', cx, cy)
      return
    }

    const gap = 0.06
    const fakeAngle = (fk / total) * Math.PI * 2

    // Fake arc
    if (fk > 0) {
      ctx.beginPath()
      ctx.arc(cx, cy, outer - width / 2, -Math.PI / 2, -Math.PI / 2 + fakeAngle - gap)
      ctx.strokeStyle = '#f43f5e'
      ctx.lineWidth = width
      ctx.lineCap = 'round'
      ctx.stroke()
    }

    // Genuine arc
    if (gn > 0) {
      ctx.beginPath()
      ctx.arc(cx, cy, outer - width / 2, -Math.PI / 2 + fakeAngle + gap, -Math.PI / 2 + Math.PI * 2 - gap)
      ctx.strokeStyle = '#10b981'
      ctx.lineWidth = width
      ctx.lineCap = 'round'
      ctx.stroke()
    }

    // Center text
    ctx.fillStyle = '#fafafa'
    ctx.font = `800 ${s * 0.16}px "JetBrains Mono", monospace`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(total, cx, cy - s * 0.03)
    ctx.fillStyle = 'rgba(161,161,170,0.6)'
    ctx.font = `500 ${s * 0.065}px Inter`
    ctx.fillText('analyzed', cx, cy + s * 0.08)
  }, [stats])

  // Confidence histogram
  const buckets = [0, 0, 0, 0, 0]
  stats.recent?.forEach(r => {
    const c = r.confidence
    if (c < 60) buckets[0]++
    else if (c < 70) buckets[1]++
    else if (c < 80) buckets[2]++
    else if (c < 90) buckets[3]++
    else buckets[4]++
  })
  const maxB = Math.max(...buckets, 1)
  const bucketLabels = ['< 60%', '60-70', '70-80', '80-90', '90%+']
  const bucketColors = ['#6366f1', '#818cf8', '#a78bfa', '#c084fc', '#e879f9']

  return (
    <>
      <div className="hero">
        <h1>Analytics <span>Dashboard</span></h1>
        <p>Live session statistics from your review analyses.</p>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat">
          <div className="stat-num" style={{ color: 'var(--text-1)' }}>{total}</div>
          <div className="stat-label">Total</div>
        </div>
        <div className="stat">
          <div className="stat-num" style={{ color: 'var(--red)' }}>{fk}</div>
          <div className="stat-label">Fake</div>
        </div>
        <div className="stat">
          <div className="stat-num" style={{ color: 'var(--green)' }}>{gn}</div>
          <div className="stat-label">Genuine</div>
        </div>
        <div className="stat">
          <div className="stat-num" style={{ color: 'var(--purple)' }}>{avgConf}%</div>
          <div className="stat-label">Avg Confidence</div>
        </div>
      </div>

      {/* Charts */}
      <div className="dash-grid">
        <div className="card">
          <div className="card-header">Fake vs Genuine</div>
          <div className="donut-layout">
            <canvas ref={canvasRef} id="donut" width={160} height={160} style={{ flexShrink: 0 }} />
            <div className="donut-legend">
              <div className="legend-row">
                <div className="legend-dot" style={{ background: '#f43f5e' }} />
                <span>Fake</span>
                <span className="legend-pct" style={{ color: '#f43f5e' }}>{fkPct}%</span>
              </div>
              <div className="legend-row">
                <div className="legend-dot" style={{ background: '#10b981' }} />
                <span>Genuine</span>
                <span className="legend-pct" style={{ color: '#10b981' }}>{gnPct}%</span>
              </div>
              <div className="legend-note">
                {total === 0 ? 'Analyze reviews to see data' : `${fk} of ${total} flagged`}
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">Confidence Distribution</div>
          {total === 0 ? (
            <div className="empty" style={{ minHeight: 140, border: 'none', background: 'transparent' }}>
              <div className="empty-icon">📊</div>
              <div className="empty-text">No data yet</div>
            </div>
          ) : (
            <div>
              {bucketLabels.map((label, i) => (
                <div key={i} className="hist-row">
                  <div className="hist-label">{label}</div>
                  <div className="hist-track">
                    <div
                      className="hist-bar"
                      style={{
                        width: `${(buckets[i] / maxB) * 100}%`,
                        background: bucketColors[i]
                      }}
                    >
                      {buckets[i] > 0 && <span>{buckets[i]}</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Recent */}
      <div className="card">
        <div className="card-header">Recent Analyses</div>
        {stats.recent?.length > 0 ? (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Preview</th>
                  <th>Result</th>
                  <th>Conf.</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent.slice(0, 10).map((r, i) => (
                  <tr key={i}>
                    <td className="td-idx">{String(i + 1).padStart(2, '0')}</td>
                    <td className="td-preview">{r.reviewText || '—'}</td>
                    <td>
                      <span className={`pill ${r.is_fake ? 'pill--fake' : 'pill--genuine'}`}>
                        {r.is_fake ? 'Fake' : 'Genuine'}
                      </span>
                    </td>
                    <td className="td-mono" style={{ color: r.is_fake ? 'var(--red)' : 'var(--green)' }}>
                      {r.confidence}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty" style={{ minHeight: 120, border: 'none', background: 'transparent' }}>
            <div className="empty-icon">🕒</div>
            <div className="empty-text">No analyses yet</div>
          </div>
        )}
      </div>
    </>
  )
}
