import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card } from '../common/Card';

interface TopDecoysChartProps {
  data: Array<{ name: string; count: number }>;
}

export const TopDecoysChart: React.FC<TopDecoysChartProps> = ({ data }) => {
  return (
    <Card>
      <h3 className="text-lg font-semibold text-white mb-4">Top Targeted Decoys</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2d3548" />
          <XAxis
            dataKey="name"
            stroke="#6b7280"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={100}
          />
          <YAxis stroke="#6b7280" tick={{ fill: '#9ca3af' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1a1f2e',
              border: '1px solid #2d3548',
              borderRadius: '8px',
              color: '#e5e7eb',
            }}
          />
          <Bar dataKey="count" fill="#3b82f6" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
};
