import { Link, useLocation } from 'react-router-dom';
import { MessageSquare, Search, Home as HomeIcon, Sun, Moon } from 'lucide-react';
import './Navbar.css';

/**
 * Navbar — Top navigation bar.
 *
 * Provides navigation between Home, Search, and Chat pages with a theme toggler.
 */
export default function Navbar({ theme, toggleTheme }) {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar" id="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand" aria-label="LabhArth AI Home">
          {/* Custom chakra vector logo */}
          <svg className="navbar-logo-svg" width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M4 6H20" stroke="var(--color-accent)" strokeWidth="3" strokeLinecap="round"/>
            <circle cx="12" cy="12" r="3.5" stroke="var(--color-primary)" strokeWidth="2"/>
            <circle cx="12" cy="12" r="1" fill="var(--color-primary)"/>
            <path d="M4 18H20" stroke="var(--color-secondary)" strokeWidth="3" strokeLinecap="round"/>
          </svg>
          <span className="navbar-title">LabhArth AI</span>
        </Link>

        <div className="navbar-links">
          <Link
            to="/"
            className={`navbar-link ${isActive('/') ? 'active' : ''}`}
            id="nav-home"
          >
            <HomeIcon size={16} className="nav-icon" />
            <span>Home</span>
          </Link>
          <Link
            to="/search"
            className={`navbar-link ${isActive('/search') ? 'active' : ''}`}
            id="nav-search"
          >
            <Search size={16} className="nav-icon" />
            <span>Search Schemes</span>
          </Link>
          <Link
            to="/chat"
            className={`navbar-link navbar-link--cta ${isActive('/chat') ? 'active' : ''}`}
            id="nav-chat"
          >
            <MessageSquare size={16} className="nav-icon-cta" />
            <span>Ask AI</span>
          </Link>

          <button
            onClick={toggleTheme}
            className="theme-toggle-btn"
            aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
          >
            {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
          </button>
        </div>
      </div>
    </nav>
  );
}
