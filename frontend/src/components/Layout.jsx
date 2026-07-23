import { Link, useLocation } from 'react-router-dom';

const navItems = [
  { icon: '◫', label: 'Dashboard',    path: '/' },
  { icon: '📋', label: 'Actividades',  path: '/actividades' },
  { icon: '🕊️', label: 'Brechas',      path: '/brechas' },
  { icon: '👤', label: 'ARSOP',        path: '/arsop' },
  { icon: '⚙',  label: 'Áreas',        path: '/areas' },
  { icon: '📊', label: 'Reportes',     path: '/reportes' },
];

export default function Layout({ children }) {
  const location = useLocation();

  const isActive = (path) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  const breadcrumb = location.pathname.split('/').filter(Boolean);

  return (
    <div className="app-shell">

      {/* ═══ NAVBAR ═══ */}
      <header className="navbar">
        <div className="navbar-inner">
          <div className="navbar-left">
            <Link to="/" className="navbar-brand">
              <img src="/logo.png" alt="RAT UCT" className="navbar-logo" />
              <span className="navbar-title">RAT UCT</span>
            </Link>
            <nav className="navbar-nav">
              {navItems.map(item => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`nav-tab${isActive(item.path) ? ' active' : ''}`}
                >
                  <span className="nav-tab-icon">{item.icon}</span>
                  <span className="nav-tab-label">{item.label}</span>
                </Link>
              ))}
            </nav>
          </div>
          <div className="navbar-right">
            <span className="navbar-badge">Ley 21.719</span>
            <div className="navbar-user">
              <span className="user-label">DPO</span>
              <span className="user-value">pendiente</span>
            </div>
            <div className="navbar-avatar" title="Admin">AD</div>
          </div>
        </div>
      </header>

      {/* ═══ BREADCRUMB ═══ */}
      <div className="breadcrumb-bar">
        <Link to="/">Inicio</Link>
        {breadcrumb.length > 0 && breadcrumb.map((seg, i) => (
          <span key={seg}>
            <span className="sep">›</span>
            <span>{decodeURIComponent(seg)}</span>
          </span>
        ))}
      </div>

      {/* ═══ CONTENT ═══ */}
      <main className="main-content">
        {children}
      </main>

      {/* ═══ FOOTER ═══ */}
      <footer className="footer">
        <div className="footer-inner">
          <span>
            © 2026 <a href="https://gobiernodedatos.uct.cl/" target="_blank" rel="noopener">Programa de Gobierno de Datos</a> · Universidad Católica de Temuco
          </span>
          <span>RAT UCT — Ley 21.719</span>
        </div>
      </footer>

    </div>
  );
}
