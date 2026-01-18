import React, { useState } from 'react'
import { apiRequest } from '../api/client'

export default function ResearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function onSearch(e) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    setResults([])
    try {
      const data = await apiRequest('/papers/search', { method: 'POST', body: { query, limit: 10 } })
      setResults(data.results || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Research search</h2>
      <form onSubmit={onSearch}>
        <label>Query</label>
        <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="e.g., perovskite degradation mechanism humidity" />
        <div style={{ marginTop: 12 }}>
          <button disabled={loading || !query.trim()}>{loading ? 'Searching…' : 'Search'}</button>
        </div>
      </form>
      {error && <div className="error">{error}</div>}

      <div style={{ marginTop: 16 }}>
        {results.map((r, idx) => (
          <div key={idx} className="card" style={{ background: '#0f1524' }}>
            <div style={{ fontWeight: 700 }}>{r.title || 'Untitled'}</div>
            {r.authors && <div style={{ opacity: 0.85 }}>{r.authors}</div>}
            {r.year && <div style={{ opacity: 0.85 }}>Year: {r.year}</div>}
            {r.snippet && <div style={{ marginTop: 8 }}>{r.snippet}</div>}
            {r.link && (
              <div style={{ marginTop: 8 }}>
                <a href={r.link} target="_blank" rel="noreferrer">Open</a>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
