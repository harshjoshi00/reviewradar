import Logo from './Logo'

export default function Navbar({ page, setPage }) {
  return (
    <nav className="nav">
      <div className="nav-brand">
        <div className="nav-icon">
          <Logo size={16} />
        </div>
        <span className="nav-name">ReviewRadar</span>
      </div>
      <div className="nav-links">
        <button
          id="nav-analyzer"
          className={`nav-link ${page === 'analyzer' ? 'active' : ''}`}
          onClick={() => setPage('analyzer')}
        >
          Analyzer
        </button>
        <button
          id="nav-dashboard"
          className={`nav-link ${page === 'dashboard' ? 'active' : ''}`}
          onClick={() => setPage('dashboard')}
        >
          Dashboard
        </button>
      </div>
    </nav>
  )
}

