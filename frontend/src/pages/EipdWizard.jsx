import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { api } from '../api';

const PASOS = ['Diagnóstico', 'Evaluación de Riesgo', 'Medidas', 'Aprobación'];

export default function EipdWizard() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [actividad, setActividad] = useState(null);
  const [paso, setPaso] = useState(0);
  const [saving, setSaving] = useState(false);
  const [eipd, setEipd] = useState({
    actividad_id: parseInt(id),
    necesita_eipd: null,
    motivo_activacion: '',
    riesgo_inherente: '',
    riesgo_residual: '',
    medidas_propuestas: '',
    medidas_implementadas: '',
    aprobado_por: '',
  });

  useEffect(() => {
    api.obtenerActividad(id).then(setActividad);
    api.listarEipd(id).then(list => {
      if (list.length > 0) {
        setEipd(prev => ({ ...prev, ...list[0] }));
        // Determinar paso según estado
        const estados = ['borrador', 'en_curso', 'completado', 'firmado'];
        const idx = estados.indexOf(list[0].estado);
        if (idx >= 0) setPaso(Math.min(idx, 3));
      }
    });
  }, [id]);

  const handleSave = async (avanzar = true) => {
    setSaving(true);
    try {
      const payload = { ...eipd, estado: avanzar ? ['borrador', 'en_curso', 'completado', 'firmado'][Math.min(paso + 1, 3)] : 'borrador' };
      await api.crearEipd(payload);
      if (avanzar && paso < 3) setPaso(paso + 1);
    } catch (e) {
      // Intentar actualizar si ya existe
      try {
        const existentes = await api.listarEipd(id);
        if (existentes.length > 0) {
          await api.actualizarEipd(existentes[0].id, { ...eipd, estado: avanzar ? ['borrador', 'en_curso', 'completado', 'firmado'][Math.min(paso + 1, 3)] : 'borrador' });
          if (avanzar && paso < 3) setPaso(paso + 1);
        }
      } catch (e2) {
        alert('Error al guardar: ' + e2.message);
      }
    }
    setSaving(false);
  };

  if (!actividad) return <div className="loading">Cargando...</div>;

  return (
    <div style={{ maxWidth: 700 }}>
      <div className="page-head">
        <Link to={`/actividades/${id}`} className="back-link">← Volver</Link>
        <h2>EIPD: {actividad.actividad_tratamiento}</h2>
      </div>

      {/* Barra de progreso */}
      <div className="wizard-progress">
        {PASOS.map((p, i) => (
          <div key={p} className={`wizard-step ${i < paso ? 'completed' : i === paso ? 'active' : 'pending'}`}
            onClick={() => i <= paso + 1 && setPaso(i)}>
            {i + 1}. {p}
          </div>
        ))}
      </div>

      <div className="form-section">
        {paso === 0 && (
          <>
            <h3>Paso 1: Diagnóstico</h3>
            <p style={{ fontSize: '0.85rem', color: '#515151', marginBottom: '1rem' }}>
              Determina si esta actividad requiere una Evaluación de Impacto en Protección de Datos.
            </p>
            <div className="form-grid">
              <div className="field full">
                <label>¿Requiere EIPD?</label>
                <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.3rem' }}>
                  <button className={`btn ${eipd.necesita_eipd === true ? 'btn-pri' : 'btn-ghost'}`}
                    onClick={() => setEipd({...eipd, necesita_eipd: true})}>Sí</button>
                  <button className={`btn ${eipd.necesita_eipd === false ? 'btn-pri' : 'btn-ghost'}`}
                    onClick={() => setEipd({...eipd, necesita_eipd: false})}>No</button>
                </div>
              </div>
              <div className="field full">
                <label>Motivo de activación</label>
                <select value={eipd.motivo_activacion} onChange={e => setEipd({...eipd, motivo_activacion: e.target.value})}>
                  <option value="">Seleccionar...</option>
                  <option value="datos_sensibles">Datos sensibles</option>
                  <option value="nna">Involucra NNA</option>
                  <option value="gran_escala">Gran escala</option>
                  <option value="transferencias">Transferencias internacionales</option>
                  <option value="perfilamiento">Perfilamiento / decisiones automatizadas</option>
                  <option value="colectivo">Datos de grupos vulnerables</option>
                </select>
              </div>
            </div>
          </>
        )}

        {paso === 1 && (
          <>
            <h3>Paso 2: Evaluación de Riesgo</h3>
            <p style={{ fontSize: '0.85rem', color: '#515151', marginBottom: '1rem' }}>
              Clasifica el nivel de riesgo inherente y el riesgo residual después de aplicar medidas.
            </p>
            <div className="form-grid">
              <div className="field">
                <label>Riesgo Inherente</label>
                <select value={eipd.riesgo_inherente} onChange={e => setEipd({...eipd, riesgo_inherente: e.target.value})}>
                  <option value="">Seleccionar...</option>
                  <option value="bajo">Bajo</option>
                  <option value="medio">Medio</option>
                  <option value="alto">Alto</option>
                  <option value="crítico">Crítico</option>
                </select>
              </div>
              <div className="field">
                <label>Riesgo Residual</label>
                <select value={eipd.riesgo_residual} onChange={e => setEipd({...eipd, riesgo_residual: e.target.value})}>
                  <option value="">Seleccionar...</option>
                  <option value="bajo">Bajo</option>
                  <option value="medio">Medio</option>
                  <option value="alto">Alto</option>
                  <option value="crítico">Crítico</option>
                </select>
              </div>
            </div>
          </>
        )}

        {paso === 2 && (
          <>
            <h3>Paso 3: Medidas</h3>
            <p style={{ fontSize: '0.85rem', color: '#515151', marginBottom: '1rem' }}>
              Describe las medidas propuestas y las implementadas para mitigar el riesgo.
            </p>
            <div className="form-grid">
              <div className="field full">
                <label>Medidas Propuestas</label>
                <textarea value={eipd.medidas_propuestas} onChange={e => setEipd({...eipd, medidas_propuestas: e.target.value})}
                  rows={3} placeholder="Ej: cifrado en reposo, control de acceso por roles, MFA..." />
              </div>
              <div className="field full">
                <label>Medidas Implementadas</label>
                <textarea value={eipd.medidas_implementadas} onChange={e => setEipd({...eipd, medidas_implementadas: e.target.value})}
                  rows={3} placeholder="Ej: se implementó cifrado AES-256, se configuró RBAC en AD..." />
              </div>
            </div>
          </>
        )}

        {paso === 3 && (
          <>
            <h3>Paso 4: Aprobación</h3>
            <p style={{ fontSize: '0.85rem', color: '#515151', marginBottom: '1rem' }}>
              Firma y aprueba la evaluación de impacto.
            </p>
            <div className="form-grid">
              <div className="field">
                <label>Aprobado por</label>
                <input value={eipd.aprobado_por} onChange={e => setEipd({...eipd, aprobado_por: e.target.value})}
                  placeholder="Nombre del DPO o responsable" />
              </div>
              <div className="field">
                <label>Fecha de aprobación</label>
                <input type="date" value={eipd.fecha_aprobacion || ''} onChange={e => setEipd({...eipd, fecha_aprobacion: e.target.value})} />
              </div>
              <div className="field full" style={{ marginTop: '0.5rem' }}>
                <div style={{ background: '#f0f8ff', borderRadius: 8, padding: '1rem', border: '1px solid #78c2ff55' }}>
                  <strong style={{ color: '#0086CA' }}>📋 Resumen</strong>
                  <p style={{ fontSize: '0.82rem', color: '#515151', marginTop: '0.5rem' }}>
                    Actividad: <strong>{actividad.actividad_tratamiento}</strong><br />
                    Riesgo inherente: <strong>{eipd.riesgo_inherente || '—'}</strong><br />
                    Riesgo residual: <strong>{eipd.riesgo_residual || '—'}</strong><br />
                    Medidas propuestas: {eipd.medidas_propuestas ? '✅' : '❌'} · Implementadas: {eipd.medidas_implementadas ? '✅' : '❌'}
                  </p>
                </div>
              </div>
            </div>
          </>
        )}

        <div className="form-actions" style={{ marginTop: '1.5rem' }}>
          {paso > 0 && (
            <button className="btn btn-ghost" onClick={() => setPaso(p => p - 1)}>Anterior</button>
          )}
          {paso < 3 ? (
            <button className="btn btn-pri" onClick={() => handleSave(true)} disabled={saving}>
              {saving ? 'Guardando...' : 'Guardar y continuar'}
            </button>
          ) : (
            <button className="btn btn-pri" onClick={async () => {
              await handleSave(true);
              navigate(`/actividades/${id}`);
            }} disabled={saving}>
              {saving ? 'Guardando...' : '✅ Firmar y finalizar'}
            </button>
          )}
          <button className="btn btn-ghost" onClick={() => handleSave(false)} disabled={saving}>
            Guardar borrador
          </button>
        </div>
      </div>
    </div>
  );
}
