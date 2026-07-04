import { useState, useEffect } from 'react';
import { FileText, CheckSquare, Square } from 'lucide-react';
import './DocumentList.css';

/**
 * DocumentList — Renders an interactive checklist of documents.
 *
 * Persists checked state in localStorage for each scheme and tracks preparation progress.
 */
export default function DocumentList({ documents, schemeId }) {
  const [checkedItems, setCheckedItems] = useState({});

  // Load checked items from localStorage when component mounts or scheme changes
  useEffect(() => {
    if (schemeId) {
      const saved = localStorage.getItem(`docs-checked-${schemeId}`);
      if (saved) {
        try {
          setCheckedItems(JSON.parse(saved));
        } catch (e) {
          console.error('Failed to parse document checked states', e);
        }
      } else {
        setCheckedItems({});
      }
    }
  }, [schemeId]);

  if (!documents || documents.length === 0) {
    return <p className="document-list-empty">No documents specified.</p>;
  }

  // Handle toggling checkbox state
  const handleToggle = (index) => {
    const nextState = {
      ...checkedItems,
      [index]: !checkedItems[index],
    };
    setCheckedItems(nextState);
    if (schemeId) {
      localStorage.setItem(`docs-checked-${schemeId}`, JSON.stringify(nextState));
    }
  };

  const parsedDocs = documents.map((doc, idx) => {
    let name = '';
    let isMandatory = true;
    let alternatives = [];

    if (typeof doc === 'string') {
      name = doc;
    } else if (doc && typeof doc === 'object') {
      name = doc.name || 'Unnamed Document';
      isMandatory = doc.mandatory !== false;
      alternatives = doc.alternatives || [];
    }
    return { name, isMandatory, alternatives, originalIndex: idx };
  });

  const totalCount = parsedDocs.length;
  const checkedCount = parsedDocs.filter(d => checkedItems[d.originalIndex]).length;
  const percent = totalCount > 0 ? Math.round((checkedCount / totalCount) * 100) : 0;

  return (
    <div className="document-list-wrapper">
      {/* Dynamic Readiness Progress Bar */}
      <div className="document-progress-container">
        <div className="document-progress-info">
          <span className="progress-label">Document Readiness: {percent}%</span>
          <span className="progress-status">{checkedCount} of {totalCount} prepared</span>
        </div>
        <div className="document-progress-bar-bg">
          <div 
            className="document-progress-bar-fill" 
            style={{ width: `${percent}%` }}
          ></div>
        </div>
      </div>

      <ul className="document-list-checklist" id="document-list">
        {parsedDocs.map((doc) => {
          const isChecked = !!checkedItems[doc.originalIndex];

          return (
            <li 
              key={doc.originalIndex} 
              onClick={() => handleToggle(doc.originalIndex)}
              className={`document-item ${doc.isMandatory ? 'document-item--mandatory' : 'document-item--optional'} ${isChecked ? 'document-item--checked' : ''}`}
              style={{ cursor: 'pointer' }}
            >
              <div className="document-item-main">
                {isChecked ? (
                  <CheckSquare size={18} className="checkbox-icon checkbox-icon--checked" />
                ) : (
                  <Square size={18} className="checkbox-icon checkbox-icon--unchecked" />
                )}
                <span className="document-item-name">{doc.name}</span>
                {doc.isMandatory ? (
                  <span className="document-tag document-tag--mandatory">Required</span>
                ) : (
                  <span className="document-tag document-tag--optional">Optional</span>
                )}
              </div>
              {doc.alternatives.length > 0 && (
                <div className="document-item-alternatives">
                  Alternatives: {doc.alternatives.join(' OR ')}
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
