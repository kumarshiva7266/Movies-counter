// src/components/Dashboard.jsx
import { useState, useEffect } from 'react'
import {
  getMovies, addMovie, deleteMovie,
  getWebseries, addWebseries, deleteWebseries,
  getWatchlist, addWatchlist, deleteWatchlist,
  getDisplayName, logout,
} from '../firebaseService'
import AddModal from './AddModal'
import ProfilePage from './ProfilePage'

export default function Dashboard({ user, onLogout, addToast }) {
  const uid = user.uid

  const [tab, setTab]           = useState('movies')
  const [movies, setMovies]     = useState([])
  const [series, setSeries]     = useState([])
  const [watchlist, setWatchlist] = useState([])
  const [search, setSearch]     = useState('')
  const [displayName, setDisplayName] = useState(user.displayName || 'User')
  const [showModal, setShowModal] = useState(false)
  const [showProfile, setShowProfile] = useState(false)
  const [page, setPage] = useState('dashboard') // 'dashboard' | 'profile'
  const [loading, setLoading]   = useState(true)

  // Load all data on mount
  useEffect(() => {
    async function load() {
      try {
        const [m, s, w] = await Promise.all([
          getMovies(uid), 
          getWebseries(uid), 
          getWatchlist(uid)
        ])
        setMovies(m)
        setSeries(s)
        setWatchlist(w)
      } catch (e) {
        addToast('Failed to load data: ' + e.message, 'error')
      } finally {
        setLoading(false)
      }
    }
    load()
    // Load display name
    getDisplayName(uid).then(n => setDisplayName(n)).catch(() => {})
  }, [uid])

  // Switch tabs resets search
  function switchTab(t) { setTab(t); setSearch('') }

  // Filtered list
  const data = tab === 'movies' ? movies : tab === 'webseries' ? series : watchlist;
  const filtered = search
    ? data.filter(i => i.name.toLowerCase().includes(search.toLowerCase()))
    : data

  // Add item
  async function handleAdd(name) {
    try {
      const lowerName = name.toLowerCase();
      
      if (tab === 'movies') {
        if (movies.some(m => m.name.toLowerCase() === lowerName)) {
          addToast(`"${name}" is already in your Movies!`, 'error');
          return;
        }
        const id = await addMovie(uid, name)
        setMovies(prev => [{ id, name }, ...prev])
      } else if (tab === 'webseries') {
        if (series.some(s => s.name.toLowerCase() === lowerName)) {
          addToast(`"${name}" is already in your Web Series!`, 'error');
          return;
        }
        const id = await addWebseries(uid, name)
        setSeries(prev => [{ id, name }, ...prev])
      } else {
        if (watchlist.some(w => w.name.toLowerCase() === lowerName)) {
          addToast(`"${name}" is already in your Watchlist!`, 'error');
          return;
        }
        const id = await addWatchlist(uid, name)
        setWatchlist(prev => [{ id, name }, ...prev])
      }
      addToast(`✅ "${name}" added!`, 'success')
    } catch (e) {
      addToast('Error: ' + e.message, 'error')
    }
  }

  // Delete item
  async function handleDelete(itemId) {
    try {
      if (tab === 'movies') {
        await deleteMovie(uid, itemId)
        setMovies(prev => prev.filter(m => m.id !== itemId))
      } else if (tab === 'webseries') {
        await deleteWebseries(uid, itemId)
        setSeries(prev => prev.filter(s => s.id !== itemId))
      } else {
        await deleteWatchlist(uid, itemId)
        setWatchlist(prev => prev.filter(w => w.id !== itemId))
      }
      addToast('🗑 Item deleted.', 'success')
    } catch (e) {
      addToast('Error: ' + e.message, 'error')
    }
  }

  async function handleLogout() {
    try { await logout() } catch (_) {}
    onLogout()
  }

  const tabTitle = tab === 'movies' ? '🎬 Movies' : tab === 'webseries' ? '📺 Web Series' : '👀 Watchlist'
  const tabSub   = tab === 'movies'
    ? 'Your watched movie collection'
    : tab === 'webseries'
      ? 'Your watched web series collection'
      : 'Movies and Web Series you want to watch'

  // ── Profile Page ──
  if (page === 'profile') {
    return (
      <ProfilePage
        user={user}
        displayName={displayName}
        movies={movies}
        series={series}
        watchlist={watchlist}
        onBack={() => setPage('dashboard')}
        onLogout={handleLogout}
      />
    )
  }

  return (
    <div className="app-layout">
      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="emoji">🎬</div>
          <h2>Movie Counter</h2>
        </div>

        <div className="sidebar-divider" />

        {/* Profile Circle Button */}
        <div className="profile-section">
          <button
            className="profile-circle-btn"
            onClick={() => setPage('profile')}
            title="View Profile"
          >
            {displayName ? displayName.charAt(0).toUpperCase() : '👤'}
          </button>
          <span className="profile-circle-name">{displayName}</span>
        </div>

        <div className="nav-label">LIBRARY</div>

        <button
          id="nav-movies"
          className={`nav-btn ${tab === 'movies' ? 'active' : 'inactive'}`}
          onClick={() => switchTab('movies')}
        >🎬 Movies</button>

        <button
          id="nav-series"
          className={`nav-btn ${tab === 'webseries' ? 'active' : 'inactive'}`}
          onClick={() => switchTab('webseries')}
        >📺 Web Series</button>

        <button
          id="nav-watchlist"
          className={`nav-btn ${tab === 'watchlist' ? 'active' : 'inactive'}`}
          onClick={() => switchTab('watchlist')}
        >👀 Watchlist</button>

        <div className="sidebar-spacer" />

        <button className="logout-btn" onClick={handleLogout} id="logout-btn">
          ⏻ Logout
        </button>
      </aside>

      {/* ── Main ── */}
      <main className="main-area">
        {/* Header */}
        <div className="main-header">
          <h1>{tabTitle}</h1>
          <p>{tabSub}</p>
        </div>

        {/* Stat cards */}
        <div className="stats-row">
          <div className="stat-card" style={{ borderTopColor: 'var(--accent-1)', borderTopWidth: 3 }}>
            <div className="sc-icon">🎬</div>
            <div className="sc-value" style={{ color: 'var(--accent-1)' }}>
              {loading ? '—' : movies.length}
            </div>
            <div className="sc-label">Total Movies</div>
          </div>
          <div className="stat-card" style={{ borderTopColor: 'var(--accent-2)', borderTopWidth: 3 }}>
            <div className="sc-icon">📺</div>
            <div className="sc-value" style={{ color: 'var(--accent-2)' }}>
              {loading ? '—' : series.length}
            </div>
            <div className="sc-label">Web Series</div>
          </div>
          <div className="stat-card" style={{ borderTopColor: '#ffaa00', borderTopWidth: 3 }}>
            <div className="sc-icon">👀</div>
            <div className="sc-value" style={{ color: '#ffaa00' }}>
              {loading ? '—' : watchlist.length}
            </div>
            <div className="sc-label">Watchlist</div>
          </div>
        </div>

        {/* Toolbar */}
        <div className="toolbar">
          <input
            id="search-input"
            className="search-input"
            placeholder="🔍  Search…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          <button id="add-btn" className="add-btn" onClick={() => setShowModal(true)}>
            ＋ Add {tab === 'movies' ? 'Movie' : tab === 'webseries' ? 'Series' : 'to Watchlist'}
          </button>
        </div>

        {/* Grid of Cards */}
        <div className="grid-container">
          {loading ? (
            <div className="empty-state">
              <div className="empty-icon">⏳</div>
              <span>Loading…</span>
            </div>
          ) : filtered.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">{tab === 'movies' ? '🎬' : tab === 'webseries' ? '📺' : '👀'}</div>
              <span>
                {search ? 'No results found.' : 'Nothing here yet. Click ＋ Add to get started!'}
              </span>
            </div>
          ) : (
            <div className="cards-grid">
              {filtered.map((item, i) => (
                <div className="card-item" key={item.id}>
                  <div className="card-header">
                    <span className="card-num">{String(i + 1).padStart(2, '0')}</span>
                    <button
                      className="card-delete"
                      onClick={() => handleDelete(item.id)}
                      title="Delete"
                    >✕</button>
                  </div>
                  
                  <div className="card-body">
                    <div className="card-icon">{tab === 'movies' ? '🎬' : tab === 'webseries' ? '📺' : '👀'}</div>
                    <h3 className="card-title">{item.name}</h3>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Add modal */}
      {showModal && (
        <AddModal
          tab={tab}
          onAdd={handleAdd}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  )
}
