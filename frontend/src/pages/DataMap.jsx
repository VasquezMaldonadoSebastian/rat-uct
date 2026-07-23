import { useState, useEffect, useMemo } from 'react';
import {
  Building2,
  Users,
  ArrowRight,
  Database,
  AlertTriangle,
  RefreshCw,
  Loader2,
} from 'lucide-react';
import { apiV1 } from '../api';
import ErrorAlert from '../components/ErrorAlert';

/* ── Node colours mapped by id for visual consistency ── */
const NODE_COLORS = [
  '#0086CA', '#2D8F5C', '#E8A838', '#D64045',
  '#6B5EAE', '#E07B39', '#3BA3A0', '#B87333',
  '#5A7D9A', '#C44569', '#3DC1A0', '#A0522D',
  '#4A6FA5', '#D4836A', '#5F9EA0', '#9B59B6',
  '#1ABC9C', '#E67E22', '#2ECC71', '#3498DB',
];

function getColor(index) {
  return NODE_COLORS[index % NODE_COLORS.length];
}

/* ── Helper: cubic bezier path between two points ── */
function linkPath(x1, y1, x2, y2) {
  const cx = (x1 + x2) / 2;
  return `M${x1},${y1} C${cx},${y1} ${cx},${y2} ${x2},${y2}`;
}

/* ══════════════════════════════════════════════
   DATA FLOW MAP
   ══════════════════════════════════════════════ */
