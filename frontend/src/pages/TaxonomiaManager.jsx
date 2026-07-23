import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';

const TABS = [
  { key: 'categorias', label: '📂 Categorías de Datos' },
  { key: 'finalidades', label: '🎯 Finalidades' },
  { key: 'bases', label: '⚖️ Bases de Licitud' },
  { key: 'asignaciones', label: '🔗 Asignaciones' },
];

const TIPOS_DATO = ['personal', 'sensible', 'biométrico', 'financiero'];

export default function TaxonomiaManager() {
  const [tab, setTab] = useState('categorias');

  return (
    <div>
      <div className="page-head">
        <Link to="/" className="back-link">← Dashboard</Link>
        <h2>📋 Taxonomía de Datos (Fides)</h2>
      </div>

      <div style={{ display: 'flex', gap: '0.25rem', marginBottom: '1.25rem', borderBottom: '1px solid var(--border)' }}>
        {TABS.map(t => (
          <button
            key={t.key}
            className={`btn ${tab === t.key ? 'btn-pri' : 'btn-ghost'}`}
            style={{ borderRadius: 0, borderBottom: tab === t.key ? '2px solid var(--pri)' : '2px solid transparent', marginBottom: '-1px' }}
            onClick={() => setTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'categorias' && <CategoriasTab />}
      {tab === 'finalidades' && <FinalidadesTab />}
      {tab === 'bases' && <BasesTab />}
      {tab === 'asignaciones' && <AsignacionesTab />}
    </div>
  );
}

/* ─── Categorías de Datos ──────────────────────────────────────────── */

function CategoriasTab() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ nombre: '', descripcion: '', tipo_dato: 'personal' });

  const load = () => api.listarCategoriasDatos().then(setItems).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    await api.crearCategoriaDato(form);
    setShowForm(false);
    setForm({ nombre: '', descripcion: '', tipo_dato: 'personal' });
    load();
  };

  return (
    <div>
      <div className="page-head" style={{ marginBottom: '0.75rem' }}>
        <span style={{ fontSize: '0.78rem', color: 'var(--text3)' }}>
          Catálogo de categorías de datos personales ({items.length} registros)
        </span>
        <button className="btn btn-pri btn-sm" onClick={() => setShowForm(true)}>+ Nueva categoría</button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="form-section" style={{ marginBottom: '1rem' }}>
          <h3>Nueva categoría de dato</h3>
          <div className="form-grid">
            <div className="field"><label>Nombre *</label>
              <input value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} required placeholder="Ej: Geolocalización" />
            </div>
            <div className="field"><label>Tipo de dato</label>
              <select value={form.tipo_dato} onChange={e => setForm({...form, tipo_dato: e.target.value})}>
                {TIPOS_DATO.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="field full"><label>Descripción</label>
              <textarea value={form.descripcion} onChange={e => setForm({...form, descripcion: e.target.value})} rows={2} placeholder="Descripción de la categoría..." />
            </div>
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn-ghost btn-sm" onClick={() => setShowForm(false)}>Cancelar</button>
            <button type="submit" className="btn btn-pri btn-sm">Guardar</button>
          </div>
        </form>
      )}

      {loading ? <div className="loading">Cargando...</div> : (
        <div className="table-card">
          <table className="rat-table">
            <thead>
              <tr>
                <th>ID</th><th>Nombre</th><th>Descripción</th><th>Tipo</th>
              </tr>
            </thead>
            <tbody>
              {items.map(item => (
                <tr key={item.id}>
                  <td style={{ color: 'var(--text3)', fontSize: '0.72rem' }}>{item.id}</td>
                  <td style={{ fontWeight: 600 }}>{item.nombre}</td>
                  <td style={{ color: 'var(--text2)', fontSize: '0.78rem' }}>{item.descripcion || '—'}</td>
                  <td>
                    <span className={`badge ${
                      item.tipo_dato === 'sensible' ? 'badge-rose' :
                      item.tipo_dato === 'biométrico' ? 'badge-gold' :
                      item.tipo_dato === 'financiero' ? 'badge-lav' :
                      'badge-pri'
                    }`}>
                      {item.tipo_dato}
                    </span>
                  </td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr><td colSpan={4} style={{ textAlign: 'center', color: 'var(--text3)', padding: '2rem' }}>No hay categorías registradas.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

/* ─── Finalidades ───────────────────────────────────────────────────── */

function FinalidadesTab() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ nombre: '', descripcion: '' });

  const load = () => api.listarFinalidades().then(setItems).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    await api.crearFinalidad(form);
    setShowForm(false);
    setForm({ nombre: '', descripcion: '' });
    load();
  };

  return (
    <div>
      <div className="page-head" style={{ marginBottom: '0.75rem' }}>
        <span style={{ fontSize: '0.78rem', color: 'var(--text3)' }}>
          Catálogo de finalidades de tratamiento ({items.length} registros)
        </span>
        <button className="btn btn-pri btn-sm" onClick={() => setShowForm(true)}>+ Nueva finalidad</button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="form-section" style={{ marginBottom: '1rem' }}>
          <h3>Nueva finalidad de tratamiento</h3>
          <div className="form-grid">
            <div className="field"><label>Nombre *</label>
              <input value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} required placeholder="Ej: Marketing directo" />
            </div>
            <div className="field full"><label>Descripción</label>
              <textarea value={form.descripcion} onChange={e => setForm({...form, descripcion: e.target.value})} rows={2} placeholder="Descripción de la finalidad..." />
            </div>
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn-ghost btn-sm" onClick={() => setShowForm(false)}>Cancelar</button>
            <button type="submit" className="btn btn-pri btn-sm">Guardar</button>
          </div>
        </form>
      )}

      {loading ? <div className="loading">Cargando...</div> : (
        <div className="table-card">
          <table className="rat-table">
            <thead>
              <tr>
                <th>ID</th><th>Nombre</th><th>Descripción</th>
              </tr>
            </thead>
            <tbody>
              {items.map(item => (
                <tr key={item.id}>
                  <td style={{ color: 'var(--text3)', fontSize: '0.72rem' }}>{item.id}</td>
                  <td style={{ fontWeight: 600 }}>{item.nombre}</td>
                  <td style={{ color: 'var(--text2)', fontSize: '0.78rem' }}>{item.descripcion || '—'}</td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr><td colSpan={3} style={{ textAlign: 'center', color: 'var(--text3)', padding: '2rem' }}>No hay finalidades registradas.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

/* ─── Bases de Licitud ──────────────────────────────────────────────── */

function BasesTab() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ nombre: '', descripcion: '', referencia_legal: 'Ley 21.719' });

  const load = () => api.listarBasesLicitud().then(setItems).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    await api.crearBaseLicitud(form);
    setShowForm(false);
    setForm({ nombre: '', descripcion: '', referencia_legal: 'Ley 21.719' });
    load();
  };

  return (
    <div>
      <div className="page-head" style={{ marginBottom: '0.75rem' }}>
        <span style={{ fontSize: '0.78rem', color: 'var(--text3)' }}>
          Catálogo de bases de licitud ({items.length} registros)
        </span>
        <button className="btn btn-pri btn-sm" onClick={() => setShowForm(true)}>+ Nueva base</button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="form-section" style={{ marginBottom: '1rem' }}>
          <h3>Nueva base de licitud</h3>
          <div className="form-grid">
            <div className="field"><label>Nombre *</label>
              <input value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} required placeholder="Ej: Cumplimiento normativo" />
            </div>
            <div className="field"><label>Referencia legal</label>
              <input value={form.referencia_legal} onChange={e => setForm({...form, referencia_legal: e.target.value})} placeholder="Ej: Ley 21.719 Art. 18" />
            </div>
            <div className="field full"><label>Descripción</label>
              <textarea value={form.descripcion} onChange={e => setForm({...form, descripcion: e.target.value})} rows={2} placeholder="Descripción de la base de licitud..." />
            </div>
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn-ghost btn-sm" onClick={() => setShowForm(false)}>Cancelar</button>
            <button type="submit" className="btn btn-pri btn-sm">Guardar</button>
          </div>
        </form>
      )}

      {loading ? <div className="loading">Cargando...</div> : (
        <div className="table-card">
          <table className="rat-table">
            <thead>
              <tr>
                <th>ID</th><th>Nombre</th><th>Descripción</th><th>Ref. Legal</th>
              </tr>
            </thead>
            <tbody>
              {items.map(item => (
                <tr key={item.id}>
                  <td style={{ color: 'var(--text3)', fontSize: '0.72rem' }}>{item.id}</td>
                  <td style={{ fontWeight: 600 }}>{item.nombre}</td>
                  <td style={{ color: 'var(--text2)', fontSize: '0.78rem' }}>{item.descripcion || '—'}</td>
                  <td><span className="badge badge-pri">{item.referencia_legal || '—'}</span></td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr><td colSpan={4} style={{ textAlign: 'center', color: 'var(--text3)', padding: '2rem' }}>No hay bases de licitud registradas.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

/* ─── Asignaciones (Taxonomía por Actividad) ────────────────────────── */

function AsignacionesTab() {
  const [actividades, setActividades] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [finalidades, setFinalidades] = useState([]);
  const [bases, setBases] = useState([]);
  const [asignaciones, setAsignaciones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actividadId, setActividadId] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ actividad_id: '', categoria_id: '', finalidad_id: '', base_id: '' });

  useEffect(() => {
    Promise.all([
      api.listarActividades({ limit: 500 }),
      api.listarCategoriasDatos(),
      api.listarFinalidades(),
      api.listarBasesLicitud(),
    ]).then(([acts, cats, fins, bas]) => {
      setActividades(acts);
      setCategorias(cats);
      setFinalidades(fins);
      setBases(bas);
    }).finally(() => setLoading(false));
  }, []);

  const loadAsignaciones = (id) => {
    if (!id) { setAsignaciones([]); return; }
    api.listarAsignaciones(id).then(setAsignaciones);
  };

  const handleActividadChange = (e) => {
    const val = e.target.value;
    setActividadId(val);
    if (val) loadAsignaciones(Number(val));
    else setAsignaciones([]);
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    await api.crearAsignacion({
      actividad_id: Number(form.actividad_id),
      categoria_id: Number(form.categoria_id),
      finalidad_id: Number(form.finalidad_id),
      base_id: Number(form.base_id),
    });
    setShowForm(false);
    setForm({ actividad_id: form.actividad_id, categoria_id: '', finalidad_id: '', base_id: '' });
    loadAsignaciones(Number(form.actividad_id));
  };

  const getNombre = (list, id) => {
    const item = list.find(i => i.id === id);
    return item ? item.nombre : `ID ${id}`;
  };

  return (
    <div>
      <div className="page-head" style={{ marginBottom: '0.75rem' }}>
        <span style={{ fontSize: '0.78rem', color: 'var(--text3)' }}>
          Asigna taxonomía (categoría + finalidad + base) a una actividad
        </span>
        {actividadId && (
          <button className="btn btn-pri btn-sm" onClick={() => {
            setForm({ actividad_id: actividadId, categoria_id: '', finalidad_id: '', base_id: '' });
            setShowForm(true);
          }}>+ Asignar taxonomía</button>
        )}
      </div>

      <div className="form-section" style={{ marginBottom: '1rem', padding: '1rem' }}>
        <div className="field">
          <label>Seleccionar actividad</label>
          <select value={actividadId} onChange={handleActividadChange}>
            <option value="">— Selecciona una actividad —</option>
            {actividades.map(a => (
              <option key={a.id} value={a.id}>
                #{a.id} — {a.actividad_tratamiento?.slice(0, 80)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="form-section" style={{ marginBottom: '1rem' }}>
          <h3>Nueva asignación de taxonomía</h3>
          <div className="form-grid">
            <div className="field"><label>Categoría de dato *</label>
              <select value={form.categoria_id} onChange={e => setForm({...form, categoria_id: e.target.value})} required>
                <option value="">Seleccionar...</option>
                {categorias.map(c => (
                  <option key={c.id} value={c.id}>{c.nombre} ({c.tipo_dato})</option>
                ))}
              </select>
            </div>
            <div className="field"><label>Finalidad *</label>
              <select value={form.finalidad_id} onChange={e => setForm({...form, finalidad_id: e.target.value})} required>
                <option value="">Seleccionar...</option>
                {finalidades.map(f => (
                  <option key={f.id} value={f.id}>{f.nombre}</option>
                ))}
              </select>
            </div>
            <div className="field"><label>Base de licitud *</label>
              <select value={form.base_id} onChange={e => setForm({...form, base_id: e.target.value})} required>
                <option value="">Seleccionar...</option>
                {bases.map(b => (
                  <option key={b.id} value={b.id}>{b.nombre}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn-ghost btn-sm" onClick={() => setShowForm(false)}>Cancelar</button>
            <button type="submit" className="btn btn-pri btn-sm">Asignar</button>
          </div>
        </form>
      )}

      {loading ? <div className="loading">Cargando...</div> : !actividadId ? (
        <div className="empty" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text3)' }}>
          <p style={{ fontSize: '0.9rem' }}>Selecciona una actividad para ver sus asignaciones de taxonomía.</p>
        </div>
      ) : (
        <div className="table-card">
          <div className="table-header">
            <h2>📋 Asignaciones — Actividad #{actividadId}</h2>
            <span style={{ fontSize: '0.72rem', color: 'var(--text3)' }}>{asignaciones.length} registros</span>
          </div>
          <table className="rat-table">
            <thead>
              <tr>
                <th>ID</th><th>Categoría de Dato</th><th>Finalidad</th><th>Base de Licitud</th>
              </tr>
            </thead>
            <tbody>
              {asignaciones.map(a => (
                <tr key={a.id}>
                  <td style={{ color: 'var(--text3)', fontSize: '0.72rem' }}>{a.id}</td>
                  <td>
                    <span className="badge badge-pri">
                      {getNombre(categorias, a.categoria_id)}
                    </span>
                  </td>
                  <td>
                    <span className="badge badge-sage">
                      {getNombre(finalidades, a.finalidad_id)}
                    </span>
                  </td>
                  <td>
                    <span className="badge badge-gold">
                      {getNombre(bases, a.base_id)}
                    </span>
                  </td>
                </tr>
              ))}
              {asignaciones.length === 0 && (
                <tr><td colSpan={4} style={{ textAlign: 'center', color: 'var(--text3)', padding: '2rem' }}>
                  No hay asignaciones para esta actividad.
                </td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
