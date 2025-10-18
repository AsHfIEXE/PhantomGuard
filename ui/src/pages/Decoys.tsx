import React, { useEffect, useState } from 'react';
import { Plus, FileText, Key, Hash, Database, Trash2 } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Modal } from '../components/common/Modal';
import type { Decoy } from '../types';
import { decoysApi } from '../services/api';
import { formatRelativeTime, formatBytes } from '../utils/formatters';
import { generateMockDecoys } from '../utils/mockData';

const getDecoyIcon = (type: string) => {
  switch (type) {
    case 'ssh_key':
      return <Key className="text-warning" size={24} />;
    case 'token':
      return <Hash className="text-primary" size={24} />;
    case 'database':
      return <Database className="text-danger" size={24} />;
    default:
      return <FileText className="text-success" size={24} />;
  }
};

export const Decoys: React.FC = () => {
  const [decoys, setDecoys] = useState<Decoy[]>([]);
  const [selectedDecoy, setSelectedDecoy] = useState<Decoy | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const [newDecoy, setNewDecoy] = useState({
    name: '',
    path: '',
    type: 'file' as Decoy['type'],
    size_bytes: 0,
    content_preview: '',
  });

  const loadDecoys = async () => {
    try {
      const data = await decoysApi.getAll();

      if (data.length === 0) {
        const mockDecoys = generateMockDecoys();
        setDecoys(mockDecoys);
      } else {
        setDecoys(data);
      }
    } catch (error) {
      console.error('Failed to load decoys:', error);
      const mockDecoys = generateMockDecoys();
      setDecoys(mockDecoys);
    }
  };

  useEffect(() => {
    loadDecoys();
  }, []);

  const handleCreateDecoy = async () => {
    try {
      await decoysApi.create(newDecoy);
      setIsCreateModalOpen(false);
      setNewDecoy({
        name: '',
        path: '',
        type: 'file',
        size_bytes: 0,
        content_preview: '',
      });
      loadDecoys();
    } catch (error) {
      console.error('Failed to create decoy:', error);
    }
  };

  const handleDeleteDecoy = async (id: string) => {
    if (!confirm('Are you sure you want to delete this decoy?')) return;

    try {
      await decoysApi.delete(id);
      loadDecoys();
    } catch (error) {
      console.error('Failed to delete decoy:', error);
    }
  };

  const handleViewContent = (decoy: Decoy) => {
    setSelectedDecoy(decoy);
    setIsViewModalOpen(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">Decoys</h2>
          <p className="text-gray-400">Manage honeypot decoys and monitor interactions</p>
        </div>

        <div className="flex gap-2">
          <Button
            variant="secondary"
            onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
          >
            {viewMode === 'grid' ? 'List View' : 'Grid View'}
          </Button>
          <Button onClick={() => setIsCreateModalOpen(true)}>
            <Plus size={18} className="mr-2" />
            Add Decoy
          </Button>
        </div>
      </div>

      <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}>
        {decoys.map((decoy) => (
          <Card key={decoy.id} elevated>
            <div className="flex items-start gap-4">
              <div className="p-3 bg-dark-elevated rounded-lg">
                {getDecoyIcon(decoy.type)}
              </div>

              <div className="flex-1 min-w-0">
                <h3 className="text-white font-semibold mb-1">{decoy.name}</h3>
                <p className="text-xs text-gray-400 font-mono mb-2 truncate">{decoy.path}</p>

                <div className="flex flex-wrap gap-2 mb-3">
                  <Badge variant="info">{decoy.type}</Badge>
                  <Badge variant="low">{formatBytes(decoy.size_bytes)}</Badge>
                </div>

                <div className="text-sm text-gray-400 space-y-1 mb-3">
                  <div>Accessed: <span className="text-white font-semibold">{decoy.access_count}</span> times</div>
                  {decoy.last_accessed_at && (
                    <div>Last: {formatRelativeTime(decoy.last_accessed_at)}</div>
                  )}
                </div>

                <div className="flex gap-2">
                  <Button size="sm" onClick={() => handleViewContent(decoy)}>
                    View
                  </Button>
                  <Button
                    size="sm"
                    variant="danger"
                    onClick={() => handleDeleteDecoy(decoy.id)}
                  >
                    <Trash2 size={14} />
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create New Decoy"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Name</label>
            <input
              type="text"
              value={newDecoy.name}
              onChange={(e) => setNewDecoy({ ...newDecoy, name: e.target.value })}
              className="w-full px-4 py-2 bg-dark-elevated border border-dark-border rounded-lg text-white focus:outline-none focus:border-primary"
              placeholder="AWS Credentials"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Path</label>
            <input
              type="text"
              value={newDecoy.path}
              onChange={(e) => setNewDecoy({ ...newDecoy, path: e.target.value })}
              className="w-full px-4 py-2 bg-dark-elevated border border-dark-border rounded-lg text-white focus:outline-none focus:border-primary font-mono"
              placeholder="/home/admin/.aws/credentials"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Type</label>
            <select
              value={newDecoy.type}
              onChange={(e) => setNewDecoy({ ...newDecoy, type: e.target.value as any })}
              className="w-full px-4 py-2 bg-dark-elevated border border-dark-border rounded-lg text-white focus:outline-none focus:border-primary"
            >
              <option value="file">File</option>
              <option value="ssh_key">SSH Key</option>
              <option value="token">Token</option>
              <option value="config">Config</option>
              <option value="database">Database</option>
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Size (bytes)</label>
            <input
              type="number"
              value={newDecoy.size_bytes}
              onChange={(e) => setNewDecoy({ ...newDecoy, size_bytes: Number(e.target.value) })}
              className="w-full px-4 py-2 bg-dark-elevated border border-dark-border rounded-lg text-white focus:outline-none focus:border-primary"
              placeholder="1024"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Content Preview</label>
            <textarea
              value={newDecoy.content_preview}
              onChange={(e) => setNewDecoy({ ...newDecoy, content_preview: e.target.value })}
              className="w-full px-4 py-2 bg-dark-elevated border border-dark-border rounded-lg text-white focus:outline-none focus:border-primary font-mono text-sm"
              rows={4}
              placeholder="First 500 characters of file content..."
            />
          </div>

          <Button onClick={handleCreateDecoy} className="w-full">
            Create Decoy
          </Button>
        </div>
      </Modal>

      <Modal
        isOpen={isViewModalOpen}
        onClose={() => setIsViewModalOpen(false)}
        title={selectedDecoy?.name || 'Decoy Content'}
      >
        {selectedDecoy && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-400 mb-1">Type</p>
                <Badge variant="info">{selectedDecoy.type}</Badge>
              </div>
              <div>
                <p className="text-sm text-gray-400 mb-1">Size</p>
                <p className="text-white">{formatBytes(selectedDecoy.size_bytes)}</p>
              </div>
              <div className="col-span-2">
                <p className="text-sm text-gray-400 mb-1">Path</p>
                <p className="text-white font-mono text-sm break-all">{selectedDecoy.path}</p>
              </div>
            </div>

            <div>
              <p className="text-sm text-gray-400 mb-2">Content Preview</p>
              <pre className="bg-dark-elevated rounded-lg p-4 text-xs text-gray-300 overflow-x-auto">
                {selectedDecoy.content_preview || 'No preview available'}
              </pre>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
