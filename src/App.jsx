// src/App.jsx
import { useState, useEffect } from 'react'
import LoginPage from './components/LoginPage'
import Dashboard from './components/Dashboard'
import Toast from './components/Toast'
import { isFirebaseConfigured, auth } from './firebase'
import { onAuthStateChanged } from 'firebase/auth'

let toastCounter = 0

export default function App() {
  const [user, setUser]         = useState(null)
  const [loading, setLoading]   = useState(isFirebaseConfigured)
  const [toasts, setToasts]     = useState([])

  useEffect(() => {
    if (!isFirebaseConfigured) return

    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser)
      setLoading(false)
    })

    return () => unsubscribe()
  }, [])

  function addToast(message, type = 'success') {
    const id = ++toastCounter
    setToasts(prev => [...prev, { id, message, type }])
  }

  function removeToast(id) {
    setToasts(prev => prev.filter(t => t.id !== id))
  }

  function handleLogin(user) {
    setUser(user)
  }

  function handleLogout() {
    setUser(null)
  }

  if (!isFirebaseConfigured) {
    return (
      <div style={{ color: 'white', textAlign: 'center', marginTop: '50px', fontFamily: 'sans-serif' }}>
        <h2>⚠️ Firebase Configuration Missing</h2>
        <p>You need to set up your <code>.env</code> file with Firebase credentials.</p>
        <p>Copy <code>.env.example</code> to <code>.env</code> and fill in the values.</p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="page-loader">
        <div className="loader-spinner" />
        <div className="loader-text">Restoring session…</div>
      </div>
    )
  }

  return (
    <>

      {user ? (
        <Dashboard user={user} onLogout={handleLogout} addToast={addToast} />
      ) : (
        <LoginPage onLogin={handleLogin} />
      )}
      <Toast toasts={toasts} removeToast={removeToast} />
    </>
  )
}
