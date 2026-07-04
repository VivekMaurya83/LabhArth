import { useState } from 'react';
import { Link } from 'react-router-dom';
import { User, Sparkles, Copy, Check, Search } from 'lucide-react';
import './MessageBubble.css';

/**
 * MessageBubble — Renders an individual message in a chat thread.
 *
 * Employs clean vector icons and styles text with markdown formatting tags.
 */
export default function MessageBubble({ message }) {
  const { role, content, agentName, sources, timestamp } = message;
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    window.dispatchEvent(new CustomEvent('show-toast', { detail: 'Copied message content to clipboard!' }));
    setTimeout(() => setCopied(false), 2000);
  };

  // Helper to format basic markdown (bold, lists, paragraphs)
  const formatMessageText = (text) => {
    if (!text) return '';

    // Split text into paragraphs
    const paragraphs = text.split(/\n\n+/);

    return paragraphs.map((para, pIdx) => {
      // Check if paragraph is a bulleted list
      if (para.trim().startsWith('- ') || para.trim().startsWith('* ')) {
        const listItems = para
          .split(/\n[*-]\s+/)
          .map(item => item.replace(/^[*-]\s+/, '').trim())
          .filter(item => item.length > 0);

        return (
          <ul key={pIdx} className="message-list">
            {listItems.map((item, lIdx) => (
              <li key={lIdx} dangerouslySetInnerHTML={{ __html: parseInlineStyles(item) }} />
            ))}
          </ul>
        );
      }

      // Check if paragraph is a numbered list
      if (/^\d+\.\s+/.test(para.trim())) {
        const listItems = para
          .split(/\n\d+\.\s+/)
          .map(item => item.replace(/^\d+\.\s+/, '').trim())
          .filter(item => item.length > 0);

        return (
          <ol key={pIdx} className="message-list-ordered">
            {listItems.map((item, lIdx) => (
              <li key={lIdx} dangerouslySetInnerHTML={{ __html: parseInlineStyles(item) }} />
            ))}
          </ol>
        );
      }

      // Standard paragraph
      return (
        <p
          key={pIdx}
          className="message-paragraph"
          dangerouslySetInnerHTML={{ __html: parseInlineStyles(para) }}
        />
      );
    });
  };

  // Helper to parse bold text (**text**) and clean inline markdown
  const parseInlineStyles = (text) => {
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      // Bold syntax
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Inline code
      .replace(/`(.*?)`/g, '<code class="inline-code">$1</code>');
    
    return html;
  };

  const formattedTime = timestamp
    ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : '';

  return (
    <div className={`message-bubble-wrapper message-bubble-wrapper--${role}`}>
      <div className="message-avatar">
        {role === 'user' ? <User size={18} /> : <Sparkles size={18} className="ai-avatar-icon" />}
      </div>
      <div className="message-bubble-container">
        <div className={`message-bubble message-bubble--${role}`}>
          <div className="message-content">
            {formatMessageText(content)}
          </div>

          <div className="message-meta-footer">
            <div className="message-info">
              {formattedTime && <span className="message-time">{formattedTime}</span>}
            </div>

            <button
              type="button"
              className="message-copy-btn"
              onClick={handleCopy}
              title="Copy message text"
            >
              {copied ? (
                <>
                  <Check size={12} className="copy-icon" />
                  <span>Copied</span>
                </>
              ) : (
                <>
                  <Copy size={12} className="copy-icon" />
                  <span>Copy</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Citations / Sources */}
        {role === 'assistant' && sources && sources.length > 0 && (
          <div className="message-sources">
            <span className="sources-title">Referenced Schemes:</span>
            <div className="sources-list">
              {sources.map((src, idx) => {
                if (src && src.id) {
                  return (
                    <Link key={idx} to={`/scheme/${src.id}`} className="source-link">
                      <Search size={11} className="source-icon" />
                      <span>{src.name || 'View Scheme'}</span>
                    </Link>
                  );
                }
                return null;
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
