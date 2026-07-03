import { FileText } from 'lucide-react';
import './DocumentList.css';

/**
 * DocumentList — Renders a structured checklist of documents.
 *
 * Employs clean checklist rows and standardizes them using Lucide's FileText vector.
 */
export default function DocumentList({ documents }) {
  if (!documents || documents.length === 0) {
    return <p className="document-list-empty">No documents specified.</p>;
  }

  return (
    <ul className="document-list-checklist" id="document-list">
      {documents.map((doc, idx) => {
        let name = '';
        let isMandatory = true;
        let alternatives = [];

        // Parse document item
        if (typeof doc === 'string') {
          name = doc;
        } else if (doc && typeof doc === 'object') {
          name = doc.name || 'Unnamed Document';
          isMandatory = doc.mandatory !== false;
          alternatives = doc.alternatives || [];
        } else {
          return null;
        }

        return (
          <li key={idx} className={`document-item ${isMandatory ? 'document-item--mandatory' : 'document-item--optional'}`}>
            <div className="document-item-main">
              <FileText size={16} className="document-item-icon" aria-hidden="true" />
              <span className="document-item-name">{name}</span>
              {isMandatory ? (
                <span className="document-tag document-tag--mandatory">Required</span>
              ) : (
                <span className="document-tag document-tag--optional">Optional</span>
              )}
            </div>
            {alternatives.length > 0 && (
              <div className="document-item-alternatives">
                Alternatives: {alternatives.join(' OR ')}
              </div>
            )}
          </li>
        );
      })}
    </ul>
  );
}
