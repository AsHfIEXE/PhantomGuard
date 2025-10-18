import React from 'react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import type { Event } from '../../types';
import { formatRelativeTime, getScoreSeverity, truncateText } from '../../utils/formatters';

interface EventTimelineProps {
  events: Event[];
}

export const EventTimeline: React.FC<EventTimelineProps> = ({ events }) => {
  return (
    <Card className="h-full">
      <h3 className="text-lg font-semibold text-white mb-4">Recent Events</h3>
      <div className="space-y-3 max-h-[500px] overflow-y-auto">
        {events.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No events yet</p>
        ) : (
          events.map((event) => (
            <div
              key={event.id}
              className="flex items-start gap-3 p-3 rounded-lg bg-dark-elevated border border-dark-border hover:border-primary/50 transition-colors"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <Badge variant={getScoreSeverity(event.score)}>
                    Score: {event.score.toFixed(1)}
                  </Badge>
                  <span className="text-xs text-gray-500">
                    {formatRelativeTime(event.timestamp)}
                  </span>
                </div>
                <p className="text-sm text-white font-medium">{event.event_type}</p>
                <p className="text-xs text-gray-400 truncate">
                  {truncateText(event.decoy_path, 60)}
                </p>
                {event.source_ip && (
                  <p className="text-xs text-gray-500 mt-1">IP: {event.source_ip}</p>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </Card>
  );
};
