import { Link } from 'react-router-dom';
import { Building, MapPin, ArrowRight } from 'lucide-react';
import EligibilityBadge from './EligibilityBadge';
import './SchemeCard.css';

/**
 * SchemeCard — Displays summary information for a welfare scheme.
 *
 * Employs clean hierarchical sections for name, category tags, ministry, state,
 * benefits overview, and eligibility metrics.
 */
export default function SchemeCard({ scheme, eligibility }) {
  return (
    <div className="scheme-card" id={`scheme-card-${scheme.id}`}>
      <div className="scheme-card-header">
        <div className="scheme-card-tags">
          <span className="scheme-card-tag scheme-card-tag--level">
            {scheme.level || 'Central'}
          </span>
          {scheme.category && (
            <span className="scheme-card-tag scheme-card-tag--category">
              {scheme.category.replace(/_/g, ' ')}
            </span>
          )}
        </div>
        {eligibility && (
          <EligibilityBadge 
            eligible={
              eligibility.is_eligible 
                ? 'eligible' 
                : eligibility.missing_criteria && eligibility.missing_criteria.length > 5
                  ? 'not eligible'
                  : 'partially eligible'
            } 
          />
        )}
      </div>

      <h3 className="scheme-card-title">{scheme.name}</h3>

      {scheme.ministry && (
        <div className="scheme-card-meta-item">
          <Building size={14} className="meta-icon" />
          <span className="meta-text">{scheme.ministry}</span>
        </div>
      )}

      {scheme.description && (
        <p className="scheme-card-desc">{scheme.description}</p>
      )}

      {scheme.benefits && (
        <div className="scheme-card-benefits">
          <span className="benefits-label">Benefits:</span>
          <span className="benefits-text">{scheme.benefits}</span>
        </div>
      )}

      <div className="scheme-card-footer">
        <div className="scheme-card-meta-item">
          <MapPin size={14} className="meta-icon" />
          <span className="meta-text">{scheme.state || 'All India (Central)'}</span>
        </div>

        <Link to={`/scheme/${scheme.id}`} className="scheme-card-link" aria-label={`View details for ${scheme.name}`}>
          <span>View Details</span>
          <ArrowRight size={14} className="link-arrow-icon" />
        </Link>
      </div>
    </div>
  );
}
