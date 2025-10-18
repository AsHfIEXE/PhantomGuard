import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  elevated?: boolean;
}

export const Card: React.FC<CardProps> = ({ children, className = '', elevated = false }) => {
  return (
    <div
      className={`rounded-lg ${
        elevated ? 'bg-dark-elevated' : 'bg-dark-surface'
      } border border-dark-border p-6 ${className}`}
    >
      {children}
    </div>
  );
};
