import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { apiRequest, setToken } from '../api/client'

export default function SignupPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function onSubmit(e) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const data = await apiRequest('/auth/signup', { method: 'POST', body: { email, password }, auth: false })
      setToken(data.access_token)
      navigate('/')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Create account</h2>
      <p>Free tier includes 100 credits/month.</p>
      <form onSubmit={onSubmit}>
        <div className="row">
          <div>
            <label>Email</label>
            <input value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div>
            <label>Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
        </div>
        <div style={{ marginTop: 12, display: 'flex', gap: 12 }}>
          <button disabled={loading}>{loading ? 'Creating…' : 'Sign up'}</button>
          <Link to="/login">Already have an account?</Link>
        </div>
        {error && <div className="error">{error}</div>}
      </form>
    </div>
  )
}
