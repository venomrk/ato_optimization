import React from 'react'
import { Link, Route, Routes, useNavigate } from 'react-router-dom'
import { clearToken, getToken } from './api/client'

import LoginPage from './pages/LoginPage.jsx'
import SignupPage from './pages/SignupPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import ResearchPage from './pages/ResearchPage.jsx'
import ChatPage from './pages/ChatPage.jsx'
import ProfilePage from './pages/ProfilePage.jsx'

function RequireAuth({ children }) {
  const token = getToken()
  if (!token) return <LoginPage />
  return children
}

export default function App() {
  const navigate = useNavigate()
  const token = getToken()

  return (
    <div className="container">
      <header className="header">
        <div className="brand">
          <Link to="/">rko.ai</Link>
        </div>
        <nav className="nav">
          {token ? (
            <>
              <Link to="/">Dashboard</Link>
              <Link to="/research">Research</Link>
              <Link to="/chat">Chemistry Chat</Link>
              <Link to="/profile">Profile</Link>
              <button
                className="linkButton"
                onClick={() => {
                  clearToken()
                  navigate('/login')
                }}
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login">Login</Link>
              <Link to="/signup">Sign up</Link>
            </>
          )}
        </nav>
      </header>

      <main>
        <Routes>
          <Route
            path="/"
            element={
              <RequireAuth>
                <DashboardPage />
              </RequireAuth>
            }
          />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route
            path="/research"
            element={
              <RequireAuth>
                <ResearchPage />
              </RequireAuth>
            }
          />
          <Route
            path="/chat"
            element={
              <RequireAuth>
                <ChatPage />
              </RequireAuth>
            }
          />
          <Route
            path="/profile"
            element={
              <RequireAuth>
                <ProfilePage />
              </RequireAuth>
            }
          />
        </Routes>
      </main>
    </div>
  )
}
