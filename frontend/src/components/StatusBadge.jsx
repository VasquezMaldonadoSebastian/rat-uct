/**
 * StatusBadge — Badge coloreado para estados.
 *
 * Props:
 *   status  : string — el valor del estado
 *   mapping?: Record<string, string> — dict opcional status → clase CSS badge
 *
 * Mapa default:
 *   activo     → badge-sage  (green)
 *   archivado  → badge-gold  (gray/amber)
 *   revisión   → badge-gold  (orange)
 *   abierta    → badge-rose  (red)
 *   recibida   → badge-pri   (blue)
 *   respondida → badge-sage  (green)
 *   rechazada  → badge-rose  (red)
 *   en_estudio → badge-gold  (amber)
 */
const DEFAULT_MAPPING = {
  activo:     'badge-sage',
  archivado:  'badge-gold',
  revisión:   'badge-gold',
  abierta:    'badge-rose',
  recibida:   'badge-pri',
  respondida: 'badge-sage',
  rechazada:  'badge-rose',
  en_estudio: 'badge-gold',
  crítica:    'badge-rose',
  alta:       'badge-gold',
  media:      'badge-pri',
  baja:       'badge-sage',
  alto:       'badge-gold',
  medio:      'badge-pri',
  bajo:       'badge-sage',
};

export default function StatusBadge({ status, mapping }) {
  const resolved = { ...DEFAULT_MAPPING, ...mapping };
  const cls = resolved[status] || 'badge-pri';

  return (
    <span className={`badge ${cls}`}>
      {status}
    </span>
  );
}
