import { Loader2 } from 'lucide-react';

/**
 * LoadingSpinner — Spinner de carga con texto opcional.
 *
 * Props:
 *   message?: string (default: "Cargando...")
 */
export default function LoadingSpinner({ message = 'Cargando...' }) {
  return (
    <div className="loading">
      <Loader2
        size={22}
        style={{
          animation: 'spin 1s linear infinite',
          verticalAlign: 'middle',
          marginRight: 8,
        }}
      />
      {message}
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
