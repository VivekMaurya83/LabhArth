import './LoadingSpinner.css';

/**
 * LoadingSpinner — Reusable CSS spinner with theme styling.
 */
export default function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="loading-spinner-container">
      <div className="loading-spinner"></div>
      {message && <p className="loading-spinner-message">{message}</p>}
    </div>
  );
}
