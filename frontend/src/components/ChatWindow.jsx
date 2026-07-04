import { useRef, useEffect } from 'react';
import { Trash2, Sparkles, MessageSquare, Shield } from 'lucide-react';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import './ChatWindow.css';

/**
 * ChatWindow — Main assistant chat window interface.
 *
 * Employs clean vector icons and structures layout grids.
 */
export default function ChatWindow({ messages, onSendMessage, onClearChat, isLoading }) {
  const chatMessagesRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  return (
    <div className="chat-window" id="chat-window">
      {/* Chat Header */}
      <div className="chat-header">
        <div className="chat-header-info">
          <span className="chat-header-status">●</span>
          <h3 className="chat-header-title">LabhArth Welfare Assistant</h3>
        </div>
        {messages.length > 0 && (
          <button
            type="button"
            className="chat-clear-btn"
            id="chat-clear"
            onClick={onClearChat}
            title="Clear conversation history"
          >
            <Trash2 size={13} className="clear-icon" />
            <span>Clear History</span>
          </button>
        )}
      </div>

      {/* Messages Scroll Area */}
      <div className="chat-messages" ref={chatMessagesRef}>
        {messages.length === 0 && (
          <div className="chat-welcome">
            <div className="chat-welcome-avatar">
              <Sparkles size={32} className="chat-welcome-logo" />
            </div>
            <h3>Welfare Scheme Assistant</h3>
            <p className="chat-welcome-subtitle">
              Ask about eligibility criteria, required documents, or search for state and central government initiatives.
            </p>
            <div className="chat-welcome-tips">
              <span className="tip-badge">
                <Shield size={11} className="tip-badge-icon" />
                <span>Example Inquiries</span>
              </span>
              <ul className="tip-list">
                <li onClick={() => onSendMessage("What scholarship schemes exist for girl students in Maharashtra?")} className="tip-clickable-item">
                  <MessageSquare size={12} className="tip-icon" />
                  <span>"What scholarship schemes exist for girl students in Maharashtra?"</span>
                </li>
                <li onClick={() => onSendMessage("Are there subsidies available for purchasing seeds or farming tools?")} className="tip-clickable-item">
                  <MessageSquare size={12} className="tip-icon" />
                  <span>"Are there subsidies available for purchasing seeds or farming tools?"</span>
                </li>
                <li onClick={() => onSendMessage("Show me details for Mahatma Jyotirao Phule Jan Arogya Yojana.")} className="tip-clickable-item">
                  <MessageSquare size={12} className="tip-icon" />
                  <span>"Show me details for Mahatma Jyotirao Phule Jan Arogya Yojana."</span>
                </li>
              </ul>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {isLoading && (
          <div className="chat-message-typing-bubble">
            <div className="message-avatar">
              <Sparkles size={16} className="ai-avatar-icon" />
            </div>
            <div className="chat-typing-container">
              <span className="chat-typing-status">Scanning government scheme catalog...</span>
              <div className="chat-typing">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Form */}
      <ChatInput onSendMessage={onSendMessage} disabled={isLoading} />
    </div>
  );
}
