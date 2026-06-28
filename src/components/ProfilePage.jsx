// src/components/ProfilePage.jsx
import { useEffect, useState } from 'react'

export default function ProfilePage({ user, displayName, movies, series, watchlist, onBack, onLogout }) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    // Trigger enter animation
    requestAnimationFrame(() => setVisible(true))
  }, [])

  function handleBack() {
    setVisible(false)
    setTimeout(onBack, 280)
  }

  const totalWatched = movies.length + series.length
  const initial = displayName ? displayName.charAt(0).toUpperCase() : '?'

  const joined = user.metadata?.creationTime
    ? new Date(user.metadata.creationTime).toLocaleDateString('en-IN', {
        year: 'numeric', month: 'long', day: 'numeric',
      })
    : 'N/A'

  return (
    <div className={`profile-page ${visible ? 'profile-page--in' : ''}`}>
      {/* Back button */}
      <button className="profile-page-back" onClick={handleBack} id="profile-back-btn">
        ← Back
      </button>

      <div className="profile-page-inner">
        {/* Avatar */}
        <div className="pp-avatar-wrap">
          <div className="pp-avatar">{initial}</div>
          <div className="pp-avatar-ring" />
        </div>

        {/* Name & email */}
        <h1 className="pp-name">{displayName}</h1>
        <p className="pp-email">{user.email}</p>
        <p className="pp-joined">Member since {joined}</p>

        {/* Divider */}
        <div className="pp-divider" />

        {/* Stats grid */}
        <div className="pp-stats-grid">
          <div className="pp-stat-card" style={{ '--accent': '#00f0ff' }}>
            <div className="pp-stat-emoji">🎬</div>
            <div className="pp-stat-val">{movies.length}</div>
            <div className="pp-stat-lbl">Movies Watched</div>
          </div>
          <div className="pp-stat-card" style={{ '--accent': '#bf00ff' }}>
            <div className="pp-stat-emoji">📺</div>
            <div className="pp-stat-val">{series.length}</div>
            <div className="pp-stat-lbl">Web Series</div>
          </div>
          <div className="pp-stat-card" style={{ '--accent': '#ffaa00' }}>
            <div className="pp-stat-emoji">👀</div>
            <div className="pp-stat-val">{watchlist.length}</div>
            <div className="pp-stat-lbl">Watchlist</div>
          </div>
          <div className="pp-stat-card" style={{ '--accent': '#00ff88' }}>
            <div className="pp-stat-emoji">🏆</div>
            <div className="pp-stat-val">{totalWatched}</div>
            <div className="pp-stat-lbl">Total Watched</div>
          </div>
        </div>

        {/* Logout */}
        <button className="pp-logout-btn" onClick={onLogout} id="profile-logout-btn">
          ⏻ &nbsp;Logout
        </button>
      </div>
    </div>
  )
}
