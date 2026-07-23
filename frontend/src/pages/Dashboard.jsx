import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import CumplimientoPanel from './CumplimientoPanel';

const DAYS_LEFT = 140;

/* ── Fases progress bar ── */
function FasesProgress() {
  const [fases, setFases] = useState(null);
  useEffect(() => { api.fases().then(setFases); }, []);
  if (!fases) return null;
  return (
    <div className="fases-progress">
      <div className="fases-inner">
        <span style={{ fontSize: '0.78rem', fontWeight: 700, whiteSpace: 'nowrap' }}>
          📊 {fases.completadas}/12 fases
        </span>
        <div className="fases-track">
          <div className="fases-fill" style={{ width: `${fases.progreso}%` }} />
        </div>
        <span style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--pri-dark)', whiteSpace: 'nowrap' }}>
          {fases.progreso}%
        </span>
        <div style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap' }}>
          {fases.fases.map(f => (
            <span key={f.id} title={f.nombre} className="fase-dot"
              style={{
                background: f.completado ? 'var(--sage)' : 'var(--border2)',
                color: f.completado ? '#fff' : 'var(--text4)',
              }}
            >{f.id}</span>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ── Score gauge ── */
const NIVELES = ['crítico', 'alto', 'medio', 'bajo'];
const COLOR_NIVEL = { crítico: 'var(--rose-dark)', alto: 'var(--gold-dark)', medio: 'var(--pri-dark)', bajo: 'var(--sage-dark)' };
const COLOR_NIVEL_BG = { crítico: 'var(--rose-bg)', alto: 'var(--gold-bg)', medio: 'var(--pri-bg)', bajo: 'var(--sage-bg)' };

function ScoreGauge({ score }) {
  const r = 55, cx = 75, cy = 75, circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  const color = score < 40 ? 'var(--rose)' : score < 70 ? 'var(--gold)' : 'var(--sage)';
  return (
    <svg width="150" height="150" viewBox="0 0 150 150">
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="var(--border2)" strokeWidth="8" />
      <circle cx={cx} cy={cy} r={r} fill="none" stroke={color} strokeWidth="8"
        strokeDasharray={circ} strokeDashoffset={offset}
        transform={`rotate(-90 ${cx} ${cy})`} strokeLinecap="round"
        style={{ transition: 'stroke-dashoffset 1s ease' }} />
      <text x={cx} y={cy - 6} textAnchor="middle" fontSize="28" fontWeight="800" fill="var(--text)">{score}</text>
      <text x={cx} y={cy + 16} textAnchor="middle" fontSize="11" fill="var(--text3)">{score < 40 ? 'En riesgo' : score < 70 ? 'En progreso' : 'Aceptable'}</text>
    </svg>
  );
}

/* ── Heatmap ── */
function Heatmap({ heatmap, porNivel }) {
  const areas = Object.keys(heatmap || {});
  if (areas.length === 0) return <p style={{ color: 'var(--text3)', fontSize: '0.85rem' }}>Evalúa actividades para ver la matriz</p>;
  return (
    <div>
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
        {NIVELES.map(n => (
          <span key={n} className={`badge ${n === 'crítico' ? 'badge-rose' : n === 'alto' ? 'badge-gold' : n === 'medio' ? 'badge-pri' : 'badge-sage'}`}>
            {n}: {porNivel?.[n] || 0}
          </span>
        ))}
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'collapse', fontSize: '0.78rem', width: '100%' }}>
          <thead>
            <tr>
              <th style={{ padding: '0.3rem 0.5rem', textAlign: 'left', color: 'var(--text3)', fontWeight: 600 }}>Área</th>
              {NIVELES.map(n => (
                <th key={n} style={{ padding: '0.3rem 0.5rem', textAlign: 'center', fontWeight: 600 }}>{n}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {areas.map(area => {
              const celda = heatmap[area] || {};
              const maxVal = Math.max(...NIVELES.map(n => celda[n] || 0), 1);
              return (
                <tr key={area}>
                  <td style={{ padding: '0.3rem 0.5rem', fontWeight: 500, whiteSpace: 'nowrap' }}>{area}</td>
                  {NIVELES.map(n => {
                    const val = celda[n] || 0;
                    const intensity = val / maxVal;
                    const colors = { crítico: '#D4958A', alto: '#D4B56C', medio: '#6B9EC2', bajo: '#8DAF94' };
                    return (
                      <td key={n} style={{
                        padding: '0.3rem', textAlign: 'center', fontWeight: 600,
                        background: val > 0 ? `${colors[n]}${Math.round(35 + intensity * 40).toString(16).padStart(2, '0')}` : undefined,
                        color: val > 0 ? '#fff' : 'var(--text4)', minWidth: 40,
                      }}>{val || ''}</td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ── Score bars per area ── */
function ScoreBars({ porArea }) {
  if (!porArea || porArea.length === 0) return <p style={{ color: 'var(--text3)', fontSize: '0.85rem' }}>Sin datos</p>;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      {porArea.map(({ area, score, actividades }) => (
        <div key={area} className="bar-row" style={{ marginBottom: 0 }}>
          <span className="bar-label">{area}</span>
          <div className="bar-track">
            <div className="bar-fill" style={{
              width: `${(score / 100) * 100}%`,
              background: score < 40 ? 'var(--rose)' : score < 70 ? 'var(--gold)' : 'var(--sage)',
            }} />
          </div>
          <span className="bar-value">{score}%</span>
          <span style={{ fontSize: '0.7rem', color: 'var(--text3)', minWidth: '1.5rem' }}>({actividades})</span>
        </div>
      ))}
    </div>
  );
}

/* ══════════════════════════════════════════════
   DASHBOARD MAIN
   ══════════════════════════════════════════════ */
export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [score, setScore] = useState(null);
  const [matriz, setMatriz] = useState(null);
  const [actividades, setActividades] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.totalActividades(),
      api.reporteScore(),
      api.matrizRiesgo(),
      api.listarActividades({ limit: 50 }),
    ]).then(([s, sc, m, acts]) => {
      setStats(s);
      setScore(sc);
      setMatriz(m);
      setActividades(acts);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Cargando dashboard...</div>;

  const totalActs = stats?.total || 0;
  const brechasCount = stats?.por_estado?.revisión || 0;
  const scoreGlobal = score?.score_global ?? 0;

  return (
    <div>
      {/* ═══ PAGE HEAD ═══ */}
      <div className="page-head">
        <h2>Dashboard · Cumplimiento Ley 21.719</h2>
        <Link to="/actividades/nueva" className="btn btn-pri">+ Nueva actividad</Link>
      </div>

      {/* ═══ FASES ═══ */}
      <FasesProgress />

      {/* ═══ KPI CARDS ═══ */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-icon">🎯</div>
          <div className="kpi-label">Nivel de Cumplimiento</div>
          <div className="kpi-value" style={{ color: scoreGlobal < 40 ? 'var(--rose-dark)' : scoreGlobal < 70 ? 'var(--gold-dark)' : 'var(--sage-dark)' }}>
            {scoreGlobal}%
          </div>
          <div className="kpi-sub">
            {scoreGlobal < 40 ? 'En riesgo' : scoreGlobal < 70 ? 'En progreso' : 'Aceptable'}
          </div>
          <div className="kpi-bar">
            <div className="kpi-bar-fill" style={{
              width: `${scoreGlobal}%`,
              background: scoreGlobal < 40 ? 'var(--rose)' : scoreGlobal < 70 ? 'var(--gold)' : 'var(--sage)'
            }} />
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon">📋</div>
          <div className="kpi-label">Actividades RAT</div>
          <div className="kpi-value" style={{ color: 'var(--pri-dark)' }}>{totalActs}</div>
          <div className="kpi-sub">
            {brechasCount > 0 ? `${brechasCount} requieren revisión` : 'Sin novedades'}
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon">🔍</div>
          <div className="kpi-label">Evaluadas</div>
          <div className="kpi-value" style={{ color: 'var(--sage-dark)' }}>{score?.total_evaluadas ?? 0}</div>
          <div className="kpi-sub">de {totalActs} actividades totales</div>
          <div className="kpi-bar">
            <div className="kpi-bar-fill" style={{
              width: totalActs > 0 ? `${((score?.total_evaluadas ?? 0) / totalActs) * 100}%` : '0%',
              background: 'var(--sage)'
            }} />
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon">⚠️</div>
          <div className="kpi-label">Señales Activas</div>
          <div className="kpi-value" style={{ color: 'var(--gold-dark)' }}>
            {(stats?.datos_sensibles ? 1 : 0) + (stats?.transferencias_internacionales ? 1 : 0)}
          </div>
          <div className="kpi-sub">
            {[stats?.datos_sensibles ? 'sensibles' : null, stats?.transferencias_internacionales ? 'internac.' : null].filter(Boolean).join(' · ') || 'ninguna'}
          </div>
        </div>
      </div>

      {/* ═══ SEÑALES ═══ */}
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1.25rem' }}>
        {stats?.datos_sensibles > 0 && <span className="signal sens">🔴 Datos sensibles</span>}
        {stats?.transferencias_internacionales > 0 && <span className="signal trans">🌐 Transferencias internacionales</span>}
        <span className="signal scale">📊 Indicio gran escala</span>
        <span className="signal eipd">📋 Requiere EIPD</span>
        <span className="signal nna">🧒 Involucra NNA</span>
      </div>

      {/* ═══ MATRIZ + GAUGE ═══ */}
      <div className="dash-grid-2">
        <div className="table-card">
          <div className="table-header">
            <h2>🔥 Matriz de Riesgo</h2>
            <button className="btn btn-ghost btn-sm" onClick={() => api.evaluarRiesgoTodas().then(r => window.location.reload())}>
              Evaluar todo
            </button>
          </div>
          <div style={{ padding: '1rem 1.25rem' }}>
            <Heatmap heatmap={matriz?.heatmap} porNivel={matriz?.por_nivel} />
          </div>
        </div>

        <div className="card gauge-box">
          <ScoreGauge score={scoreGlobal} />
          <div style={{ marginTop: '0.25rem', textAlign: 'center' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text3)' }}>Score global</span>
          </div>
        </div>
      </div>

      {/* ═══ SCORE POR ÁREA ═══ */}
      <div className="table-card mb-2">
        <div className="table-header">
          <h2>📊 Cumplimiento por Área</h2>
        </div>
        <div style={{ padding: '1rem 1.25rem' }}>
          <ScoreBars porArea={score?.por_area} />
        </div>
      </div>

      {/* ═══ BRECHAS + TABLA RAT ═══ */}
      <div className="dash-grid-main" style={{ gridTemplateColumns: '280px 1fr' }}>
        {/* Sidebar interno: brechas */}
        <div>
          <div className="card" style={{ marginBottom: '1rem' }}>
            <div className="section-title">🔍 Brechas detectadas</div>
            {[
              { icon: '📋', name: 'Sin política de privacidad', desc: 'No se declaró una política publicada.', sev: 'high', sevLabel: 'ALTA' },
              { icon: '🕊️', name: 'Sin registro de brechas', desc: 'No existe registro de vulneraciones.', sev: 'med', sevLabel: 'MEDIA' },
              { icon: '🔐', name: 'Se recomienda EIPD', desc: 'Datos sensibles o gran escala.', sev: 'med', sevLabel: 'MEDIA' },
              { icon: '👤', name: 'Sin DPO designado', desc: 'Evaluar DPO interno o externo.', sev: 'med', sevLabel: 'MEDIA' },
            ].map(b => (
              <div key={b.name} className="breach-item">
                <div className="breach-icon">{b.icon}</div>
                <div className="breach-info">
                  <div className="name">{b.name}</div>
                  <div className="desc">{b.desc}</div>
                </div>
                <span className={`sev-tag sev-${b.sev}`}>{b.sevLabel}</span>
              </div>
            ))}
          </div>

          <div className="card">
            <div className="section-title">⚙ Gestión</div>
            <Link to="/brechas" className="sidebar-item" style={{ marginBottom: '2px' }}>
              <span className="s-icon">🕊️</span> Brechas
            </Link>
            <Link to="/arsop" className="sidebar-item" style={{ marginBottom: '2px' }}>
              <span className="s-icon">👤</span> ARSOP
            </Link>
            <Link to="/actividades/1/eipd" className="sidebar-item">
              <span className="s-icon">🔍</span> EIPD
            </Link>
          </div>
        </div>

        {/* Tabla RAT */}
        <div className="table-card">
          <div className="table-header">
            <h2>📋 Registro de Actividades de Tratamiento</h2>
            <Link to="/actividades/nueva" className="btn btn-pri btn-sm">+ Nueva</Link>
          </div>
          {actividades.length === 0 ? (
            <div className="empty"><p>No hay actividades registradas.</p></div>
          ) : (
            <table className="rat-table">
              <thead>
                <tr>
                  <th>Actividad</th>
                  <th>Unidad</th>
                  <th>Riesgo</th>
                  <th>Score</th>
                  <th>Base legal</th>
                  <th>Retención</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {actividades.map(a => (
                  <tr key={a.id}>
                    <td>
                      <span style={{ fontWeight: 600, display: 'block', fontSize: '0.81rem' }}>{a.actividad_tratamiento}</span>
                      <span style={{ fontSize: '0.68rem', color: 'var(--text3)', marginTop: '0.1rem', display: 'block' }}>
                        {(a.finalidad || '').slice(0, 55)}
                      </span>
                    </td>
                    <td>{(a.areas_intervienen || []).slice(0, 2).join(', ')}{(a.areas_intervienen || []).length > 2 ? '…' : ''}</td>
                    <td>
                      {a.nivel_riesgo ? (
                        <span className={`badge ${a.nivel_riesgo === 'crítico' ? 'badge-rose' : a.nivel_riesgo === 'alto' ? 'badge-gold' : a.nivel_riesgo === 'medio' ? 'badge-pri' : 'badge-sage'}`}>
                          {a.nivel_riesgo}
                        </span>
                      ) : (
                        <span style={{ fontSize: '0.72rem', color: 'var(--text3)' }}>—</span>
                      )}
                    </td>
                    <td style={{ fontWeight: 700, color: (a.score_actividad || 0) < 40 ? 'var(--rose-dark)' : (a.score_actividad || 0) < 70 ? 'var(--gold-dark)' : 'var(--sage-dark)' }}>
                      {a.score_actividad != null ? `${a.score_actividad}%` : '—'}
                    </td>
                    <td>
                      <span className={`badge ${a.base_licitud?.includes('contrato') ? 'badge-pri' : a.base_licitud?.includes('Consent') ? 'badge-lav' : 'badge-sage'}`}>
                        {a.base_licitud}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.78rem' }}>{a.plazo_conservacion || '—'}</td>
                    <td>
                      <Link to={`/actividades/${a.id}`} className="btn btn-ghost btn-sm">Ver</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* ═══ MÉTRICAS DE CUMPLIMIENTO ═══ */}
      <CumplimientoPanel />
    </div>
  );
}
