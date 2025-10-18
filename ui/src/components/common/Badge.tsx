import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant: 'low' | 'medium' | 'high' | 'critical' | 'info';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant, className = '' }) => {
  const variantStyles = {
    low: 'bg-severity-low/20 text-severity-low border-severity-low',
    medium: 'bg-severity-medium/20 text-severity-medium border-severity-medium',
    high: 'bg-severity-high/20 text-severity-high border-severity-high',
    critical: 'bg-severity-critical/20 text-severity-critical border-severity-critical',
    info: 'bg-primary/20 text-primary border-primary',
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
};
