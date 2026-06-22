import './Footer.css';

/**
 * Footer — Application footer with project info.
 */
export default function Footer() {
  return (
    <footer className="footer" id="footer">
      <div className="footer-container">
        <p className="footer-text">
          <strong>LabhArth AI</strong> — Empowering citizens through AI-driven welfare scheme discovery
        </p>
        <p className="footer-sub">
          Built for Kaggle AI Agents Capstone · Powered by Gemini & Google ADK
        </p>
      </div>
    </footer>
  );
}
