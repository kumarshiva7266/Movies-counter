// src/components/LoginPage.jsx
import { useState, useEffect } from 'react'
import { login, register } from '../firebaseService'

// Floating particles for the login page background
function Particles() {
  const particles = Array.from({ length: 20 }, (_, i) => ({
    id: i,
    size: Math.random() * 4 + 2,
    x: Math.random() * 100,
    delay: Math.random() * 8,
    duration: Math.random() * 10 + 8,
    color: ['#00f0ff', '#bf00ff', '#00ff88', '#ff0080', '#ff6b35'][Math.floor(Math.random() * 5)],
  }))

  return (
    <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', pointerEvents: 'none' }}>
      {particles.map(p => (
        <div key={p.id} style={{
          position: 'absolute',
          width: p.size, height: p.size,
          borderRadius: '50%',
          backgroundColor: p.color,
          left: `${p.x}%`,
          bottom: '-10px',
          boxShadow: `0 0 ${p.size * 3}px ${p.color}`,
          animation: `particleRise ${p.duration}s ${p.delay}s linear infinite`,
          opacity: 0,
        }} />
      ))}
      <style>{`
        @keyframes particleRise {
          0%   { transform: translateY(0) scale(1);    opacity: 0; }
          10%  { opacity: 0.8; }
          90%  { opacity: 0.4; }
          100% { transform: translateY(-110vh) scale(0.3); opacity: 0; }
        }
      `}</style>
    </div>
  )
}

// Animated grid in background
function GridBackground() {
  return (
    <div style={{
      position: 'absolute', inset: 0,
      backgroundImage: `
        linear-gradient(rgba(0,240,255,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,240,255,0.04) 1px, transparent 1px)
      `,
      backgroundSize: '60px 60px',
      maskImage: 'radial-gradient(ellipse 80% 80% at 50% 50%, black 40%, transparent 100%)',
      WebkitMaskImage: 'radial-gradient(ellipse 80% 80% at 50% 50%, black 40%, transparent 100%)',
    }} />
  )
}

export default function LoginPage({ onLogin }) {
  const [mode, setMode]         = useState('login')
  const [name, setName]         = useState('')
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [status, setStatus]     = useState({ msg: '', type: '' })
  const [loading, setLoading]   = useState(false)

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
      <GridBackground />
      <Particles />

      {/* Center third orb */}
      <div style={{
        position: 'absolute',
        width: 300, height: 300,
        top: '30%', left: '40%',
        background: 'radial-gradient(circle, rgba(0,255,136,0.12) 0%, transparent 70%)',
        borderRadius: '50%',
        animation: 'orb-float-3 12s ease-in-out infinite',
        pointerEvents: 'none',
      }} />

      <div className="login-card">
        <div className="login-logo">
          <span className="emoji">🎬</span>
          <h1>Movie Counter</h1>
          <p>Track your cinematic journey ✨</p>
        </div>

        {/* Tab toggle */}
        <div className="login-tabs">
          <button
            type="button"
            className={mode === 'login' ? 'active' : 'inactive'}
            onClick={() => switchMode('login')}
          >🔐 Login</button>
          <button
            type="button"
            className={mode === 'register' ? 'active' : 'inactive'}
            onClick={() => switchMode('register')}
          >🚀 Register</button>
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
            {loading ? '⏳ Please wait…' : mode === 'login' ? '⚡ Login' : '🚀 Create Account'}
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
