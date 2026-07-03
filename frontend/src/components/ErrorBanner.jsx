import { useState } from 'react';
import { AlertCircle, X } from 'lucide-react';
import './ErrorBanner.css';

/**
 * ErrorBanner — Reusable dismissable error display component.
 *
 * Uses Lucide vector icons for professional feedback.
 */
export default function ErrorBanner({ message, onDismiss }) {
  const [visible, setVisible] = useState(true);

  if (!message || !visible) return null;

  const handleDismiss = () => {
    setVisible(false);
    if (onDismiss) onDismiss();
  };

  return (
    <div className="error-banner" id="error-banner">
      <AlertCircle size={16} className="error-banner-icon" aria-hidden="true" />
      <div className="error-banner-content">
        <p className="error-banner-text">{message}</p>
      </div>
      <button type="button" className="error-banner-close" onClick={handleDismiss} aria-label="Dismiss error">
        <X size={14} />
      </button>
    </div>
  );
}
