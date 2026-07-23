import { useState, useEffect } from 'react';
import { apiV1 } from '../api';

/* ── Color helpers ── */
const RIESGO_COLORS = {
  crítico: { badge: 'badge-rose', bg: 'var(--rose-bg)', text: 'var(--rose-dark)' },
  alto: { badge: 'badge-gold', bg: 'var(--gold-bg)', text: 'var(--gold-dark)' },
  medio: { badge: 'badge-pri', bg: 'var(--pri-bg)', text: 'var(--pri-dark)' },
  bajo: { badge: 'badge-sage', bg: 'var(--sage-bg)', text: 'var(--sage-dark)' },
};

const ARSOP_LABELS = {
  recibida: 'Recibida',
  en_estudio: 'En estudio',
  respondida: 'Respondida',
};

const RIESGO_LABELS = {
  crítico: 'Crítico',
  alto: 'Alto',
  medio: 'Medio',
  bajo: 'Bajo',
};

/* ── KPI card (inline, matching Dashboard style) ── */
function KpiCard({ icon, label, value, sub, color }) {
  return (
    <div className="kpi-card">
      <div className="kpi-icon">{icon}</div>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value" style={{ color: color || 'var(--pri-dark)' }}>{value}</div>
      {sub && <div className="kpi-sub">{sub}</div>}
    </div>
  );
}

/* ── ARSOP Status Table ── */
function ArsopTable({ data }) {
  const estados = ['recibida', 'en_estudio', 'respondida'];
  const total = Object.values(data || {}).reduce((s, v) => s + (v || 0), 0);
  if (total === 0) return <p className="empty-hint">Sin solicitudes ARSOP</p>;
  return (
    <table className="mini-table">
      <thead>
        <tr>
          <th>Estado</th>
          <th style={{ textAlign: 'center' }}>Cant.</th>
          <th style={{ textAlign: 'center' }}>%</th>
        </tr>
      </thead>
      <tbody>
        {estados.map(est => {
          const val = data[est] || 0;
          return (
            <tr key={est}>
              <td>
                <span className={`badge ${est === 'recibida' ? 'badge-gold' : est === 'en_estudio' ? 'badge-pri' : 'badge-sage'}`}>
                  {ARSOP_LABELS[est] || est}
                </span>
              </td>
              <td style={{ textAlign: 'center', fontWeight: 700 }}>{val}</td>
              <td style={{ textAlign: 'center', color: 'var(--text3)' }}>
                {Math.round((val / total) * 100)}%
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

/* ── Riesgo Distribution ── */
function RiesgoBadges({ data }) {
  const niveles = ['crítico', 'alto', 'medio', 'bajo'];
  const total = Object.values(data || {}).reduce((s, v) => s + (v || 0), 0);
  if (total === 0) return <p className="empty-hint">Sin actividades evaluadas</p>;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      {niveles.map(n => {
        const val = data[n] || 0;
        const c = RIESGO_COLORS[n] || {};
        const pct = total > 0 ? (val / total) * 100 : 0;
        return (
          <div key={n} className="bar-row" style={{ marginBottom: 0 }}>
            <span className={`bar-label`} style={{ textTransform: 'capitalize' }}>{RIESGO_LABELS[n] || n}</span>
            <div className="bar-track">
              <div className="bar-fill" style={{
                width: `${pct}%`,
                background: c.text || 'var(--pri)',
              }} />
            </div>
            <span className="bar-value" style={{ color: c.text }}>{val}</span>
          </div>
        );
      })}
    </div>
  );
}

/* ── Brechas Timeline ── */
function BrechasTimeline({ data }) {
  if (!data || data.length === 0) return <p className="empty-hint">Sin brechas en los últimos 6 meses</p>;
  const maxCount = Math.max(...data.map(d => d.count), 1);
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: '0.5rem', height: 80, padding: '0.5rem 0' }}>
      {data.map(item => {
        const height = (item.count / maxCount) * 100;
        return (
          <div key={item.mes} style={{
            flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.2rem',
          }}>
            <span style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--text3)' }}>{item.count}</span>
            <div style={{
              width: '100%', height: `${Math.max(height, 8)}%`,
              background: item.count > 0 ? 'var(--rose)' : 'var(--border2)',
              borderRadius: '3px 3px 0 0',
              transition: 'height 0.3s ease',
              minHeight: 8,
            }} />
            <span style={{ fontSize: '0.58rem', color: 'var(--text4)', whiteSpace: 'nowrap' }}>
              {item.mes?.slice(-2)}/{item.mes?.slice(0, 4)}
            </span>
          </div>
        );
      })}
    </div>
  );
}

/* ══════════════════════════════════════════════
   CUMPLIMIENTO PANEL MAIN
   ══════════════════════════════════════════════ */
export default function CumplimientoPanel() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiV1.reporteCumplimiento()
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Cargando métricas de cumplimiento...</div>;
  if (!data) return null;

  const {
    brechas_por_mes = [],
    eipd_pendientes = 0,
    eipd_completadas = 0,
    arsop_por_estado = {},
    actividades_por_riesgo = {},
    score_promedio = 0,
  } = data;

  const totalEipd = eipd_pendientes + eipd_completadas;

  return (
    <div className="table-card" style={{ marginTop: '1.5rem' }}>
      <div className="table-header">
        <h2>📊 Métricas de Cumplimiento</h2>
      </div>
      <div style={{ padding: '1rem 1.25rem' }}>
        {/* KPI Cards */}
        <div className="kpi-grid">
          <KpiCard
            icon="🔍"
            label="EIPD Pendientes"
            value={eipd_pendientes}
            color="var(--gold-dark)"
            sub={totalEipd > 0 ? `${Math.round((eipd_pendientes / totalEipd) * 100)}% del total` : 'Sin registros'}
          />
          <KpiCard
            icon="✅"
            label="EIPD Completadas"
            value={eipd_completadas}
            color="var(--sage-dark)"
            sub={totalEipd > 0 ? `${Math.round((eipd_completadas / totalEipd) * 100)}% del total` : 'Sin registros'}
          />
          <KpiCard
            icon="⭐"
            label="Score Promedio"
            value={`${score_promedio}%`}
            color={score_promedio < 40 ? 'var(--rose-dark)' : score_promedio < 70 ? 'var(--gold-dark)' : 'var(--sage-dark)'}
            sub={score_promedio < 40 ? 'En riesgo' : score_promedio < 70 ? 'En progreso' : 'Aceptable'}
          />
        </div>

        {/* Two-column: ARSOP + Riesgo */}
        <div className="dash-grid-2" style={{ marginTop: '1.25rem' }}>
          <div className="card" style={{ padding: '0.75rem 1rem' }}>
            <div className="section-title" style={{ marginBottom: '0.75rem' }}>👤 ARSOP por Estado</div>
            <ArsopTable data={arsop_por_estado} />
          </div>
          <div className="card" style={{ padding: '0.75rem 1rem' }}>
            <div className="section-title" style={{ marginBottom: '0.75rem' }}>🔥 Actividades por Riesgo</div>
            <RiesgoBadges data={actividades_por_riesgo} />
          </div>
        </div>

        {/* Brechas timeline */}
        <div className="card" style={{ padding: '0.75rem 1rem', marginTop: '1rem' }}>
          <div className="section-title" style={{ marginBottom: '0.75rem' }}>🕊️ Brechas — últimos 6 meses</div>
          <BrechasTimeline data={brechas_por_mes} />
        </div>
      </div>
    </div>
  );
}
