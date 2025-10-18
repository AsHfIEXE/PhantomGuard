import React, { useEffect } from 'react';
import { AlertTriangle, CheckCircle, Info, X } from 'lucide-react';

interface ToastProps {
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  onClose: () => void;
  duration?: number;
}

export const Toast: React.FC<ToastProps> = ({ message, type, onClose, duration = 5000 }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const icons = {
    success: <CheckCircle size={20} className="text-success" />,
    error: <AlertTriangle size={20} className="text-danger" />,
    warning: <AlertTriangle size={20} className="text-warning" />,
    info: <Info size={20} className="text-primary" />,
  };

  const styles = {
    success: 'border-success bg-success/10',
    error: 'border-danger bg-danger/10',
    warning: 'border-warning bg-warning/10',
    info: 'border-primary bg-primary/10',
  };

  return (
    <div
      className={`flex items-center gap-3 px-4 py-3 rounded-lg border ${styles[type]} shadow-lg min-w-[300px] max-w-md animate-slideIn`}
    >
      {icons[type]}
      <p className="flex-1 text-sm text-gray-200">{message}</p>
      <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
        <X size={16} />
      </button>
    </div>
  );
};

interface ToastContainerProps {
  toasts: Array<{ id: string; message: string; type: 'success' | 'error' | 'warning' | 'info' }>;
  onRemove: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onRemove }) => {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          onClose={() => onRemove(toast.id)}
        />
      ))}
    </div>
  );
};
