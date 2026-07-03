import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import ChatWindow from '../components/ChatWindow';
import ErrorBanner from '../components/ErrorBanner';
import useChat from '../hooks/useChat';
import './Chat.css';

/**
 * Chat — Conversational page wrapper.
 *
 * Receives preset search/chat triggers from the landing page.
 * Manages chat hook bindings and triggers error display banners.
 */
export default function Chat() {
  const location = useLocation();
  const { messages, isLoading, error, sendMessage, clearChat } = useChat();
  const initializedRef = useRef(false);

  // Check for preset query prompts passed from Home page links
  useEffect(() => {
    if (!initializedRef.current && location.state && location.state.presetPrompt) {
      initializedRef.current = true;
      const preset = location.state.presetPrompt;
      sendMessage(preset);
    }
  }, [location, sendMessage]);

  return (
    <div className="chat-page" id="page-chat">
      <div className="chat-container">
        {error && <ErrorBanner message={error} />}
        <ChatWindow
          messages={messages}
          onSendMessage={sendMessage}
          onClearChat={clearChat}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}
