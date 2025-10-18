import React from 'react';
import { Card } from '../common/Card';

interface ThreatGaugeProps {
  level: 'low' | 'medium' | 'high' | 'critical';
}

export const ThreatGauge: React.FC<ThreatGaugeProps> = ({ level }) => {
  const levels = [
    { name: 'Low', value: 'low', color: 'bg-severity-low' },
    { name: 'Medium', value: 'medium', color: 'bg-severity-medium' },
    { name: 'High', value: 'high', color: 'bg-severity-high' },
    { name: 'Critical', value: 'critical', color: 'bg-severity-critical' },
  ];

  const currentIndex = levels.findIndex((l) => l.value === level);

  return (
    <Card>
      <h3 className="text-lg font-semibold text-white mb-4">Threat Level</h3>
      <div className="flex flex-col items-center">
        <div className="text-5xl font-bold text-white mb-4">
          {levels[currentIndex].name}
        </div>
        <div className="w-full flex gap-2">
          {levels.map((l, index) => (
            <div
              key={l.value}
              className={`flex-1 h-3 rounded-full transition-all ${
                index <= currentIndex ? l.color : 'bg-dark-border'
              }`}
            />
          ))}
        </div>
        <p className="text-sm text-gray-400 mt-4 text-center">
          Based on average event scores in the last hour
        </p>
      </div>
    </Card>
  );
};
