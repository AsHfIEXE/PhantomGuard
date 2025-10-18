import React, { useEffect, useState } from 'react';
import { Search, Filter } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { EventDetailsModal } from '../components/events/EventDetailsModal';
import type { Event, EventFilter } from '../types';
import { eventsApi } from '../services/api';
import { usePolling } from '../hooks/usePolling';
import { formatTimestamp, getScoreSeverity, truncateText } from '../utils/formatters';
import { generateMockEvents } from '../utils/mockData';

export const Events: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h' | '7d'>('24h');
  const [minScore, setMinScore] = useState(0);

  const loadEvents = async () => {
    try {
      const filter: EventFilter = {
        timeRange,
        minScore,
        searchTerm: searchTerm || undefined,
      };

      const data = await eventsApi.getAll(filter, { field: 'timestamp', direction: 'desc' }, 100);

      if (data.length === 0) {
        setEvents(generateMockEvents(50));
      } else {
        setEvents(data);
      }
    } catch (error) {
      console.error('Failed to load events:', error);
      setEvents(generateMockEvents(50));
    }
  };

  useEffect(() => {
    loadEvents();
  }, [timeRange, minScore]);

  usePolling(loadEvents, 5000);

  const handleSearch = () => {
    loadEvents();
  };

  const handleViewDetails = (event: Event) => {
    setSelectedEvent(event);
    setIsModalOpen(true);
  };

  const filteredEvents = events;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Events</h2>
        <p className="text-gray-400">Monitor and analyze security events in real-time</p>
      </div>

      <Card>
        <div className="flex flex-col lg:flex-row gap-4 mb-6">
          <div className="flex-1 flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="text"
                placeholder="Search by path or IP..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="w-full pl-10 pr-4 py-2 bg-dark-elevated border border-dark-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary"
              />
            </div>
            <Button onClick={handleSearch}>Search</Button>
          </div>

          <div className="flex gap-4">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as any)}
              className="px-4 py-2 bg-dark-elevated border border-dark-border rounded-lg text-white focus:outline-none focus:border-primary"
            >
              <option value="1h">Last Hour</option>
              <option value="6h">Last 6 Hours</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
            </select>

            <div className="flex items-center gap-2">
              <Filter size={18} className="text-gray-400" />
              <input
                type="range"
                min="0"
                max="100"
                value={minScore}
                onChange={(e) => setMinScore(Number(e.target.value))}
                className="w-32"
              />
              <span className="text-sm text-gray-400 min-w-[60px]">
                Score: {minScore}+
              </span>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-dark-border">
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Timestamp</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Event Type</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Decoy Path</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Score</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Source IP</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredEvents.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-8 text-gray-500">
                    No events found
                  </td>
                </tr>
              ) : (
                filteredEvents.map((event) => (
                  <tr
                    key={event.id}
                    className="border-b border-dark-border hover:bg-dark-elevated transition-colors"
                  >
                    <td className="py-3 px-4 text-sm text-gray-300">
                      {formatTimestamp(event.timestamp)}
                    </td>
                    <td className="py-3 px-4 text-sm text-white">{event.event_type}</td>
                    <td className="py-3 px-4 text-sm text-gray-300 font-mono">
                      {truncateText(event.decoy_path, 40)}
                    </td>
                    <td className="py-3 px-4">
                      <Badge variant={getScoreSeverity(event.score)}>
                        {event.score.toFixed(1)}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-300 font-mono">
                      {event.source_ip || 'Unknown'}
                    </td>
                    <td className="py-3 px-4">
                      <Button size="sm" onClick={() => handleViewDetails(event)}>
                        View
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="mt-4 text-sm text-gray-400">
          Showing {filteredEvents.length} events
        </div>
      </Card>

      <EventDetailsModal
        event={selectedEvent}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onLabel={loadEvents}
      />
    </div>
  );
};
