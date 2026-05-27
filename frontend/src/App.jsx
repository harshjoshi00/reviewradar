import { useState } from 'react'
import Navbar from './components/Navbar'
import AnalyzerPage from './components/AnalyzerPage'
import DashboardPage from './components/DashboardPage'
import './index.css'

export default function App() {
  const [page, setPage] = useState('analyzer')
  const [stats, setStats] = useState({
    total: 0, fake: 0, genuine: 0, recent: []
  })

  const addResult = (result) => {
    setStats(prev => ({
      total: prev.total + 1,
      fake: result.is_fake ? prev.fake + 1 : prev.fake,
      genuine: !result.is_fake ? prev.genuine + 1 : prev.genuine,
      recent: [result, ...prev.recent].slice(0, 20)
    }))
  }

  return (
    <div className="app">
      <Navbar page={page} setPage={setPage} />
      <main className="main">
        {page === 'analyzer' && <AnalyzerPage onResult={addResult} />}
        {page === 'dashboard' && <DashboardPage stats={stats} />}
      </main>
    </div>
  )
}

