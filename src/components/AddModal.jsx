// src/components/AddModal.jsx
import { useState, useEffect, useRef } from 'react'

export default function AddModal({ tab, onAdd, onClose }) {
  const [name, setName]   = useState('')
  const [error, setError] = useState('')
  const inputRef = useRef(null)

  useEffect(() => { inputRef.current?.focus() }, [])

  const label = tab === 'movies' ? 'Movie Name' : tab === 'webseries' ? 'Web Series Name' : 'Watchlist Item Name'

  function handleSubmit(e) {
    e.preventDefault()
    if (!name.trim()) { setError('Name cannot be empty.'); return }
    onAdd(name.trim())
    onClose()
  }

  function handleOverlayClick(e) {
    if (e.target === e.currentTarget) onClose()
  }

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-card">
        <h2>➕ New {label}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>{label}</label>
            <input
              ref={inputRef}
              type="text"
              placeholder="Enter name…"
              value={name}
              onChange={e => { setName(e.target.value); setError('') }}
            />
          </div>
          <div className="modal-error">{error}</div>
          <div className="modal-actions">
            <button type="button" className="modal-cancel" onClick={onClose}>Cancel</button>
            <button type="submit" className="modal-submit">Add ✓</button>
          </div>
        </form>
      </div>
    </div>
  )
}
