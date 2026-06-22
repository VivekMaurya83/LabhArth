/**
 * Home — Landing page for LabhArth AI.
 *
 * Hero section with value proposition and quick-action cards
 * directing users to Search, Chat, or Eligibility features.
 */

import { Link } from 'react-router-dom';
import './Home.css';

export default function Home() {
  return (
    <div className="home" id="page-home">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-badge">🇮🇳 AI-Powered Government Scheme Discovery</div>
        <h1 className="hero-title">
          Discover <span className="gradient-text">Government Schemes</span> You Deserve
        </h1>
        <p className="hero-subtitle">
          LabhArth AI helps Indian citizens find relevant welfare schemes,
          check eligibility, and navigate the application process — all through
          an intelligent AI assistant.
        </p>
        <div className="hero-actions">
          <Link to="/chat" className="btn btn-primary" id="cta-chat">
            💬 Talk to AI Assistant
          </Link>
          <Link to="/search" className="btn btn-secondary" id="cta-search">
            🔍 Browse Schemes
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="features">
        <div className="feature-card" id="feature-discover">
          <div className="feature-icon">🔍</div>
          <h3>Scheme Discovery</h3>
          <p>Search 500+ central and state government welfare schemes with AI-powered semantic search.</p>
        </div>
        <div className="feature-card" id="feature-eligibility">
          <div className="feature-icon">✅</div>
          <h3>Eligibility Check</h3>
          <p>Instantly know if you qualify for a scheme based on your profile — with clear reasoning.</p>
        </div>
        <div className="feature-card" id="feature-guidance">
          <div className="feature-icon">📋</div>
          <h3>Application Guide</h3>
          <p>Get step-by-step guidance on required documents and the application process.</p>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="tech-section">
        <h2 className="section-title">Powered By</h2>
        <div className="tech-badges">
          <span className="tech-badge">Gemini 2.5 Flash</span>
          <span className="tech-badge">Google ADK</span>
          <span className="tech-badge">Agentic RAG</span>
          <span className="tech-badge">MCP</span>
          <span className="tech-badge">Multi-Agent AI</span>
        </div>
      </section>
    </div>
  );
}
