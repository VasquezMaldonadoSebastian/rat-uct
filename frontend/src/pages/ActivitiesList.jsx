import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';

export default function ActivitiesList() {
  const [actividades, setActividades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const load = () => {
    setLoading(true);
    const params = {};
    if (search) params.search = search;
    api.listarActividades(params).then(setActividades).finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, [search]);

  return (
    <div>
      <div className="page-head">
        <Link to="/" className="back-link">← Dashboard</Link>
        <h2>Actividades de Tratamiento</h2>
        <Link to="/actividades/nueva" className="btn btn-pri">+ Nueva actividad</Link>
      </div>

      <div style={{ marginBottom: '1rem', display: 'flex', gap: '0.5rem' }}>
        <input
          style={{ flex: 1, padding: '0.5rem 0.75rem', borderRadius: 8, border: '1px solid var(--border)', background: '#fff', fontSize: '0.85rem', outline: 'none' }}
          placeholder="Buscar actividades por nombre, área o base legal..."
          value={search} onChange={e => setSearch(e.target.value)}
        />
      </div>

      {loading ? <div className="loading">Cargando...</div> : (
        <div className="table-card">
          <div className="table-header">
            <h2>📋 Registro de Actividades</h2>
            <span style={{ fontSize: '0.75rem', color: 'var(--text3)' }}>{actividades.length} actividades</span>
          </div>
          <table className="rat-table">
            <thead>
              <tr>
                <th>Actividad</th>
                <th>Áreas</th>
                <th>Base legal</th>
                <th>Titulares</th>
                <th>Retención</th>
                <th>Estado</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {actividades.map(a => (
                <tr key={a.id}>
                  <td>
                    <Link to={`/actividades/${a.id}`} style={{ fontWeight: 600, color: 'var(--text)', textDecoration: 'none' }}>
                      {a.actividad_tratamiento}
                    </Link>
                  </td>
                  <td>{(a.areas_intervienen || []).join(', ')}</td>
                  <td>
                    <span className={`badge ${a.base_licitud?.includes('contrato') ? 'badge-pri' : a.base_licitud?.includes('Consent') ? 'badge-lav' : 'badge-sage'}`}>
                      {a.base_licitud}
                    </span>
                  </td>
                  <td>{(a.categoria_titulares || []).join(', ')}</td>
                  <td>{a.plazo_conservacion || '—'}</td>
                  <td>
                    <span className={`badge ${a.estado === 'activo' ? 'badge-sage' : 'badge-gold'}`}>
                      {a.estado}
                    </span>
                  </td>
                  <td><Link to={`/actividades/${a.id}`} className="btn btn-ghost btn-sm">Ver</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
