import './Footer.css';

/**
 * Footer — Application footer with project info.
 */
export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer" id="footer">
      <div className="footer-container">
        <p className="footer-text">
          <strong>LabhArth AI</strong> — Empowering citizens through AI-driven welfare scheme discovery
        </p>
        <p className="footer-sub">
          &copy; {currentYear} LabhArth AI · Powered by Gemini & Google ADK
        </p>
      </div>
    </footer>
  );
}
