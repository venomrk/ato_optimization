import React, { useState } from 'react'
import { apiRequest } from '../api/client'

export default function ChatPage() {
  const [prompt, setPrompt] = useState('')
  const [mode, setMode] = useState('multi')
  const [combined, setCombined] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function onRun(e) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    setCombined('')
    try {
      const data = await apiRequest('/chat/completions', {
        method: 'POST',
        body: {
          agent_mode: mode,
          messages: [{ role: 'user', content: prompt }],
        },
      })
      setCombined(data.combined)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Chemistry chat</h2>
      <form onSubmit={onRun}>
        <label>Mode</label>
        <select value={mode} onChange={(e) => setMode(e.target.value)}>
          <option value="multi">Multi-agent</option>
          <option value="single">Single agent</option>
        </select>

        <div style={{ marginTop: 12 }}>
          <label>Prompt</label>
          <textarea rows={6} value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="Ask a chemistry/research question…" />
        </div>

        <div style={{ marginTop: 12 }}>
          <button disabled={loading || !prompt.trim()}>{loading ? 'Running…' : 'Run'}</button>
        </div>
      </form>

      {error && <div className="error">{error}</div>}

      {combined && (
        <div className="card" style={{ marginTop: 16, background: '#0f1524' }}>
          <h3>Result</h3>
          <pre>{combined}</pre>
        </div>
      )}
    </div>
  )
}
