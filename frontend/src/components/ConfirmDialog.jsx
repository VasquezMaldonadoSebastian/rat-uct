import { X, AlertCircle } from 'lucide-react';

/**
 * ConfirmDialog — Modal de confirmación.
 *
 * Props:
 *   open      : boolean
 *   title     : string
 *   message   : string
 *   onConfirm : () => void
 *   onCancel  : () => void
 *   confirmText? : string (default: "Confirmar")
 *   cancelText?  : string (default: "Cancelar")
 *   variant?     : "default" | "danger" (default: "default")
 */
export default function ConfirmDialog({
  open,
  title = 'Confirmar acción',
  message = '¿Estás seguro?',
  onConfirm,
  onCancel,
  confirmText = 'Confirmar',
  cancelText = 'Cancelar',
  variant = 'default',
}) {
  if (!open) return null;

  return (
    <div
      style={{
        position: 'fixed', inset: 0, zIndex: 1000,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: 'rgba(0,0,0,0.35)',
      }}
      onClick={onCancel}
    >
      <div
        className="card"
        style={{
          width: 400, maxWidth: '90vw', padding: '1.5rem',
          boxShadow: 'var(--sh-lg)',
        }}
        onClick={e => e.stopPropagation()}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {variant === 'danger' && <AlertCircle size={20} style={{ color: 'var(--rose)' }} />}
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text)' }}>{title}</h3>
          </div>
          <button
            onClick={onCancel}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text3)', padding: 2 }}
          >
            <X size={18} />
          </button>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text2)', marginBottom: '1.25rem', lineHeight: 1.5 }}>
          {message}
        </p>
        <div className="form-actions" style={{ marginTop: 0 }}>
          <button className="btn btn-ghost" onClick={onCancel}>{cancelText}</button>
          <button
            className={variant === 'danger' ? 'btn btn-danger' : 'btn btn-pri'}
            onClick={onConfirm}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
