/**
 * SchemeCard — Displays a government scheme search result.
 *
 * Shows scheme name, category, level, and a brief description.
 * Links to the full scheme details page.
 */

import { Link } from 'react-router-dom';
import './SchemeCard.css';

export default function SchemeCard({ scheme }) {
  return (
    <Link to={`/scheme/${scheme.id}`} className="scheme-card" id={`scheme-card-${scheme.id}`}>
      <div className="scheme-card-header">
        <span className="scheme-card-level">{scheme.level || 'Central'}</span>
        {scheme.category && (
          <span className="scheme-card-category">{scheme.category}</span>
        )}
      </div>
      <h3 className="scheme-card-title">{scheme.name}</h3>
      {scheme.description && (
        <p className="scheme-card-desc">{scheme.description}</p>
      )}
      {scheme.state && (
        <span className="scheme-card-state">📍 {scheme.state}</span>
      )}
    </Link>
  );
}
