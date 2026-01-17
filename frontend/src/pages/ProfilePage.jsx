import React, { useEffect, useState } from 'react'
import { apiRequest } from '../api/client'

export default function ProfilePage() {
  const [me, setMe] = useState(null)
  const [plans, setPlans] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    Promise.all([apiRequest('/users/me'), apiRequest('/billing/plans', { auth: false })])
      .then(([meData, plansData]) => {
        setMe(meData)
        setPlans(plansData)
      })
      .catch((e) => setError(e.message))
  }, [])

  async function startCheckout() {
    setError(null)
    setLoading(true)
    try {
      const data = await apiRequest('/billing/checkout-session', { method: 'POST', body: { plan: 'premium' } })
      window.location.href = data.url
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function openPortal() {
    setError(null)
    setLoading(true)
    try {
      const data = await apiRequest('/billing/portal-session', { method: 'POST' })
      window.location.href = data.url
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Profile & Billing</h2>
      {error && <div className="error">{error}</div>}

      {!me ? (
        <div>Loading…</div>
      ) : (
        <>
          <div><b>Email:</b> {me.email}</div>
          <div><b>Plan:</b> {me.plan}</div>
          <div><b>Credits:</b> {me.credits_balance}</div>
        </>
      )}

      <div className="card" style={{ marginTop: 16, background: '#0f1524' }}>
        <h3>Plans</h3>
        <ul>
          {plans.map((p) => (
            <li key={p.id}>
              <b>{p.name}</b> – {p.monthly_credits ? `${p.monthly_credits} credits/month` : 'custom'}
            </li>
          ))}
        </ul>

        <div style={{ display: 'flex', gap: 12 }}>
          <button disabled={loading} onClick={startCheckout}>Upgrade to Premium</button>
          <button disabled={loading} onClick={openPortal}>Manage subscription</button>
        </div>
        <p style={{ opacity: 0.85 }}>
          Requires Stripe env vars on the backend.
        </p>
      </div>
    </div>
  )
}
