import { useState, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { api } from '../api';

const BASES_LEGALES = [
  'Consentimiento Informado', 'Ejecución de un contrato',
  'Obligación legal', 'Interés legítimo', 'Interés público',
  'Vital', 'Cumplimiento normativo sectorial',
];
const TITULARES_OPTS = ['Estudiantes', 'Funcionarios', 'Alumni', 'Prospectos', 'Proveedores', 'Menores (NNA)', 'Público general'];
const DATOS_OPTS = ['Identificación (nombre, RUT)', 'Contacto (email, teléfono)', 'Académicos (notas)',
  'Financieros / bancarios', 'Laborales', 'Navegación (IP, cookies)', 'Salud (sensible)',
  'Biométricos (sensible)', 'Origen racial o étnico (sensible)', 'Ideología / religión / sindical (sensible)',
  'Vida sexual (sensible)', 'Datos de niños/as y adolescentes'];
const AREAS_OPTS = ['CERETI', 'Admisión', 'Finanzas', 'TI', 'RRHH', 'Investigación', 'Biblioteca',
  'Bienestar Estudiantil', 'Docencia', 'Vinculación', 'Marketing', 'Jurídica', 'Carreras',
  'Vicerrectoría Académica', 'Dirección de Personas', 'Dirección de Docencia'];

export default function ActivityForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    actividad_tratamiento: '', finalidad: '', descripcion: '',
    responsable_tratamiento: 'UCT — Universidad Católica de Temuco',
    dpo_contacto: 'dpo@uct.cl',
    areas_intervienen: [], categoria_titulares: [], categorias_datos: [],
    origen_fuente: '', categoria_destinatarios: [], base_licitud: '',
    transferencia_internacional: '', plazo_conservacion: '',
    medidas_seguridad: '', decisiones_automatizadas: '',
  });

  useEffect(() => {
    if (id) {
      api.obtenerActividad(id).then(data => {
        setForm(prev => ({ ...prev, ...data }));
        setLoading(false);
      });
    }
  }, [id]);

  const toggleArray = (field, val) => {
    setForm(prev => ({
      ...prev,
      [field]: prev[field].includes(val)
        ? prev[field].filter(v => v !== val)
        : [...prev[field], val]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (isEdit) await api.actualizarActividad(id, form);
      else await api.crearActividad(form);
      navigate('/');
    } catch (err) {
      alert('Error: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="loading">Cargando...</div>;

  return (
    <div style={{ maxWidth: 800 }}>
      <div className="page-head">
        <Link to="/" className="back-link">← Volver al dashboard</Link>
        <h2>{isEdit ? 'Editar Actividad' : 'Nueva Actividad de Tratamiento'}</h2>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-section">
          <h3>Identificación</h3>
          <div className="form-grid">
            <div className="field full">
              <label>Actividad de Tratamiento *</label>
              <input value={form.actividad_tratamiento} onChange={e => setForm({...form, actividad_tratamiento: e.target.value})} required />
            </div>
            <div className="field">
              <label>Responsable</label>
              <input value={form.responsable_tratamiento} onChange={e => setForm({...form, responsable_tratamiento: e.target.value})} />
            </div>
            <div className="field">
              <label>DPO Contacto</label>
              <input value={form.dpo_contacto} onChange={e => setForm({...form, dpo_contacto: e.target.value})} />
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Finalidad y Descripción</h3>
          <div className="form-grid">
            <div className="field full">
              <label>Finalidad del Tratamiento *</label>
              <textarea value={form.finalidad} onChange={e => setForm({...form, finalidad: e.target.value})} rows={2} required />
            </div>
            <div className="field full">
              <label>Descripción de la Actividad</label>
              <textarea value={form.descripcion} onChange={e => setForm({...form, descripcion: e.target.value})} rows={3} />
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Áreas, Titulares y Datos</h3>
          <div className="form-grid">
            <div className="field">
              <label>Áreas que Intervienen</label>
              <div className="chip-group">
                {AREAS_OPTS.map(a => (
                  <span key={a} className={`chip ${form.areas_intervienen.includes(a) ? 'checked' : ''}`}
                    onClick={() => toggleArray('areas_intervienen', a)}>{a}</span>
                ))}
              </div>
            </div>
            <div className="field">
              <label>Categoría de Titulares</label>
              <div className="chip-group">
                {TITULARES_OPTS.map(t => (
                  <span key={t} className={`chip ${form.categoria_titulares.includes(t) ? 'checked' : ''}`}
                    onClick={() => toggleArray('categoria_titulares', t)}>{t}</span>
                ))}
              </div>
            </div>
            <div className="field full">
              <label>Categorías de Datos Tratados</label>
              <div className="chip-group">
                {DATOS_OPTS.map(d => (
                  <span key={d} className={`chip ${form.categorias_datos.includes(d) ? 'checked' : ''}`}
                    onClick={() => toggleArray('categorias_datos', d)}>{d}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Origen, Destinatarios y Base Legal</h3>
          <div className="form-grid">
            <div className="field">
              <label>Origen o Fuente de los Datos</label>
              <input value={form.origen_fuente} onChange={e => setForm({...form, origen_fuente: e.target.value})} />
            </div>
            <div className="field">
              <label>Base de Licitud *</label>
              <select value={form.base_licitud} onChange={e => setForm({...form, base_licitud: e.target.value})} required>
                <option value="">Seleccionar...</option>
                {BASES_LEGALES.map(b => <option key={b} value={b}>{b}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Transferencia Internacional</label>
              <input value={form.transferencia_internacional} onChange={e => setForm({...form, transferencia_internacional: e.target.value})} placeholder="No aplica" />
            </div>
            <div className="field">
              <label>Plazo de Conservación *</label>
              <input value={form.plazo_conservacion} onChange={e => setForm({...form, plazo_conservacion: e.target.value})} required />
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Seguridad y Automatización</h3>
          <div className="form-grid">
            <div className="field full">
              <label>Medidas de Seguridad</label>
              <textarea value={form.medidas_seguridad} onChange={e => setForm({...form, medidas_seguridad: e.target.value})} rows={2} />
            </div>
            <div className="field">
              <label>Decisiones Automatizadas</label>
              <input value={form.decisiones_automatizadas} onChange={e => setForm({...form, decisiones_automatizadas: e.target.value})} placeholder="No aplica" />
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button type="button" className="btn btn-ghost" onClick={() => navigate('/')}>Cancelar</button>
          <button type="submit" className="btn btn-pri" disabled={saving}>
            {saving ? 'Guardando...' : (isEdit ? 'Actualizar' : 'Crear Actividad')}
          </button>
        </div>
      </form>
    </div>
  );
}
