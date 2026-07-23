/**
 * CardMetric — Tarjeta de métrica tipo KPI para dashboards.
 *
 * Props:
 *   title  : string — etiqueta de la métrica
 *   value  : string|number — valor a mostrar
 *   icon?  : ReactNode — ícono (ej: <Activity size={20} />)
 *   color? : string — color CSS para el valor (default: var(--pri-dark))
 */
export default function CardMetric({ title, value, icon, color }) {
  return (
    <div className="kpi-card">
      {icon && <div className="kpi-icon">{icon}</div>}
      <div className="kpi-label">{title}</div>
      <div className="kpi-value" style={color ? { color } : undefined}>
        {value}
      </div>
    </div>
  );
}
