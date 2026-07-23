import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';

export default function Reports() {
  const [resumen, setResumen] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.reporteResumen().then(setResumen).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Cargando reportes...</div>;

  const charts = [
    { title: 'Por Base Legal', data: resumen?.por_base_legal, color: 'var(--pri)' },
    { title: 'Por Área', data: resumen?.por_area, color: 'var(--sage)' },
    { title: 'Por Titular', data: resumen?.por_titular, color: 'var(--gold)' },
  ];

  return (
    <div>
      <div className="page-head">
        <Link to="/" className="back-link">← Dashboard</Link>
        <h2>Reportes</h2>
        <span className="badge badge-pri">
          {resumen?.total_actividades} actividades
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
        {charts.map(({ title, data, color }) => (
          <div key={title} className="chart-card">
            <div className="chart-title">{title}</div>
            {data && Object.keys(data).length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {Object.entries(data).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([key, val]) => {
                  const max = Math.max(...Object.values(data));
                  return (
                    <div key={key} className="bar-row" style={{ marginBottom: 0 }}>
                      <span className="bar-label">{key}</span>
                      <div className="bar-track">
                        <div className="bar-fill" style={{ width: `${(val / max) * 100}%`, background: color }} />
                      </div>
                      <span className="bar-value">{val}</span>
                    </div>
                  );
                })}
              </div>
            ) : <p style={{ color: 'var(--text3)', fontSize: '0.85rem' }}>Sin datos</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
