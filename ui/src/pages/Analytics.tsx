import React, { useEffect, useState } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card } from '../components/common/Card';
import type { Event } from '../types';
import { eventsApi } from '../services/api';
import { generateMockEvents } from '../utils/mockData';
import { format } from 'date-fns';

export const Analytics: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d'>('7d');

  const loadEvents = async () => {
    try {
      const data = await eventsApi.getAll({ timeRange }, undefined, 1000);

      if (data.length === 0) {
        setEvents(generateMockEvents(100));
      } else {
        setEvents(data);
      }
    } catch (error) {
      console.error('Failed to load events:', error);
      setEvents(generateMockEvents(100));
    }
  };

  useEffect(() => {
    loadEvents();
  }, [timeRange]);

  const timeSeriesData = React.useMemo(() => {
    const grouped = new Map<string, { count: number; totalScore: number }>();

    events.forEach((event) => {
      const date = format(new Date(event.timestamp), 'MMM dd');
      const existing = grouped.get(date) || { count: 0, totalScore: 0 };
      grouped.set(date, {
        count: existing.count + 1,
        totalScore: existing.totalScore + event.score,
      });
    });

    return Array.from(grouped.entries()).map(([date, data]) => ({
      date,
      count: data.count,
      avgScore: data.count > 0 ? data.totalScore / data.count : 0,
    }));
  }, [events]);

  const scoreDistribution = React.useMemo(() => {
    const ranges = [
      { name: '0-20', min: 0, max: 20, count: 0 },
      { name: '20-40', min: 20, max: 40, count: 0 },
      { name: '40-60', min: 40, max: 60, count: 0 },
      { name: '60-80', min: 60, max: 80, count: 0 },
      { name: '80-100', min: 80, max: 100, count: 0 },
    ];

    events.forEach((event) => {
      const range = ranges.find((r) => event.score >= r.min && event.score < r.max);
      if (range) range.count++;
    });

    return ranges;
  }, [events]);

  const topSourceIPs = React.useMemo(() => {
    const ipMap = new Map<string, { count: number; totalScore: number }>();

    events.forEach((event) => {
      if (!event.source_ip) return;
      const existing = ipMap.get(event.source_ip) || { count: 0, totalScore: 0 };
      ipMap.set(event.source_ip, {
        count: existing.count + 1,
        totalScore: existing.totalScore + event.score,
      });
    });

    return Array.from(ipMap.entries())
      .map(([ip, data]) => ({
        ip,
        count: data.count,
        avgScore: data.totalScore / data.count,
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);
  }, [events]);

  const decoyEffectiveness = React.useMemo(() => {
    const decoyMap = new Map<string, number>();

    events.forEach((event) => {
      const path = event.decoy_path.split('/').pop() || event.decoy_path;
      decoyMap.set(path, (decoyMap.get(path) || 0) + 1);
    });

    return Array.from(decoyMap.entries())
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);
  }, [events]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">Analytics</h2>
          <p className="text-gray-400">Advanced threat intelligence and patterns</p>
        </div>

        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value as any)}
          className="px-4 py-2 bg-dark-surface border border-dark-border rounded-lg text-white focus:outline-none focus:border-primary"
        >
          <option value="24h">Last 24 Hours</option>
          <option value="7d">Last 7 Days</option>
          <option value="30d">Last 30 Days</option>
        </select>
      </div>

      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Events Over Time</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={timeSeriesData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2d3548" />
            <XAxis dataKey="date" stroke="#6b7280" tick={{ fill: '#9ca3af' }} />
            <YAxis stroke="#6b7280" tick={{ fill: '#9ca3af' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1a1f2e',
                border: '1px solid #2d3548',
                borderRadius: '8px',
                color: '#e5e7eb',
              }}
            />
            <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-lg font-semibold text-white mb-4">Score Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={scoreDistribution}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d3548" />
              <XAxis dataKey="name" stroke="#6b7280" tick={{ fill: '#9ca3af' }} />
              <YAxis stroke="#6b7280" tick={{ fill: '#9ca3af' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1f2e',
                  border: '1px solid #2d3548',
                  borderRadius: '8px',
                  color: '#e5e7eb',
                }}
              />
              <Bar dataKey="count" fill="#10b981" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <h3 className="text-lg font-semibold text-white mb-4">Decoy Effectiveness</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={decoyEffectiveness}>
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
              <Bar dataKey="count" fill="#f59e0b" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Top Source IPs</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-dark-border">
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">IP Address</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Event Count</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Avg Score</th>
              </tr>
            </thead>
            <tbody>
              {topSourceIPs.map((item, index) => (
                <tr key={index} className="border-b border-dark-border">
                  <td className="py-3 px-4 text-sm text-white font-mono">{item.ip}</td>
                  <td className="py-3 px-4 text-sm text-gray-300">{item.count}</td>
                  <td className="py-3 px-4 text-sm text-gray-300">{item.avgScore.toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
