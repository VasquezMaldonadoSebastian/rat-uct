import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';

const SEVERIDAD = { crítica: 'critical', alta: 'high', media: 'medium', baja: 'low' };

export default function BrechasList() {
  const [brechas, setBrechas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ titulo: '', descripcion: '', severidad: 'media', tipo_incidente: '', datos_afectados: '', medidas_correctivas: '' });

  const load = () => api.listarBrechas().then(setBrechas).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    await api.crearBrecha(form);
    setShowForm(false);
    setForm({ titulo: '', descripcion: '', severidad: 'media', tipo_incidente: '', datos_afectados: '', medidas_correctivas: '' });
    load();
  };

  return (
    <div>
      <div className="page-head">
        <Link to="/" className="back-link">← Dashboard</Link>
        <h2>🕊️ Registro de Brechas</h2>
        <button className="btn btn-pri" onClick={() => setShowForm(true)}>+ Nueva brecha</button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="form-section" style={{ marginBottom: '1.5rem' }}>
          <h3>Nueva brecha de seguridad</h3>
          <div className="form-grid">
            <div className="field full"><label>Título *</label><input value={form.titulo} onChange={e => setForm({...form, titulo: e.target.value})} required /></div>
            <div className="field full"><label>Descripción</label><textarea value={form.descripcion} onChange={e => setForm({...form, descripcion: e.target.value})} rows={2} /></div>
            <div className="field"><label>Severidad</label>
              <select value={form.severidad} onChange={e => setForm({...form, severidad: e.target.value})}>
                <option value="baja">Baja</option><option value="media">Media</option><option value="alta">Alta</option><option value="crítica">Crítica</option>
              </select>
            </div>
            <div className="field"><label>Tipo de incidente</label>
              <select value={form.tipo_incidente} onChange={e => setForm({...form, tipo_incidente: e.target.value})}>
                <option value="">Seleccionar...</option>
                <option value="fuga">Fuga de datos</option><option value="acceso">Acceso no autorizado</option>
                <option value="perdida">Pérdida de dispositivo</option><option value="phishing">Phishing</option>
                <option value="malware">Malware / Ransomware</option><option value="interno">Error interno</option>
              </select>
            </div>
            <div className="field"><label>Datos afectados</label><input value={form.datos_afectados} onChange={e => setForm({...form, datos_afectados: e.target.value})} /></div>
            <div className="field"><label>Medidas correctivas</label><input value={form.medidas_correctivas} onChange={e => setForm({...form, medidas_correctivas: e.target.value})} /></div>
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn-ghost" onClick={() => setShowForm(false)}>Cancelar</button>
            <button type="submit" className="btn btn-pri">Registrar brecha</button>
          </div>
        </form>
      )}

      {loading ? <div className="loading">Cargando...</div> : brechas.length === 0 ? (
        <div className="empty"><p>No hay brechas registradas.</p></div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {brechas.map(b => (
            <div key={b.id} className={`breach-card ${SEVERIDAD[b.severidad] || 'medium'}`}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.3rem' }}>
                    <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{b.titulo}</span>
                    <span className={`sev-tag ${b.severidad === 'crítica' ? 'sev-high' : b.severidad === 'alta' ? 'sev-high' : b.severidad === 'media' ? 'sev-med' : 'sev-low'}`}>
                      {b.severidad}
                    </span>
                    <span className={`badge ${b.estado === 'abierta' ? 'badge-rose' : 'badge-sage'}`}>
                      {b.estado}
                    </span>
                  </div>
                  {b.descripcion && <p style={{ fontSize: '0.78rem', color: 'var(--text2)', marginBottom: '0.3rem' }}>{b.descripcion}</p>}
                  <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.72rem', color: 'var(--text3)', flexWrap: 'wrap' }}>
                    {b.tipo_incidente && <span>📌 {b.tipo_incidente}</span>}
                    {b.datos_afectados && <span>📦 {b.datos_afectados}</span>}
                    {b.created_at && <span>🕐 {new Date(b.created_at).toLocaleDateString('es-CL')}</span>}
                    {b.notificado_apdp && <span style={{ color: 'var(--sage-dark)' }}>✅ Notificado APDP</span>}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
