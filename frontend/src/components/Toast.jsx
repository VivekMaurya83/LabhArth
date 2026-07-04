import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Info } from 'lucide-react';
import './Toast.css';

/**
 * Toast — Global overlay feedback notification.
 *
 * Listens to window-level custom events to display feedback alerts.
 */
export default function Toast() {
  const [toast, setToast] = useState(null);

  useEffect(() => {
    const handleShowToast = (e) => {
      setToast(e.detail || '');
    };

    window.addEventListener('show-toast', handleShowToast);
    return () => window.removeEventListener('show-toast', handleShowToast);
  }, []);

  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 2500);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  return (
    <AnimatePresence>
      {toast && (
        <motion.div
          className="toast-notification"
          initial={{ opacity: 0, y: 30, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 15, scale: 0.95 }}
          transition={{ duration: 0.25, ease: 'easeOut' }}
        >
          <Info size={16} className="toast-icon" />
          <span className="toast-message">{toast}</span>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/**
 * Helper utility to trigger a global toast message.
 * @param {string} message 
 */
export function showToast(message) {
  window.dispatchEvent(new CustomEvent('show-toast', { detail: message }));
}
