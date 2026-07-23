import { useState } from 'react';
import { Shield, Send, CheckCircle, AlertCircle, User, Mail, FileText, Hash } from 'lucide-react';
import { api } from '../api';

const TIPOS_DERECHO = ['Acceso', 'Rectificacion', 'Supresion', 'Oposicion', 'Portabilidad'];

const DESCRIPCION_DERECHOS = {
  Acceso:
    'Obtener confirmación sobre si tus datos personales están siendo tratados y acceder a ellos.',
  Rectificacion:
    'Solicitar la corrección de tus datos personales si son inexactos o están incompletos.',
  Supresion:
    'Solicitar la eliminación de tus datos personales cuando ya no sean necesarios para los fines que motivaron su tratamiento.',
  Oposicion:
    'Oponerte al tratamiento de tus datos personales por motivos relacionados con tu situación particular.',
  Portabilidad:
    'Recibir tus datos personales en un formato estructurado y de uso común para transmitirlos a otro responsable.',
};

const INITIAL_FORM = {
  tipo_derecho: '',
  solicitante_nombre: '',
  solicitante_email: '',
  solicitante_rut: '',
  descripcion: '',
};

export default function PrivacyCenter() {
  const [form, setForm] = useState(INITIAL_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (success) setSuccess(null);
    if (error) setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setSuccess(null);
    try {
      const result = await api.crearArsop(form);
      const numero = result?.id || result?.numero_solicitud || result?.folio || '—';
      setSuccess(
        `Solicitud ARSOP enviada exitosamente. Número de solicitud: ${numero}`
      );
      setForm(INITIAL_FORM);
    } catch (err) {
      setError(err.message || 'Error al enviar la solicitud. Intenta nuevamente.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: 820, margin: '0 auto', padding: '2rem 1rem 3rem' }}>
      {/* ── Hero Header ── */}
      <div
        style={{
          textAlign: 'center',
          marginBottom: '2.5rem',
          padding: '3rem 1.5rem 2rem',
          background: 'linear-gradient(135deg, #002855 0%, #004B87 50%, #0086CA 100%)',
          borderRadius: 16,
          color: '#fff',
        }}
      >
        <div
          style={{
            width: 72,
            height: 72,
            borderRadius: '50%',
            background: 'rgba(255,255,255,0.15)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '1rem',
            backdropFilter: 'blur(4px)',
          }}
        >
          <Shield size={36} />
        </div>
        <h1
          style={{
            fontSize: '1.6rem',
            fontWeight: 700,
            marginBottom: '0.5rem',
            letterSpacing: '-0.5px',
          }}
        >
          Portal de Privacidad
        </h1>
        <p style={{ fontSize: '0.9rem', opacity: 0.85, maxWidth: 560, margin: '0 auto', lineHeight: 1.6 }}>
          Ejerce tus derechos ARSOP sobre tus datos personales ante la Pontificia Universidad
          Católica de Chile
        </p>
      </div>

      {/* ── Rights Info ── */}
      <div
        className="card"
        style={{ marginBottom: '1.5rem', padding: '1.5rem 1.5rem 1rem' }}
      >
        <h2
          style={{
            fontSize: '1rem',
            fontWeight: 700,
            marginBottom: '0.5rem',
            color: 'var(--pri-dark)',
          }}
        >
          ¿Qué son los derechos ARSOP?
        </h2>
        <p style={{ fontSize: '0.82rem', color: 'var(--text2)', marginBottom: '1rem', lineHeight: 1.7 }}>
          La Ley N° 19.628 sobre Protección de la Vida Privada y la normativa de protección de
          datos reconocen los siguientes derechos que puedes ejercer como titular de datos
          personales:
        </p>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '0.75rem',
          }}
        >
          {TIPOS_DERECHO.map((d) => (
            <div
              key={d}
              style={{
                background: 'var(--pri-bg)',
                borderRadius: 10,
                padding: '0.85rem 1rem',
                border: '1px solid var(--border)',
              }}
            >
              <h3
                style={{
                  fontSize: '0.82rem',
                  fontWeight: 700,
                  color: 'var(--pri-dark)',
                  marginBottom: '0.25rem',
                }}
              >
                {d}
              </h3>
              <p style={{ fontSize: '0.72rem', color: 'var(--text2)', lineHeight: 1.5 }}>
                {DESCRIPCION_DERECHOS[d]}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Form ── */}
      <div className="form-section" style={{ padding: '1.75rem' }}>
        <h3
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            fontSize: '0.9rem',
          }}
        >
          <FileText size={16} />
          Formulario de Solicitud ARSOP
        </h3>
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="field full">
              <label>Tipo de derecho *</label>
              <select
                name="tipo_derecho"
                value={form.tipo_derecho}
                onChange={handleChange}
                required
              >
                <option value="">Selecciona un derecho...</option>
                {TIPOS_DERECHO.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>

            <div className="field">
              <label>
                <User size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} /> Nombre
                completo *
              </label>
              <input
                name="solicitante_nombre"
                value={form.solicitante_nombre}
                onChange={handleChange}
                placeholder="Ej: Juan Pérez González"
                required
              />
            </div>

            <div className="field">
              <label>
                <Mail size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} /> Email *
              </label>
              <input
                type="email"
                name="solicitante_email"
                value={form.solicitante_email}
                onChange={handleChange}
                placeholder="Ej: juan.perez@ejemplo.cl"
                required
              />
            </div>

            <div className="field">
              <label>
                <Hash size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} /> RUT
              </label>
              <input
                name="solicitante_rut"
                value={form.solicitante_rut}
                onChange={handleChange}
                placeholder="Ej: 12.345.678-9 (opcional)"
              />
            </div>

            <div className="field full">
              <label>
                <FileText size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />{' '}
                Descripción *
              </label>
              <textarea
                name="descripcion"
                value={form.descripcion}
                onChange={handleChange}
                placeholder="Describe tu solicitud en detalle..."
                rows={4}
                required
              />
            </div>
          </div>

          {/* Messages */}
          {error && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                marginTop: '1rem',
                padding: '0.75rem 1rem',
                borderRadius: 8,
                background: 'var(--rose-bg)',
                color: 'var(--rose-dark)',
                fontSize: '0.82rem',
                border: '1px solid rgba(214,64,69,0.2)',
              }}
            >
              <AlertCircle size={16} style={{ flexShrink: 0 }} />
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                marginTop: '1rem',
                padding: '0.75rem 1rem',
                borderRadius: 8,
                background: 'var(--sage-bg)',
                color: 'var(--sage-dark)',
                fontSize: '0.82rem',
                border: '1px solid rgba(45,143,92,0.2)',
              }}
            >
              <CheckCircle size={16} style={{ flexShrink: 0 }} />
              <span>{success}</span>
            </div>
          )}

          <div className="form-actions">
            <button type="submit" className="btn btn-pri" disabled={submitting}>
              <Send size={14} />
              {submitting ? 'Enviando...' : 'Enviar solicitud'}
            </button>
          </div>
        </form>
      </div>

      {/* ── Footer Note ── */}
      <div
        style={{
          textAlign: 'center',
          marginTop: '1.5rem',
          fontSize: '0.72rem',
          color: 'var(--text3)',
          lineHeight: 1.6,
          padding: '0 1rem',
        }}
      >
        <p>
          Tus datos serán tratados de acuerdo a nuestra{' '}
          <a href="#" style={{ color: 'var(--pri)', textDecoration: 'none' }}>
            Política de Privacidad
          </a>{' '}
          y la Ley N° 19.628. Te contactaremos al correo proporcionado para dar seguimiento a tu
          solicitud.
        </p>
      </div>
    </div>
  );
}
