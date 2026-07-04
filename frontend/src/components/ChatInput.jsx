import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, X, Mic } from 'lucide-react';
import './ChatInput.css';

/**
 * ChatInput — Text entry component with voice recognition capabilities.
 */
export default function ChatInput({ onSendMessage, disabled, placeholder = 'Ask about government schemes...' }) {
  const [text, setText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  useEffect(() => {
    // Cleanup speech recognition on unmount
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim() && !disabled) {
      onSendMessage(text.trim());
      setText('');
    }
  };

  const handleClear = () => {
    setText('');
  };

  const startListening = () => {
    if (!SpeechRecognition) {
      window.dispatchEvent(new CustomEvent('show-toast', { detail: 'Speech input not supported on this browser.' }));
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-IN'; // Supports English with local Indian dialect phrasing

    recognition.onstart = () => {
      setIsListening(true);
      window.dispatchEvent(new CustomEvent('show-toast', { detail: 'Listening... Speak now.' }));
    };

    recognition.onerror = (e) => {
      console.error('Speech recognition error', e);
      setIsListening(false);
      window.dispatchEvent(new CustomEvent('show-toast', { detail: 'Speech error. Try again.' }));
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      setText(prev => {
        const spacing = prev.trim() ? ' ' : '';
        return prev.trim() + spacing + transcript;
      });
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  return (
    <form className="chat-input-container" onSubmit={handleSubmit}>
      <div className="chat-input-wrapper">
        <input
          type="text"
          className="chat-input-text"
          id="chat-input-text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={isListening ? 'Listening...' : placeholder}
          disabled={disabled}
          maxLength={400}
          autoComplete="off"
          required
        />
        <AnimatePresence>
          {text && !disabled && (
            <motion.button
              type="button"
              className="chat-input-clear-btn"
              onClick={handleClear}
              aria-label="Clear text input"
              title="Clear text input"
              initial={{ scale: 0, rotate: -45, opacity: 0 }}
              animate={{ scale: 1, rotate: 0, opacity: 1 }}
              exit={{ scale: 0, rotate: 45, opacity: 0 }}
              whileHover={{ scale: 1.15, rotate: 90 }}
              whileTap={{ scale: 0.85 }}
              transition={{ type: 'spring', stiffness: 350, damping: 18 }}
            >
              <X size={16} />
            </motion.button>
          )}
        </AnimatePresence>

        <button
          type="button"
          className={`chat-input-mic-btn ${isListening ? 'chat-input-mic-btn--listening' : ''}`}
          onClick={toggleListening}
          disabled={disabled}
          title={isListening ? 'Stop listening' : 'Start voice input'}
          aria-label={isListening ? 'Stop listening' : 'Start voice input'}
        >
          <Mic size={16} />
        </button>
      </div>
      <button
        type="submit"
        className="chat-input-send-btn"
        id="chat-input-submit"
        disabled={disabled || !text.trim() || isListening}
        aria-label="Send message"
      >
        <span>Send</span>
        <Send size={14} className="send-icon" aria-hidden="true" />
      </button>
    </form>
  );
}
