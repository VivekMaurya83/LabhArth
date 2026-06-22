/**
 * Chat — AI Assistant chat page.
 *
 * Full-screen chat interface using the ChatWindow component
 * and useChat hook for state management.
 */

import ChatWindow from '../components/ChatWindow';
import useChat from '../hooks/useChat';
import './Chat.css';

export default function Chat() {
  const { messages, isLoading, error, sendMessage } = useChat();

  return (
    <div className="chat-page" id="page-chat">
      <ChatWindow
        messages={messages}
        onSendMessage={sendMessage}
        isLoading={isLoading}
      />
      {error && <div className="chat-error">⚠️ {error}</div>}
    </div>
  );
}
