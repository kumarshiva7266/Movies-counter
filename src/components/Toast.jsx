// src/components/Toast.jsx
import { useEffect } from 'react'

export default function Toast({ toasts, removeToast }) {
  return (
    <div className="toast-container">
      {toasts.map(t => (
        <ToastItem key={t.id} toast={t} onRemove={() => removeToast(t.id)} />
      ))}
    </div>
  )
}

function ToastItem({ toast, onRemove }) {
  useEffect(() => {
    const timer = setTimeout(onRemove, 2500)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className={`toast ${toast.type}`}>
      {toast.message}
    </div>
  )
}
