import React, { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle, Shield } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import type { Alert } from '../types';
import { alertsApi } from '../services/api';
import { formatTimestamp, truncateText } from '../utils/formatters';
import { generateMockEvents, generateMockAlerts } from '../utils/mockData';

export const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [filter, setFilter] = useState<'all' | 'unacknowledged'>('all');

  const loadAlerts = async () => {
    try {
      const data = await alertsApi.getAll(50);

      if (data.length === 0) {
        const mockEvents = generateMockEvents(50);
        const mockAlerts = generateMockAlerts(mockEvents);
        setAlerts(mockAlerts);
      } else {
        setAlerts(data);
      }
    } catch (error) {
      console.error('Failed to load alerts:', error);
      const mockEvents = generateMockEvents(50);
      const mockAlerts = generateMockAlerts(mockEvents);
      setAlerts(mockAlerts);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  const handleAcknowledge = async (id: string) => {
    try {
      await alertsApi.acknowledge(id);
      loadAlerts();
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const filteredAlerts = alerts.filter((alert) =>
    filter === 'all' ? true : !alert.acknowledged
  );

  const getSeverityIcon = (severity: string) => {
    if (severity === 'critical' || severity === 'high') {
      return <AlertTriangle className="text-danger" size={20} />;
    }
    return <Shield className="text-warning" size={20} />;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">Alerts</h2>
          <p className="text-gray-400">High-severity events requiring attention</p>
        </div>

        <div className="flex gap-2">
          <Button
            variant={filter === 'all' ? 'primary' : 'secondary'}
            onClick={() => setFilter('all')}
          >
            All
          </Button>
          <Button
            variant={filter === 'unacknowledged' ? 'primary' : 'secondary'}
            onClick={() => setFilter('unacknowledged')}
          >
            Unacknowledged
          </Button>
        </div>
      </div>

      <div className="space-y-4">
        {filteredAlerts.length === 0 ? (
          <Card>
            <p className="text-center py-8 text-gray-500">No alerts found</p>
          </Card>
        ) : (
          filteredAlerts.map((alert) => (
            <Card key={alert.id} elevated>
              <div className="flex items-start gap-4">
                <div className="mt-1">{getSeverityIcon(alert.severity)}</div>

                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <Badge variant={alert.severity as any}>
                      {alert.severity.toUpperCase()}
                    </Badge>
                    {alert.acknowledged && (
                      <div className="flex items-center gap-1 text-success text-sm">
                        <CheckCircle size={16} />
                        <span>Acknowledged</span>
                      </div>
                    )}
                    <span className="text-sm text-gray-400">
                      {formatTimestamp(alert.created_at)}
                    </span>
                  </div>

                  {alert.event && (
                    <div className="space-y-2 mb-4">
                      <div>
                        <span className="text-white font-medium">{alert.event.event_type}</span>
                        {' - '}
                        <span className="text-gray-400">Score: {alert.event.score.toFixed(1)}</span>
                      </div>
                      <div className="text-sm text-gray-400 font-mono">
                        {truncateText(alert.event.decoy_path, 80)}
                      </div>
                      {alert.event.source_ip && (
                        <div className="text-sm text-gray-400">
                          Source IP: <span className="font-mono">{alert.event.source_ip}</span>
                        </div>
                      )}
                      {alert.event.matched_rules && alert.event.matched_rules.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-2">
                          {alert.event.matched_rules.map((rule, i) => (
                            <Badge key={i} variant="info">
                              {rule}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {alert.response_actions && alert.response_actions.length > 0 && (
                    <div className="text-sm text-gray-400 mb-3">
                      <span className="font-medium">Response Actions:</span>{' '}
                      {alert.response_actions.map((a) => a.action).join(', ')}
                    </div>
                  )}

                  {alert.notes && (
                    <div className="text-sm text-gray-300 bg-dark-elevated p-3 rounded-lg mb-3">
                      {alert.notes}
                    </div>
                  )}

                  {!alert.acknowledged && (
                    <Button
                      size="sm"
                      variant="success"
                      onClick={() => handleAcknowledge(alert.id)}
                    >
                      Acknowledge
                    </Button>
                  )}
                </div>
              </div>
            </Card>
          ))
        )}
      </div>

      <div className="text-sm text-gray-400">
        Showing {filteredAlerts.length} of {alerts.length} alerts
      </div>
    </div>
  );
};