export default function DataMap() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hoveredLink, setHoveredLink] = useState(null);

  function load() {
    setLoading(true);
    setError(null);
    apiV1
      .dataFlow()
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
  }, []);

  /* ── Layout computation ── */
  const { leftNodes, rightNodes, links, maxCount } = useMemo(() => {
    if (!data) return { leftNodes: [], rightNodes: [], links: [], maxCount: 0 };

    const areas = data.nodos
      .filter((n) => n.tipo === 'area')
      .sort((a, b) => a.nombre.localeCompare(b.nombre));
    const dests = data.nodos
      .filter((n) => n.tipo === 'destinatario')
      .sort((a, b) => a.nombre.localeCompare(b.nombre));

    const m = Math.max(...data.enlaces.map((e) => e.count), 1);

    return { leftNodes: areas, rightNodes: dests, links: data.enlaces, maxCount: m };
  }, [data]);

  /* ── SVG dimensions ── */
  const NODE_HEIGHT = 32;
  const NODE_GAP = 12;
  const PADDING_TOP = 20;
  const PADDING_BOTTOM = 20;
  const LEFT_WIDTH = 160;
  const RIGHT_WIDTH = 160;
  const SVG_MIDDLE = 240;

  const leftCount = leftNodes.length;
  const rightCount = rightNodes.length;
  const svgHeight = Math.max(
    PADDING_TOP + leftCount * (NODE_HEIGHT + NODE_GAP) + PADDING_BOTTOM,
    PADDING_TOP + rightCount * (NODE_HEIGHT + NODE_GAP) + PADDING_BOTTOM,
    300,
  );

  function getLeftY(idx) {
    const totalH = leftCount * (NODE_HEIGHT + NODE_GAP) - NODE_GAP;
    const startY = (svgHeight - totalH) / 2;
    return startY + idx * (NODE_HEIGHT + NODE_GAP) + NODE_HEIGHT / 2;
  }

  function getRightY(idx) {
    const totalH = rightCount * (NODE_HEIGHT + NODE_GAP) - NODE_GAP;
    const startY = (svgHeight - totalH) / 2;
    return startY + idx * (NODE_HEIGHT + NODE_GAP) + NODE_HEIGHT / 2;
  }

  const lx = LEFT_WIDTH;
  const rx = LEFT_WIDTH + SVG_MIDDLE;
  const totalWidth = LEFT_WIDTH + SVG_MIDDLE + RIGHT_WIDTH + 40;

  /* ── Node index maps ── */
  const leftIdx = {};
  leftNodes.forEach((n, i) => {
    leftIdx[n.id] = i;
  });
  const rightIdx = {};
  rightNodes.forEach((n, i) => {
    rightIdx[n.id] = i;
  });

  /* ── Filter visible links ── */
  const visibleLinks = links.filter(
    (l) => leftIdx[l.source] !== undefined && rightIdx[l.target] !== undefined,
  );

  /* ── Loading ── */
  if (loading) {
    return (
      <div className="loading">
        <Loader2
          size={22}
          style={{
            animation: 'spin 1s linear infinite',
            verticalAlign: 'middle',
            marginRight: 8,
          }}
        />
        Cargando mapa de flujo de datos...
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  /* ── Error ── */
  if (error) {
    return <ErrorAlert message={`Error al cargar flujo de datos: ${error}`} onRetry={load} />;
  }

  /* ── Empty state ── */
  if (!data || leftNodes.length === 0 || visibleLinks.length === 0) {
    return (
      <div className="table-card">
        <div className="table-header">
          <h2>
            <Database size={16} /> Mapa de Flujo de Datos
          </h2>
        </div>
        <div className="empty">
          <Database size={40} style={{ opacity: 0.3, marginBottom: '0.5rem' }} />
          <p>No hay datos de flujo disponibles</p>
          <p style={{ fontSize: '0.78rem', color: 'var(--text4)', marginTop: '0.25rem' }}>
            Registra actividades con áreas y destinatarios para visualizar el flujo de datos.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="table-card">
      <div className="table-header">
        <h2>
          <Database size={16} /> Mapa de Flujo de Datos
        </h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.72rem', color: 'var(--text3)' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <Building2 size={13} /> Áreas: {leftNodes.length}
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <Users size={13} /> Destinatarios: {rightNodes.length}
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <ArrowRight size={13} /> Conexiones: {visibleLinks.length}
          </span>
        </div>
      </div>

      <div style={{ overflowX: 'auto', padding: '0.75rem 1rem' }}>
        <svg
          width={totalWidth}
          height={svgHeight}
          viewBox={`0 0 ${totalWidth} ${svgHeight}`}
          style={{ display: 'block', margin: '0 auto', minWidth: totalWidth }}
        >
          {/* ── Links (bezier curves) ── */}
          {visibleLinks.map((link, i) => {
            const sx = lx;
            const sy = getLeftY(leftIdx[link.source]);
            const tx = rx;
            const ty = getRightY(rightIdx[link.target]);
            const thickness = Math.max(1.5, (link.count / maxCount) * 8);
            const isHovered = hoveredLink === i;
            const opacity = hoveredLink !== null ? (isHovered ? 1 : 0.12) : 0.35;

            return (
              <g key={`link-${i}`}>
                {/* Invisible wide path for hover */}
                <path
                  d={linkPath(sx, sy, tx, ty)}
                  fill="none"
                  stroke="transparent"
                  strokeWidth={16}
                  style={{ cursor: 'pointer' }}
                  onMouseEnter={() => setHoveredLink(i)}
                  onMouseLeave={() => setHoveredLink(null)}
                />
                {/* Visible line */}
                <path
                  d={linkPath(sx, sy, tx, ty)}
                  fill="none"
                  stroke="#0086CA"
                  strokeWidth={thickness}
                  strokeOpacity={opacity}
                  style={{ transition: 'stroke-opacity 0.15s' }}
                />
                {/* Count label at midpoint of curve */}
                {isHovered && (
                  <g>
                    <rect
                      x={(sx + tx) / 2 - 14}
                      y={(sy + ty) / 2 - 10}
                      width={28}
                      height={20}
                      rx={10}
                      fill="#002855"
                    />
                    <text
                      x={(sx + tx) / 2}
                      y={(sy + ty) / 2 + 4}
                      textAnchor="middle"
                      fill="#fff"
                      fontSize={11}
                      fontWeight={700}
                    >
                      {link.count}
                    </text>
                  </g>
                )}
              </g>
            );
          })}

          {/* ── Left nodes (Areas) ── */}
          {leftNodes.map((node, i) => {
            const y = getLeftY(i) - NODE_HEIGHT / 2;
            const color = getColor(i);
            return (
              <g key={`left-${node.id}`}>
                <rect
                  x={0}
                  y={y}
                  width={LEFT_WIDTH}
                  height={NODE_HEIGHT}
                  rx={6}
                  fill={color}
                  opacity={0.12}
                />
                <rect
                  x={0}
                  y={y}
                  width={4}
                  height={NODE_HEIGHT}
                  rx={2}
                  fill={color}
                />
                <text
                  x={14}
                  y={y + NODE_HEIGHT / 2 + 4}
                  fill="var(--text)"
                  fontSize={12}
                  fontWeight={600}
                >
                  {node.nombre}
                </text>
              </g>
            );
          })}

          {/* ── Right nodes (Destinatarios) ── */}
          {rightNodes.map((node, i) => {
            const y = getRightY(i) - NODE_HEIGHT / 2;
            const color = getColor(i);
            return (
              <g key={`right-${node.id}`}>
                <rect
                  x={rx}
                  y={y}
                  width={RIGHT_WIDTH}
                  height={NODE_HEIGHT}
                  rx={6}
                  fill={color}
                  opacity={0.12}
                />
                <rect
                  x={rx + RIGHT_WIDTH - 4}
                  y={y}
                  width={4}
                  height={NODE_HEIGHT}
                  rx={2}
                  fill={color}
                />
                <text
                  x={rx + 14}
                  y={y + NODE_HEIGHT / 2 + 4}
                  fill="var(--text)"
                  fontSize={12}
                  fontWeight={600}
                >
                  {node.nombre}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* ── Hovered link detail ── */}
      {hoveredLink !== null && visibleLinks[hoveredLink] && (() => {
        const link = visibleLinks[hoveredLink];
        return (
          <div
            style={{
              padding: '0.75rem 1.25rem',
              borderTop: '1px solid var(--border2)',
              background: 'var(--pri-bg)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              fontSize: '0.82rem',
              color: 'var(--pri-dark)',
              fontWeight: 500,
            }}
          >
            <Building2 size={14} />
            <span>{link.source}</span>
            <ArrowRight size={14} />
            <Users size={14} />
            <span>{link.target}</span>
            <span style={{ marginLeft: 'auto', background: 'var(--pri-dark)', color: '#fff', padding: '0.15rem 0.6rem', borderRadius: '12px', fontSize: '0.72rem', fontWeight: 700 }}>
              {link.count} {link.count === 1 ? 'actividad' : 'actividades'}
            </span>
          </div>
        );
      })()}
    </div>
  );
}
