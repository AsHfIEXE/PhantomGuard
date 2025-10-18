import React from 'react';
import { Activity, Bell, Ghost } from 'lucide-react';
import { useStore } from '../../store/useStore';
import { Badge } from '../common/Badge';

export const Header: React.FC = () => {
  const { systemStatus, metrics } = useStore();

  return (
    <header className="bg-dark-surface border-b border-dark-border px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Ghost className="text-primary" size={32} />
          <div>
            <h1 className="text-2xl font-bold text-white">PhantomGuard</h1>
            <p className="text-sm text-gray-400">Deception-Based Threat Detection</p>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                systemStatus?.status === 'running' ? 'bg-success animate-pulse' : 'bg-gray-500'
              }`}
            />
            <span className="text-sm text-gray-300">
              {systemStatus?.status === 'running' ? 'Running' : 'Stopped'}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <Activity size={18} className="text-primary" />
            <span className="text-sm text-gray-300">
              Events: <span className="font-semibold text-white">{metrics?.totalEvents || 0}</span>
            </span>
          </div>

          <div className="flex items-center gap-2">
            <Bell size={18} className="text-warning" />
            <span className="text-sm text-gray-300">
              Alerts: <span className="font-semibold text-white">{metrics?.alertsTriggered || 0}</span>
            </span>
          </div>

          {metrics?.threatLevel && (
            <Badge variant={metrics.threatLevel}>
              {metrics.threatLevel.toUpperCase()}
            </Badge>
          )}
        </div>
      </div>
    </header>
  );
};
