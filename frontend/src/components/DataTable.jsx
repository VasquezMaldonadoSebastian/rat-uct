import { Loader2 } from 'lucide-react';

/**
 * DataTable — Tabla genérica reutilizable para listados CRUD.
 *
 * Props:
 *   columns  : Array<{ key: string, label: string, render?: (row) => ReactNode }>
 *   data     : Array<Object>
 *   onRowClick? : (row) => void
 *   loading?    : boolean
 */
export default function DataTable({ columns = [], data = [], onRowClick, loading }) {
  if (loading) {
    return (
      <div className="loading">
        <Loader2 size={20} style={{ animation: 'spin 1s linear infinite', verticalAlign: 'middle', marginRight: 8 }} />
        Cargando...
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="table-card">
        <div className="empty">
          <p>No hay datos</p>
        </div>
      </div>
    );
  }

  return (
    <div className="table-card">
      <table className="rat-table">
        <thead>
          <tr>
            {columns.map(col => (
              <th key={col.key}>{col.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr
              key={row.id ?? idx}
              onClick={() => onRowClick?.(row)}
              style={onRowClick ? { cursor: 'pointer' } : undefined}
            >
              {columns.map(col => (
                <td key={col.key}>
                  {col.render ? col.render(row) : row[col.key] ?? '—'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
