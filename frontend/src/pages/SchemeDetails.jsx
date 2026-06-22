/**
 * SchemeDetails — Full details page for a single scheme.
 *
 * Shows all scheme information including eligibility,
 * benefits, documents, and application process.
 */

import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { getSchemeDetails } from '../services/api';
import './SchemeDetails.css';

export default function SchemeDetails() {
  const { id } = useParams();
  const [scheme, setScheme] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchScheme() {
      try {
        const data = await getSchemeDetails(id);
        setScheme(data);
      } catch (err) {
        console.error('Failed to fetch scheme:', err);
      } finally {
        setIsLoading(false);
      }
    }
    fetchScheme();
  }, [id]);

  if (isLoading) {
    return <div className="scheme-details-loading">Loading scheme details...</div>;
  }

  if (!scheme) {
    return <div className="scheme-details-error">Scheme not found.</div>;
  }

  return (
    <div className="scheme-details" id="page-scheme-details">
      <div className="scheme-header">
        <div className="scheme-meta">
          {scheme.level && <span className="scheme-level">{scheme.level}</span>}
          {scheme.category && <span className="scheme-category">{scheme.category}</span>}
        </div>
        <h1 className="scheme-name">{scheme.name}</h1>
        {scheme.ministry && <p className="scheme-ministry">Ministry: {scheme.ministry}</p>}
      </div>

      {scheme.description && (
        <section className="scheme-section">
          <h2>Description</h2>
          <p>{scheme.description}</p>
        </section>
      )}

      {scheme.benefits && (
        <section className="scheme-section">
          <h2>Benefits</h2>
          <p>{scheme.benefits}</p>
        </section>
      )}

      {scheme.required_documents && scheme.required_documents.length > 0 && (
        <section className="scheme-section">
          <h2>Required Documents</h2>
          <ul className="document-list">
            {scheme.required_documents.map((doc, i) => (
              <li key={i}>{doc}</li>
            ))}
          </ul>
        </section>
      )}

      {scheme.application_process && (
        <section className="scheme-section">
          <h2>Application Process</h2>
          <p>{scheme.application_process}</p>
        </section>
      )}

      {scheme.official_url && (
        <a href={scheme.official_url} target="_blank" rel="noopener noreferrer" className="scheme-link">
          Visit Official Page →
        </a>
      )}
    </div>
  );
}
