/**
 * ChatWindow — Conversational AI interface component.
 *
 * Displays chat messages and provides input for user interaction.
 * Used on the Chat page with the useChat hook.
 */

import { useState, useRef, useEffect } from 'react';
import './ChatWindow.css';

export default function ChatWindow({ messages, onSendMessage, isLoading }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  return (
    <div className="chat-window" id="chat-window">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-welcome">
            <span className="chat-welcome-icon">🇮🇳</span>
            <h3>Welcome to LabhArth AI</h3>
            <p>Ask me about government welfare schemes, eligibility, or required documents.</p>
          </div>
        )}
        {messages.map((msg) => (
          <div key={msg.id} className={`chat-message chat-message--${msg.role}`}>
            <div className="chat-message-content">{msg.content}</div>
            {msg.agentName && (
              <span className="chat-message-agent">via {msg.agentName}</span>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="chat-message chat-message--assistant">
            <div className="chat-typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chat-input"
          id="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about government schemes..."
          disabled={isLoading}
          autoFocus
        />
        <button type="submit" className="chat-send-btn" id="chat-send" disabled={isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
