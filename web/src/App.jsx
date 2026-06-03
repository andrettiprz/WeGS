import { useState, useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import HomePage from './pages/HomePage'
import PassesPage from './pages/PassesPage'
import PassDetailPage from './pages/PassDetailPage'
import ErrorBoundary from './components/ErrorBoundary'
import { fetchPasses } from './lib/data'

function App() {
  const [passes, setPasses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [config, setConfig] = useState({})

  const stationName = config.station_name || 'My Ground Station'

  useEffect(() => {
    // Load config first
    fetch('/config.json')
      .then(r => r.json())
      .then(cfg => { window.__WEGS_CONFIG__ = cfg; setConfig(cfg) })
      .catch(() => {}) // config.json is optional
  }, [])

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const data = await fetchPasses()
        if (!cancelled) {
          setPasses(data)
          setLoading(false)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message)
          setLoading(false)
        }
      }
    }
    load()
    return () => { cancelled = true }
  }, [])

  return (
    <>
      <a href="#main-content" className="skip-nav">{config.skipNavText || 'Skip to content'}</a>
      <Navbar passes={passes} stationName={stationName} />
      <div id="main-content">
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={
              <HomePage passes={passes} loading={loading} error={error} stationName={stationName} />
            } />
            <Route path="/pases" element={
              <PassesPage passes={passes} loading={loading} error={error} />
            } />
            <Route path="/pase/:id" element={
              <PassDetailPage />
            } />
          </Routes>
        </ErrorBoundary>
      </div>
      <Footer
        stationName={stationName}
        mapSrc={config.maps_embed_url || ''}
        githubUrl={config.github_url || 'https://github.com/andrettiprz/WeGS'}
      />
    </>
  )
}

export default App
