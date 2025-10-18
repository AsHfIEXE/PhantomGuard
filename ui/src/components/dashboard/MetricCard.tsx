import React from 'react';
import { LucideIcon } from 'lucide-react';
import { Card } from '../common/Card';

interface MetricCardProps {
  title: string;
  value: number | string;
  icon: LucideIcon;
  iconColor?: string;
  subtitle?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  icon: Icon,
  iconColor = 'text-primary',
  subtitle,
}) => {
  return (
    <Card>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400 mb-1">{title}</p>
          <p className="text-3xl font-bold text-white">{value}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-lg bg-dark-elevated ${iconColor}`}>
          <Icon size={24} />
        </div>
      </div>
    </Card>
  );
};
