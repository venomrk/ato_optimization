import React, { useEffect, useState } from 'react'
import { apiRequest } from '../api/client'

export default function DashboardPage() {
  const [me, setMe] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    apiRequest('/users/me')
      .then(setMe)
      .catch((e) => setError(e.message))
  }, [])

  return (
    <>
      <div className="card">
        <h2>Dashboard</h2>
        {error && <div className="error">{error}</div>}
        {!me ? (
          <div>Loading…</div>
        ) : (
          <>
            <div><b>Email:</b> {me.email}</div>
            <div><b>Plan:</b> {me.plan}</div>
            <div><b>Credits remaining:</b> {me.credits_balance}</div>
            <div><b>Next credit reset:</b> {new Date(me.credits_reset_at).toLocaleString()}</div>
          </>
        )}
      </div>

      <div className="card">
        <h3>Quick start</h3>
        <ul>
          <li>Use <b>Research</b> to search Google Scholar (requires SERPAPI_API_KEY).</li>
          <li>Use <b>Chemistry Chat</b> to run multi-agent chat (requires OPENROUTER_API_KEY).</li>
        </ul>
      </div>
    </>
  )
}
