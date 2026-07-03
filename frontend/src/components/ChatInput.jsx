import { useState } from 'react';
import { Send } from 'lucide-react';
import './ChatInput.css';

/**
 * ChatInput — Reusable text entry component for sending chat assistant queries.
 */
export default function ChatInput({ onSendMessage, disabled, placeholder = 'Ask about government schemes...' }) {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim() && !disabled) {
      onSendMessage(text.trim());
      setText('');
    }
  };

  return (
    <form className="chat-input-container" onSubmit={handleSubmit}>
      <input
        type="text"
        className="chat-input-text"
        id="chat-input-text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        maxLength={400}
        autoComplete="off"
        required
      />
      <button
        type="submit"
        className="chat-input-send-btn"
        id="chat-input-submit"
        disabled={disabled || !text.trim()}
        aria-label="Send message"
      >
        <span>Send</span>
        <Send size={14} className="send-icon" aria-hidden="true" />
      </button>
    </form>
  );
}
