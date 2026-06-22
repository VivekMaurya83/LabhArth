import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

/**
 * Navbar — Top navigation bar.
 *
 * Provides navigation between Home, Search, and Chat pages.
 * Highlights the active route.
 */
export default function Navbar() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar" id="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <span className="navbar-logo">🇮🇳</span>
          <span className="navbar-title">LabhArth AI</span>
        </Link>

        <div className="navbar-links">
          <Link
            to="/"
            className={`navbar-link ${isActive('/') ? 'active' : ''}`}
            id="nav-home"
          >
            Home
          </Link>
          <Link
            to="/search"
            className={`navbar-link ${isActive('/search') ? 'active' : ''}`}
            id="nav-search"
          >
            Search Schemes
          </Link>
          <Link
            to="/chat"
            className={`navbar-link navbar-link--cta ${isActive('/chat') ? 'active' : ''}`}
            id="nav-chat"
          >
            💬 Ask AI
          </Link>
        </div>
      </div>
    </nav>
  );
}
