import { Search } from 'lucide-react';

/**
 * SearchFilter — Barra de búsqueda con filtros desplegables opcionales.
 *
 * Props:
 *   onSearch   : (text: string) => void
 *   placeholder? : string (default: "Buscar...")
 *   filters?   : Array<{ key: string, label: string, options: Array<{ value: string, label: string }> }>
 *   onFilter?  : (key: string, value: string) => void
 *   filterValues? : Record<string, string> — valores actuales de los filtros
 */
export default function SearchFilter({
  onSearch,
  placeholder = 'Buscar...',
  filters,
  onFilter,
  filterValues = {},
}) {
  return (
    <div style={{ marginBottom: '1rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
      <div style={{ flex: 1, position: 'relative', minWidth: 200 }}>
        <Search
          size={16}
          style={{
            position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)',
            color: 'var(--text3)', pointerEvents: 'none',
          }}
        />
        <input
          style={{
            width: '100%', padding: '0.5rem 0.75rem 0.5rem 2rem',
            borderRadius: 8, border: '1px solid var(--border)',
            background: '#fff', fontSize: '0.85rem', outline: 'none',
          }}
          placeholder={placeholder}
          onChange={e => onSearch(e.target.value)}
        />
      </div>
      {filters?.map(f => (
        <select
          key={f.key}
          value={filterValues[f.key] ?? ''}
          onChange={e => onFilter?.(f.key, e.target.value)}
          style={{
            padding: '0.5rem 0.75rem', borderRadius: 8,
            border: '1px solid var(--border)', background: '#fff',
            fontSize: '0.82rem', outline: 'none', color: 'var(--text)', minWidth: 130,
          }}
        >
          <option value="">{f.label}</option>
          {f.options.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      ))}
    </div>
  );
}
