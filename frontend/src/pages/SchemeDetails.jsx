import { useParams, Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { ArrowLeft, ExternalLink, MapPin, Building, Check } from 'lucide-react';
import { getSchemeDetails, checkEligibility } from '../services/api';
import EligibilityForm from '../components/EligibilityForm';
import EligibilityBadge from '../components/EligibilityBadge';
import DocumentList from '../components/DocumentList';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';
import './SchemeDetails.css';

/**
 * SchemeDetails — Detailed scheme specs.
 *
 * Shows full scheme metadata and lets the user test their personal profile criteria
 * in real-time against this specific scheme.
 */
export default function SchemeDetails() {
  const { id } = useParams();
  const [scheme, setScheme] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Single eligibility evaluation states
  const [evalResult, setEvalResult] = useState(null);
  const [isChecking, setIsChecking] = useState(false);
  const [evalError, setEvalError] = useState(null);

  useEffect(() => {
    async function fetchScheme() {
      setIsLoading(true);
      setError(null);
      setEvalResult(null); // Reset prior checks
      try {
        const data = await getSchemeDetails(id);
        setScheme(data);
      } catch (err) {
        console.error('Failed to fetch scheme:', err);
        setError(err.message || 'Failed to load scheme details. Verify the backend is running.');
      } finally {
        setIsLoading(false);
      }
    }
    fetchScheme();
  }, [id]);

  const handleCheckSingleEligibility = async (profile) => {
    setIsChecking(true);
    setEvalError(null);
    setEvalResult(null);
    try {
      const result = await checkEligibility(scheme.id, profile);
      setEvalResult(result);
    } catch (err) {
      console.error('Single eligibility check failed:', err);
      setEvalError(err.message || 'Error occurred during eligibility evaluation. Please try again.');
    } finally {
      setIsChecking(false);
    }
  };

  if (isLoading) {
    return <LoadingSpinner message="Fetching detailed scheme metadata from database..." />;
  }

  if (error) {
    return (
      <div className="scheme-details-error-page">
        <ErrorBanner message={error} />
        <Link to="/search" className="back-link">
          <ArrowLeft size={14} />
          <span>Return to Catalog</span>
        </Link>
      </div>
    );
  }

  if (!scheme) {
    return (
      <div className="scheme-details-empty">
        <p>Scheme record not found.</p>
        <Link to="/search" className="back-link">
          <ArrowLeft size={14} />
          <span>Return to Catalog</span>
        </Link>
      </div>
    );
  }

  return (
    <div className="scheme-details-container" id="page-scheme-details">
      <Link to="/search" className="back-link-top">
        <ArrowLeft size={14} />
        <span>Back to Catalog</span>
      </Link>

      <div className="scheme-details-grid">
        {/* Main Details Panel */}
        <div className="scheme-details-main">
          <div className="scheme-header">
            <div className="scheme-meta">
              {scheme.level && <span className="scheme-level">{scheme.level}</span>}
              {scheme.category && <span className="scheme-category">{scheme.category.replace(/_/g, ' ')}</span>}
              {scheme.state && (
                <span className="scheme-state-badge">
                  <MapPin size={12} className="inline-meta-icon" />
                  <span>{scheme.state}</span>
                </span>
              )}
            </div>
            <h1 className="scheme-name">{scheme.name}</h1>
            {scheme.ministry && (
              <p className="scheme-ministry">
                <Building size={14} className="inline-meta-icon" />
                <span>{scheme.ministry}</span>
              </p>
            )}
          </div>

          {scheme.description && (
            <section className="scheme-section">
              <h2>Description</h2>
              <p className="scheme-section-text">{scheme.description}</p>
            </section>
          )}

          {scheme.eligibility_criteria && (
            <section className="scheme-section">
              <h2>Eligibility Rules</h2>
              {typeof scheme.eligibility_criteria === 'object' ? (
                <div className="eligibility-criteria-block">
                  {scheme.eligibility_criteria.raw_text && (
                    <p className="scheme-section-text" style={{ whiteSpace: 'pre-wrap' }}>
                      {scheme.eligibility_criteria.raw_text}
                    </p>
                  )}
                  {scheme.eligibility_criteria.additional_notes && (
                    <div className="eligibility-additional-notes" style={{ marginTop: 'var(--space-md)' }}>
                      <strong style={{ color: 'var(--color-primary)', display: 'block', marginBottom: 'var(--space-xs)' }}>
                        Additional Notes:
                      </strong>
                      <p className="scheme-section-text" style={{ whiteSpace: 'pre-wrap' }}>
                        {scheme.eligibility_criteria.additional_notes}
                      </p>
                    </div>
                  )}
                  {!scheme.eligibility_criteria.raw_text && !scheme.eligibility_criteria.additional_notes && (
                    <ul className="eligibility-criteria-list">
                      {Object.entries(scheme.eligibility_criteria).map(([key, val]) => {
                        const formattedKey = key
                          .replace(/_/g, ' ')
                          .replace(/\b\w/g, c => c.toUpperCase());
                        let formattedVal = String(val);
                        if (val === true) formattedVal = 'Yes';
                        if (val === false) formattedVal = 'No';
                        return (
                          <li key={key} className="criteria-list-item">
                            <strong>{formattedKey}:</strong> {formattedVal}
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </div>
              ) : (
                <p className="scheme-section-text" style={{ whiteSpace: 'pre-wrap' }}>
                  {scheme.eligibility_criteria}
                </p>
              )}
            </section>
          )}

          {scheme.benefits && (
            <section className="scheme-section">
              <h2>Benefits Offered</h2>
              <p className="scheme-section-text">{scheme.benefits}</p>
            </section>
          )}

          {scheme.required_documents && scheme.required_documents.length > 0 && (
            <section className="scheme-section">
              <h2>Documents Required</h2>
              <DocumentList documents={scheme.required_documents} />
            </section>
          )}

          {scheme.application_process && (
            <section className="scheme-section">
              <h2>How to Apply</h2>
              <p className="scheme-section-text">{scheme.application_process}</p>
            </section>
          )}

          {scheme.official_url && (
            <a href={scheme.official_url} target="_blank" rel="noopener noreferrer" className="scheme-link">
              <span>Visit Official Government Portal</span>
              <ExternalLink size={14} />
            </a>
          )}
        </div>

        {/* Sidebar Interactive Eligibility Panel */}
        <div className="scheme-details-sidebar">
          <div className="eligibility-evalulator-card">
            <h2>Check Your Eligibility</h2>
            <p className="evaluator-card-subtitle">
              Input your details below to evaluate if you qualify for this specific initiative.
            </p>

            {evalError && <ErrorBanner message={evalError} onDismiss={() => setEvalError(null)} />}

            {/* Eligibility Report */}
            {evalResult && (
              <div className="single-eligibility-report">
                <div className="report-badge-row">
                  <span className="report-badge-label">Your Status:</span>
                  <EligibilityBadge 
                    eligible={
                      evalResult.is_eligible 
                        ? 'eligible' 
                        : evalResult.missing_criteria && evalResult.missing_criteria.length > 3
                          ? 'not eligible'
                          : 'partially eligible'
                    } 
                  />
                </div>
                <div className="report-details">
                  <p className="report-reasoning">
                    <strong>Evaluation Reasoning:</strong> {evalResult.reasoning}
                  </p>
                  {evalResult.missing_criteria && evalResult.missing_criteria.length > 0 && (
                    <div className="report-missing-criteria">
                      <strong>Missing Requirements:</strong>
                      <ul>
                        {evalResult.missing_criteria.map((crit, idx) => (
                          <li key={idx}>{crit}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {evalResult.is_eligible && evalResult.required_documents && evalResult.required_documents.length > 0 && (
                    <div className="report-documents-checklist">
                      <strong>Verified Checklist:</strong>
                      <ul className="docs-sub-list">
                        {evalResult.required_documents.map((doc, idx) => (
                          <li key={idx}>
                            <Check size={12} className="verified-check-icon" />
                            <span>{doc}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
                <button
                  type="button"
                  className="re-eval-btn"
                  onClick={() => setEvalResult(null)}
                >
                  Edit Profile & Re-check
                </button>
              </div>
            )}

            {!evalResult && (
              <EligibilityForm
                onSubmit={handleCheckSingleEligibility}
                isLoading={isChecking}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
