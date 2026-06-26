// src/components/LoginPage.jsx
import { useState } from 'react'
import { login, register } from '../firebaseService'

export default function LoginPage({ onLogin }) {
  const [mode, setMode]       = useState('login')   // 'login' | 'register'
  const [name, setName]       = useState('')
  const [email, setEmail]     = useState('')
  const [password, setPassword] = useState('')
  const [status, setStatus]   = useState({ msg: '', type: '' })
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!email || !password) { setStatus({ msg: 'Please fill in all fields.', type: 'error' }); return }
    setLoading(true)
    setStatus({ msg: '⏳ Please wait…', type: 'loading' })
    try {
      let user
      if (mode === 'login') {
        user = await login(email, password)
      } else {
        const displayName = name.trim() || email.split('@')[0]
        user = await register(email, password, displayName)
      }
      setStatus({ msg: '✅ Success!', type: 'success' })
      setTimeout(() => onLogin(user), 500)
    } catch (err) {
      console.error("Auth/Register Error:", err)
      setStatus({ msg: parseError(err.message || ''), type: 'error' })
      setLoading(false)
    }
  }

  function switchMode(m) {
    setMode(m); setStatus({ msg: '', type: '' })
    setName(''); setEmail(''); setPassword('')
  }

  return (
    <div className="login-page">
      {/* Animated blobs */}
      <div className="login-blob b1" />
      <div className="login-blob b2" />
      <div className="login-blob b3" />

      <div className="login-card">
        <div className="login-logo">
          <span className="emoji">🎬</span>
          <h1>Movie Counter</h1>
          <p>Track your cinematic journey</p>
        </div>

        {/* Tab toggle */}
        <div className="login-tabs">
          <button
            type="button"
            className={mode === 'login' ? 'active' : 'inactive'}
            onClick={() => switchMode('login')}
          >Login</button>
          <button
            type="button"
            className={mode === 'register' ? 'active' : 'inactive'}
            onClick={() => switchMode('register')}
          >Register</button>
        </div>

        <form onSubmit={handleSubmit}>
          {mode === 'register' && (
            <div className="form-group">
              <label>Display Name</label>
              <input
                type="text"
                placeholder="Your name"
                value={name}
                onChange={e => setName(e.target.value)}
                disabled={loading}
              />
            </div>
          )}

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={e => setEmail(e.target.value)}
              disabled={loading}
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
              disabled={loading}
              required
            />
          </div>

          <div className={`status-msg ${status.type}`}>{status.msg}</div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Please wait…' : mode === 'login' ? 'Login →' : 'Create Account →'}
          </button>
        </form>
      </div>
    </div>
  )
}

function parseError(raw) {
  const lowercaseRaw = raw.toLowerCase()
  if (lowercaseRaw.includes('user-not-found') || lowercaseRaw.includes('wrong-password') || lowercaseRaw.includes('invalid-credential'))
    return '⚠ Wrong email or password.'
  if (lowercaseRaw.includes('email-already-in-use'))
    return '⚠ Email already registered. Try logging in.'
  if (lowercaseRaw.includes('weak-password'))
    return '⚠ Password must be at least 6 characters.'
  if (lowercaseRaw.includes('too-many-requests'))
    return '⚠ Too many attempts. Try again later.'
  if (lowercaseRaw.includes('invalid-api-key') || lowercaseRaw.includes('api-key'))
    return '⚠ Firebase API key not configured. See README.'
  if (lowercaseRaw.includes('permission') || lowercaseRaw.includes('permission-denied'))
    return '⚠ Firestore database permission denied. Please configure your Firestore Security Rules in the Firebase Console.'
  return '⚠ Something went wrong. Check your connection.'
}
