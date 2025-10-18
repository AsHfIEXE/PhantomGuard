import React from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import type { Event } from '../../types';
import { formatTimestamp, getScoreSeverity } from '../../utils/formatters';
import { labelsApi } from '../../services/api';

interface EventDetailsModalProps {
  event: Event | null;
  isOpen: boolean;
  onClose: () => void;
  onLabel?: () => void;
}

export const EventDetailsModal: React.FC<EventDetailsModalProps> = ({
  event,
  isOpen,
  onClose,
  onLabel,
}) => {
  if (!event) return null;

  const handleLabel = async (label: 'benign' | 'attack' | 'false_positive') => {
    try {
      await labelsApi.create({
        event_id: event.id,
        signature: `${event.event_type}_${event.decoy_path}`,
        label,
        notes: '',
        labeled_by: 'user',
      });
      onLabel?.();
      onClose();
    } catch (error) {
      console.error('Failed to label event:', error);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Event Details" size="lg">
      <div className="space-y-6">
        <div>
          <div className="flex items-center gap-3 mb-4">
            <Badge variant={getScoreSeverity(event.score)}>
              Score: {event.score.toFixed(1)}
            </Badge>
            <span className="text-sm text-gray-400">{formatTimestamp(event.timestamp)}</span>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-400 mb-1">Event Type</p>
              <p className="text-white font-medium">{event.event_type}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400 mb-1">Source IP</p>
              <p className="text-white font-medium">{event.source_ip || 'Unknown'}</p>
            </div>
            <div className="col-span-2">
              <p className="text-sm text-gray-400 mb-1">Decoy Path</p>
              <p className="text-white font-mono text-sm break-all">{event.decoy_path}</p>
            </div>
          </div>
        </div>

        {event.process_info && Object.keys(event.process_info).length > 0 && (
          <div>
            <h4 className="text-white font-semibold mb-3">Process Information</h4>
            <div className="bg-dark-elevated rounded-lg p-4 space-y-2">
              {event.process_info.name && (
                <div className="flex justify-between">
                  <span className="text-gray-400">Name:</span>
                  <span className="text-white font-mono">{event.process_info.name}</span>
                </div>
              )}
              {event.process_info.pid && (
                <div className="flex justify-between">
                  <span className="text-gray-400">PID:</span>
                  <span className="text-white font-mono">{event.process_info.pid}</span>
                </div>
              )}
              {event.process_info.user && (
                <div className="flex justify-between">
                  <span className="text-gray-400">User:</span>
                  <span className="text-white font-mono">{event.process_info.user}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {event.matched_rules && event.matched_rules.length > 0 && (
          <div>
            <h4 className="text-white font-semibold mb-3">Matched Rules</h4>
            <div className="flex flex-wrap gap-2">
              {event.matched_rules.map((rule, index) => (
                <Badge key={index} variant="info">
                  {rule}
                </Badge>
              ))}
            </div>
          </div>
        )}

        <div>
          <h4 className="text-white font-semibold mb-3">Full Payload</h4>
          <pre className="bg-dark-elevated rounded-lg p-4 text-xs text-gray-300 overflow-x-auto">
            {JSON.stringify(event.payload, null, 2)}
          </pre>
        </div>

        <div>
          <h4 className="text-white font-semibold mb-3">Label This Event</h4>
          <div className="flex gap-3">
            <Button variant="success" onClick={() => handleLabel('benign')}>
              Benign
            </Button>
            <Button variant="danger" onClick={() => handleLabel('attack')}>
              Attack
            </Button>
            <Button variant="secondary" onClick={() => handleLabel('false_positive')}>
              False Positive
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
};
