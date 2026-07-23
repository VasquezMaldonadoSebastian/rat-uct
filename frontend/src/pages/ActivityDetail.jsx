import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api';

const fields = [
  'actividad_tratamiento', 'responsable_tratamiento', 'dpo_contacto',
  'areas_intervienen', 'finalidad', 'descripcion',
  'categoria_titulares', 'categorias_datos', 'datos_sensibles',
  'origen_fuente', 'base_licitud', 'transferencia_internacional',
  'plazo_conservacion', 'medidas_seguridad', 'decisiones_automatizadas',
];

const labels = {
  actividad_tratamiento: 'Actividad',
  responsable_tratamiento: 'Responsable',
  dpo_contacto: 'DPO',
  areas_intervienen: 'Áreas',
  finalidad: 'Finalidad',
  descripcion: 'Descripción',
  categoria_titulares: 'Titulares',
  categorias_datos: 'Categorías de Datos',
  datos_sensibles: 'Datos Sensibles',
  origen_fuente: 'Origen',
  base_licitud: 'Base Legal',
  transferencia_internacional: 'Transferencia Internacional',
  plazo_conservacion: 'Plazo de Conservación',
  medidas_seguridad: 'Medidas de Seguridad',
  decisiones_automatizadas: 'Decisiones Automatizadas',
};

function formatValue(a, key) {
  const val = a[key];
  if (key === 'datos_sensibles') return val ? '🔴 Sí' : '🟢 No';
  if (Array.isArray(val)) return val.join(', ');
  return val || '—';
}

export default function ActivityDetail() {
  const [actividad, setActividad] = useState(null);
  const { id } = useParams();

  useEffect(() => { api.obtenerActividad(id).then(setActividad); }, [id]);

  if (!actividad) return <div className="loading">Cargando actividad...</div>;

  return (
    <div>
      <div className="page-head">
        <Link to="/" className="back-link">← Volver al dashboard</Link>
        <h2>{actividad.actividad_tratamiento}</h2>
      </div>

      <div className="detail-card">
        <div className="detail-grid">
          {fields.map(f => (
            <div key={f} className="detail-item">
              <span className="detail-label">{labels[f]}</span>
              <span className="detail-value">{formatValue(actividad, f)}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="form-actions">
        <Link to={`/actividades/${id}/editar`} className="btn btn-pri">Editar actividad</Link>
        <Link to={`/actividades/${id}/eipd`} className="btn btn-ghost">Evaluar EIPD</Link>
        <Link to="/" className="btn btn-ghost">Volver</Link>
      </div>
    </div>
  );
}
