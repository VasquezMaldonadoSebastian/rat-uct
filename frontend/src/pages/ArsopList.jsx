import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';

const TIPOS_DERECHO = ['Acceso', 'Rectificación', 'Cancelación', 'Oposición', 'Portabilidad', 'Bloqueo'];
const ESTADOS = ['recibida', 'en_estudio', 'respondida', 'rechazada'];

export default function ArsopList() {
  const [solicitudes, setSolicitudes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ tipo_derecho: '', solicitante_nombre: '', solicitante_email: '', solicitante_rut: '', descripcion: '' });
  const [respondiendo, setRespondiendo] = useState(null);
  const [respuestaText, setRespuestaText] = useState('');

  const load = () => api.listarArsop().then(setSolicitudes).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    await api.crearArsop(form);
    setShowForm(false);
    setForm({ tipo_derecho: '', solicitante_nombre: '', solicitante_email: '', solicitante_rut: '', descripcion: '' });
    load();
  };

  const handleResponder = async (id) => {
    await api.responderArsop(id, { estado: 'respondida', respuesta: respuestaText, fecha_respuesta: new Date().toISOString().split('T')[0] });
    setRespondiendo(null);
    setRespuestaText('');
    load();
  };

  return (
    <div>
      <div className="page-head">
        <Link to="/" className="back-link">← Dashboard</Link>
        <h2>👤 Portal ARSOP</h2>
        <button className="btn btn-pri" onClick={() => setShowForm(true)}>+ Nueva solicitud</button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="form-section" style={{ marginBottom: '1.5rem' }}>
          <h3>Nueva solicitud ARSOP</h3>
          <div className="form-grid">
            <div className="field"><label>Tipo de derecho *</label>
              <select value={form.tipo_derecho} onChange={e => setForm({...form, tipo_derecho: e.target.value})} required>
                <option value="">Seleccionar...</option>
                {TIPOS_DERECHO.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="field"><label>RUT</label><input value={form.solicitante_rut} onChange={e => setForm({...form, solicitante_rut: e.target.value})} /></div>
            <div className="field"><label>Nombre</label><input value={form.solicitante_nombre} onChange={e => setForm({...form, solicitante_nombre: e.target.value})} /></div>
            <div className="field"><label>Email</label><input type="email" value={form.solicitante_email} onChange={e => setForm({...form, solicitante_email: e.target.value})} /></div>
            <div className="field full"><label>Descripción</label><textarea value={form.descripcion} onChange={e => setForm({...form, descripcion: e.target.value})} rows={2} /></div>
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn-ghost" onClick={() => setShowForm(false)}>Cancelar</button>
            <button type="submit" className="btn btn-pri">Ingresar solicitud</button>
          </div>
        </form>
      )}

      {loading ? <div className="loading">Cargando...</div> : solicitudes.length === 0 ? (
        <div className="empty"><p>No hay solicitudes ARSOP.</p></div>
      ) : (
        <div className="table-card">
          <div className="table-header">
            <h2>📋 Solicitudes de Derechos</h2>
          </div>
          <table className="rat-table">
            <thead>
              <tr>
                <th>Derecho</th><th>Solicitante</th><th>Fecha</th><th>Estado</th><th>Respuesta</th><th></th>
              </tr>
            </thead>
            <tbody>
              {solicitudes.map(s => (
                <tr key={s.id}>
                  <td><span className="badge badge-pri">{s.tipo_derecho}</span></td>
                  <td>
                    <div style={{ fontWeight: 500, fontSize: '0.82rem' }}>{s.solicitante_nombre || '—'}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text3)' }}>{s.solicitante_email || s.solicitante_rut}</div>
                  </td>
                  <td style={{ fontSize: '0.78rem' }}>{s.fecha_solicitud ? new Date(s.fecha_solicitud).toLocaleDateString('es-CL') : '—'}</td>
                  <td>
                    <span className={`badge ${s.estado === 'respondida' ? 'badge-sage' : s.estado === 'rechazada' ? 'badge-rose' : 'badge-gold'}`}>
                      {s.estado}
                    </span>
                  </td>
                  <td style={{ fontSize: '0.78rem', color: 'var(--text2)', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {s.respuesta || '—'}
                  </td>
                  <td>
                    {s.estado !== 'respondida' && s.estado !== 'rechazada' ? (
                      <button className="btn btn-ghost btn-sm" onClick={() => setRespondiendo(s.id)}>Responder</button>
                    ) : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {respondiendo && (
            <div style={{ margin: '1rem', padding: '1rem', background: 'var(--bg)', borderRadius: 8, border: '1px solid var(--border)' }}>
              <h4 style={{ fontSize: '0.85rem', marginBottom: '0.5rem', color: 'var(--text)' }}>Responder solicitud</h4>
              <textarea rows={2} style={{ width: '100%', padding: '0.5rem', borderRadius: 6, border: '1px solid var(--border)', fontSize: '0.82rem', fontFamily: 'var(--font)' }}
                value={respuestaText} onChange={e => setRespuestaText(e.target.value)} placeholder="Escribe la respuesta..." />
              <div style={{ marginTop: '0.5rem', display: 'flex', gap: '0.5rem' }}>
                <button className="btn btn-pri btn-sm" onClick={() => handleResponder(respondiendo)} disabled={!respuestaText}>Enviar respuesta</button>
                <button className="btn btn-ghost btn-sm" onClick={() => setRespondiendo(null)}>Cancelar</button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
