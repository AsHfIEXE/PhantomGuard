import React, { useEffect } from 'react';
import { Activity, Bell, Shield, Layers } from 'lucide-react';
import { MetricCard } from '../components/dashboard/MetricCard';
import { EventTimeline } from '../components/dashboard/EventTimeline';
import { ThreatGauge } from '../components/dashboard/ThreatGauge';
import { TopDecoysChart } from '../components/dashboard/TopDecoysChart';
import { useStore } from '../store/useStore';
import { systemApi, eventsApi } from '../services/api';
import { usePolling } from '../hooks/usePolling';
import { generateMockEvents, generateMockDecoys } from '../utils/mockData';

export const Dashboard: React.FC = () => {
  const { metrics, setMetrics, events, setEvents } = useStore();

  const loadData = async () => {
    try {
      const [metricsData, recentEvents] = await Promise.all([
        systemApi.getMetrics(),
        eventsApi.getRecent(10),
      ]);

      setMetrics(metricsData);

      if (recentEvents.length === 0) {
        const mockEvents = generateMockEvents(10);
        setEvents(mockEvents);
      } else {
        setEvents(recentEvents);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      const mockEvents = generateMockEvents(10);
      setEvents(mockEvents);
      setMetrics({
        totalEvents: mockEvents.length,
        totalEventsToday: Math.floor(mockEvents.length / 2),
        alertsTriggered: mockEvents.filter(e => e.score >= 60).length,
        ipsBlocked: 3,
        activeDecoys: 5,
        threatLevel: 'medium',
      });
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  usePolling(loadData, 5000);

  const decoyStats = React.useMemo(() => {
    const decoyMap = new Map<string, number>();
    events.forEach((event) => {
      const path = event.decoy_path.split('/').pop() || event.decoy_path;
      decoyMap.set(path, (decoyMap.get(path) || 0) + 1);
    });

    return Array.from(decoyMap.entries())
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);
  }, [events]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Dashboard</h2>
        <p className="text-gray-400">Real-time threat monitoring and system overview</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Events"
          value={metrics?.totalEvents || 0}
          subtitle={`${metrics?.totalEventsToday || 0} today`}
          icon={Activity}
          iconColor="text-primary"
        />
        <MetricCard
          title="Alerts Triggered"
          value={metrics?.alertsTriggered || 0}
          icon={Bell}
          iconColor="text-warning"
        />
        <MetricCard
          title="IPs Blocked"
          value={metrics?.ipsBlocked || 0}
          icon={Shield}
          iconColor="text-danger"
        />
        <MetricCard
          title="Active Decoys"
          value={metrics?.activeDecoys || 0}
          icon={Layers}
          iconColor="text-success"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ThreatGauge level={metrics?.threatLevel || 'low'} />
        <TopDecoysChart data={decoyStats} />
      </div>

      <EventTimeline events={events} />
    </div>
  );
};
