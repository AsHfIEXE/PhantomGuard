import React, { useEffect, useState } from 'react';
import { Play, Square, RefreshCw, Save } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { systemApi } from '../services/api';
import { useStore } from '../store/useStore';

export const Settings: React.FC = () => {
  const { systemStatus, setSystemStatus } = useStore();
  const [config, setConfig] = useState({
    alertThreshold: 60,
    pollingInterval: 5000,
    enableTelegram: false,
    telegramBotToken: '',
    telegramChatId: '',
    watcherPaths: ['/home', '/opt', '/var/www'],
    enableDryRun: false,
  });

  useEffect(() => {
    loadSystemStatus();
  }, []);

  const loadSystemStatus = async () => {
    try {
      const status = await systemApi.getStatus();
      if (status) {
        setSystemStatus(status);
      }
    } catch (error) {
      console.error('Failed to load system status:', error);
    }
  };

  const handleStartStop = async () => {
    try {
      const newStatus = systemStatus?.status === 'running' ? 'stopped' : 'running';
      const updated = await systemApi.updateStatus({ status: newStatus });
      setSystemStatus(updated);
    } catch (error) {
      console.error('Failed to update system status:', error);
    }
  };

  const handleSaveConfig = () => {
    console.log('Saving configuration:', config);
    alert('Configuration saved successfully!');
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Settings</h2>
        <p className="text-gray-400">Configure PhantomGuard system and integrations</p>
      </div>

      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">System Controls</h3>
        <div className="flex items-center gap-4">
          <Button
            onClick={handleStartStop}
            variant={systemStatus?.status === 'running' ? 'danger' : 'success'}
            size="lg"
          >
            {systemStatus?.status === 'running' ? (
              <>
                <Square size={18} className="mr-2" />
                Stop PhantomGuard
              </>
            ) : (
              <>
                <Play size={18} className="mr-2" />
                Start PhantomGuard
              </>
            )}
          </Button>

          <Button variant="secondary" size="lg">
            <RefreshCw size={18} className="mr-2" />
            Restart
          </Button>

          <div className="ml-auto flex items-center gap-2">
            <input
              type="checkbox"
              id="dryRun"
              checked={config.enableDryRun}
              onChange={(e) => setConfig({ ...config, enableDryRun: e.target.checked })}
              className="w-4 h-4 rounded border-dark-border bg-dark-elevated"
            />
            <label htmlFor="dryRun" className="text-sm text-gray-300">
              Dry Run Mode
            </label>
          </div>
        </div>

        {systemStatus && (
          <div className="mt-4 p-4 bg-dark-elevated rounded-lg">
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-400">Status</p>
                <p className="text-white font-medium capitalize">{systemStatus.status}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Uptime</p>
                <p className="text-white font-medium">
                  {Math.floor(systemStatus.uptime_seconds / 3600)}h{' '}
                  {Math.floor((systemStatus.uptime_seconds % 3600) / 60)}m
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Last Event</p>
                <p className="text-white font-medium">
                  {systemStatus.last_event_at
                    ? new Date(systemStatus.last_event_at).toLocaleTimeString()
                    : 'Never'}
                </p>
              </div>
            </div>
          </div>
        )}
      </Card>

      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Detection Settings</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">
              Alert Threshold (Score)
            </label>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="0"
                max="100"
                value={config.alertThreshold}
                onChange={(e) => setConfig({ ...config, alertThreshold: Number(e.target.value) })}
                className="flex-1"
              />
              <span className="text-white font-medium w-12">{config.alertThreshold}</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Events with scores above this threshold will trigger alerts
            </p>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">
              Polling Interval (ms)
            </label>
            <input
              type="number"
              value={config.pollingInterval}
              onChange={(e) => setConfig({ ...config, pollingInterval: Number(e.target.value) })}
              className="w-full px-4 py-2 bg-dark-elevated border border-dark-border rounded-lg text-white focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">
              Watcher Paths
            </label>
            <div className="space-y-2">
              {config.watcherPaths.map((path, index) => (
                <input
                  key={index}
                  type="text"
                  value={path}
                  onChange={(e) => {
                    const newPaths = [...config.watcherPaths];
                    newPaths[index] = e.target.value;
                    setConfig({ ...config, watcherPaths: newPaths });
                  }}
                  className="w-full px-4 py-2 bg-dark-elevated border border-dark-border rounded-lg text-white font-mono focus:outline-none focus:border-primary"
                />
              ))}
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Telegram Integration</h3>
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-4">
            <input
              type="checkbox"
              id="enableTelegram"
              checked={config.enableTelegram}
              onChange={(e) => setConfig({ ...config, enableTelegram: e.target.checked })}
              className="w-4 h-4 rounded border-dark-border bg-dark-elevated"
            />
            <label htmlFor="enableTelegram" className="text-sm text-gray-300">
              Enable Telegram Alerts
            </label>
          </div>

          {config.enableTelegram && (
            <>
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Bot Token
                </label>
                <input
                  type="password"
                  value={config.telegramBotToken}
                  onChange={(e) => setConfig({ ...config, telegramBotToken: e.target.value })}
                  placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
                  className="w-full px-4 py-2 bg-dark-elevated border border-dark-border rounded-lg text-white font-mono focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Chat ID
                </label>
                <input
                  type="text"
                  value={config.telegramChatId}
                  onChange={(e) => setConfig({ ...config, telegramChatId: e.target.value })}
                  placeholder="-1001234567890"
                  className="w-full px-4 py-2 bg-dark-elevated border border-dark-border rounded-lg text-white font-mono focus:outline-none focus:border-primary"
                />
              </div>

              <Button variant="secondary">
                Test Alert
              </Button>
            </>
          )}
        </div>
      </Card>

      <div className="flex justify-end">
        <Button onClick={handleSaveConfig} size="lg">
          <Save size={18} className="mr-2" />
          Save Configuration
        </Button>
      </div>
    </div>
  );
};
