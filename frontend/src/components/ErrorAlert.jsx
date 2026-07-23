import { AlertTriangle, RefreshCw } from 'lucide-react';

/**
 * ErrorAlert — Alerta de error con botón de reintento opcional.
 *
 * Props:
 *   message : string — mensaje de error
 *   onRetry?: () => void — callback para reintentar
 */
export default function ErrorAlert({ message, onRetry }) {
  return (
    <div className="error" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <AlertTriangle size={18} />
        <span>{message}</span>
      </div>
      {onRetry && (
        <button className="btn btn-ghost btn-sm" onClick={onRetry} style={{ flexShrink: 0 }}>
          <RefreshCw size={14} /> Reintentar
        </button>
      )}
    </div>
  );
}
