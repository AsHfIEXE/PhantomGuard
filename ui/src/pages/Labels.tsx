import React, { useEffect, useState } from 'react';
import { Trash2, Download } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import type { Label } from '../types';
import { labelsApi } from '../services/api';
import { formatTimestamp } from '../utils/formatters';
import { generateMockEvents, generateMockLabels } from '../utils/mockData';

export const Labels: React.FC = () => {
  const [labels, setLabels] = useState<Label[]>([]);
  const [filter, setFilter] = useState<'all' | 'benign' | 'attack' | 'false_positive'>('all');

  const loadLabels = async () => {
    try {
      const data = await labelsApi.getAll();

      if (data.length === 0) {
        const mockEvents = generateMockEvents(50);
        const mockLabels = generateMockLabels(mockEvents);
        setLabels(mockLabels);
      } else {
        setLabels(data);
      }
    } catch (error) {
      console.error('Failed to load labels:', error);
      const mockEvents = generateMockEvents(50);
      const mockLabels = generateMockLabels(mockEvents);
      setLabels(mockLabels);
    }
  };

  useEffect(() => {
    loadLabels();
  }, []);

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this label?')) return;

    try {
      await labelsApi.delete(id);
      loadLabels();
    } catch (error) {
      console.error('Failed to delete label:', error);
    }
  };

  const handleExport = () => {
    const csvContent = [
      ['Signature', 'Label', 'Notes', 'Created At'].join(','),
      ...labels.map((label) =>
        [
          label.signature,
          label.label,
          label.notes.replace(/,/g, ';'),
          label.created_at,
        ].join(',')
      ),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `phantomguard-labels-${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredLabels = labels.filter((label) =>
    filter === 'all' ? true : label.label === filter
  );

  const getLabelBadgeVariant = (label: string): 'low' | 'medium' | 'high' | 'critical' | 'info' => {
    switch (label) {
      case 'benign':
        return 'low';
      case 'attack':
        return 'critical';
      case 'false_positive':
        return 'medium';
      default:
        return 'info';
    }
  };

  const stats = {
    total: labels.length,
    benign: labels.filter((l) => l.label === 'benign').length,
    attack: labels.filter((l) => l.label === 'attack').length,
    falsePositive: labels.filter((l) => l.label === 'false_positive').length,
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">Training Labels</h2>
          <p className="text-gray-400">Manage labeled events for machine learning</p>
        </div>

        <Button onClick={handleExport}>
          <Download size={18} className="mr-2" />
          Export CSV
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <p className="text-sm text-gray-400 mb-1">Total Labels</p>
          <p className="text-2xl font-bold text-white">{stats.total}</p>
        </Card>
        <Card>
          <p className="text-sm text-gray-400 mb-1">Benign</p>
          <p className="text-2xl font-bold text-success">{stats.benign}</p>
        </Card>
        <Card>
          <p className="text-sm text-gray-400 mb-1">Attack</p>
          <p className="text-2xl font-bold text-danger">{stats.attack}</p>
        </Card>
        <Card>
          <p className="text-sm text-gray-400 mb-1">False Positives</p>
          <p className="text-2xl font-bold text-warning">{stats.falsePositive}</p>
        </Card>
      </div>

      <div className="flex gap-2">
        <Button
          variant={filter === 'all' ? 'primary' : 'secondary'}
          onClick={() => setFilter('all')}
        >
          All
        </Button>
        <Button
          variant={filter === 'benign' ? 'primary' : 'secondary'}
          onClick={() => setFilter('benign')}
        >
          Benign
        </Button>
        <Button
          variant={filter === 'attack' ? 'primary' : 'secondary'}
          onClick={() => setFilter('attack')}
        >
          Attack
        </Button>
        <Button
          variant={filter === 'false_positive' ? 'primary' : 'secondary'}
          onClick={() => setFilter('false_positive')}
        >
          False Positive
        </Button>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-dark-border">
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Signature</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Label</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Notes</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Created</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredLabels.length === 0 ? (
                <tr>
                  <td colSpan={5} className="text-center py-8 text-gray-500">
                    No labels found
                  </td>
                </tr>
              ) : (
                filteredLabels.map((label) => (
                  <tr
                    key={label.id}
                    className="border-b border-dark-border hover:bg-dark-elevated transition-colors"
                  >
                    <td className="py-3 px-4 text-sm text-white font-mono">
                      {label.signature}
                    </td>
                    <td className="py-3 px-4">
                      <Badge variant={getLabelBadgeVariant(label.label)}>
                        {label.label.replace('_', ' ').toUpperCase()}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-400">
                      {label.notes || '-'}
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-400">
                      {formatTimestamp(label.created_at)}
                    </td>
                    <td className="py-3 px-4">
                      <Button
                        size="sm"
                        variant="danger"
                        onClick={() => handleDelete(label.id)}
                      >
                        <Trash2 size={14} />
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="mt-4 text-sm text-gray-400">
          Showing {filteredLabels.length} of {labels.length} labels
        </div>
      </Card>
    </div>
  );
};
