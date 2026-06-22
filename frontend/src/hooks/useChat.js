import { useState, useCallback, useRef } from 'react';
import { sendChatMessage } from '../services/api';

/**
 * useChat — Custom hook for managing chat state and communication.
 *
 * Handles message sending, loading states, session management,
 * and conversation history.
 */
export default function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const sessionIdRef = useRef(null);

  const sendMessage = useCallback(async (text) => {
    if (!text.trim()) return;

    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await sendChatMessage(text, sessionIdRef.current);
      sessionIdRef.current = response.session_id;

      // Add assistant response
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.response,
        agentName: response.agent_name,
        sources: response.sources,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearChat = useCallback(() => {
    setMessages([]);
    sessionIdRef.current = null;
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearChat,
    sessionId: sessionIdRef.current,
  };
}
