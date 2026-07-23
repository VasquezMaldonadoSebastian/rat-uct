import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';

export default function AreasList() {
  const [areas, setAreas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listarAreas().then(setAreas).finally(() => setLoading(false));
  }, []);

  const grouped = areas.reduce((acc, a) => {
    (acc[a.tipo] = acc[a.tipo] || []).push(a);
    return acc;
  }, {});

  return (
    <div>
      <div className="page-head">
        <Link to="/" className="back-link">← Dashboard</Link>
        <h2>Áreas UCT</h2>
      </div>

      {loading ? <div className="loading">Cargando...</div> : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '1rem' }}>
          {Object.entries(grouped).map(([tipo, items]) => (
            <div key={tipo} className="card">
              <h3 style={{ textTransform: 'capitalize', color: 'var(--pri-dark)', fontSize: '0.82rem', fontWeight: 700, marginBottom: '0.75rem', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border2)' }}>
                {tipo}
              </h3>
              <ul style={{ listStyle: 'none' }}>
                {items.map(a => (
                  <li key={a.id} style={{ padding: '0.45rem 0', borderBottom: '1px solid var(--border2)', fontSize: '0.83rem' }}>
                    <strong style={{ color: 'var(--text)' }}>{a.nombre}</strong>
                    {a.descripcion && <div style={{ fontSize: '0.72rem', color: 'var(--text3)', marginTop: '0.15rem' }}>{a.descripcion}</div>}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
