import type { Event, Alert, Decoy, Label } from '../types';

const eventTypes = [
  'file_access',
  'network_scan',
  'ssh_attempt',
  'token_read',
  'database_query',
  'config_read',
];

const decoyPaths = [
  '/home/admin/.aws/credentials',
  '/var/www/.env',
  '/root/.ssh/id_rsa',
  '/opt/app/config/database.yml',
  '/etc/shadow',
  '/home/user/.bash_history',
  '/var/log/secrets.log',
  '/opt/passwords.txt',
  '/root/.mysql_history',
  '/home/admin/api_keys.json',
];

const sourceIPs = [
  '192.168.1.100',
  '10.0.0.45',
  '172.16.0.88',
  '203.0.113.42',
  '198.51.100.67',
  '192.0.2.123',
];

const processNames = ['bash', 'python3', 'node', 'curl', 'wget', 'ssh', 'nc', 'nmap'];

export const generateMockEvents = (count: number): Event[] => {
  const events: Event[] = [];
  const now = Date.now();

  for (let i = 0; i < count; i++) {
    const timestamp = new Date(now - Math.random() * 7 * 24 * 60 * 60 * 1000);
    const score = Math.random() * 100;

    events.push({
      id: `event-${i}`,
      timestamp: timestamp.toISOString(),
      event_type: eventTypes[Math.floor(Math.random() * eventTypes.length)],
      decoy_path: decoyPaths[Math.floor(Math.random() * decoyPaths.length)],
      score: Math.round(score * 10) / 10,
      source_ip: sourceIPs[Math.floor(Math.random() * sourceIPs.length)],
      process_info: {
        name: processNames[Math.floor(Math.random() * processNames.length)],
        pid: Math.floor(Math.random() * 65535),
        user: Math.random() > 0.5 ? 'root' : 'user',
        command: 'cat /path/to/file',
      },
      matched_rules: score > 60 ? ['suspicious_time', 'unusual_process'] : ['normal_access'],
      payload: {
        action: 'read',
        bytes_read: Math.floor(Math.random() * 10000),
      },
      created_at: timestamp.toISOString(),
    });
  }

  return events.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
};

export const generateMockAlerts = (events: Event[]): Alert[] => {
  return events
    .filter((e) => e.score >= 60)
    .slice(0, 10)
    .map((event, i) => ({
      id: `alert-${i}`,
      event_id: event.id,
      severity: event.score >= 80 ? 'critical' : event.score >= 70 ? 'high' : 'medium',
      acknowledged: Math.random() > 0.5,
      acknowledged_at: Math.random() > 0.5 ? new Date().toISOString() : undefined,
      response_actions: [
        {
          action: 'alert_sent',
          timestamp: event.timestamp,
          status: 'completed',
        },
      ],
      notes: '',
      created_at: event.timestamp,
      event,
    })) as Alert[];
};

export const generateMockDecoys = (): Decoy[] => {
  return [
    {
      id: 'decoy-1',
      name: 'AWS Credentials',
      path: '/home/admin/.aws/credentials',
      type: 'config',
      size_bytes: 245,
      content_preview: '[default]\naws_access_key_id = AKIAIOSFODNN7EXAMPLE\naws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
      access_count: 15,
      last_accessed_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: 'decoy-2',
      name: 'Database Environment',
      path: '/var/www/.env',
      type: 'config',
      size_bytes: 512,
      content_preview: 'DB_HOST=localhost\nDB_USER=admin\nDB_PASSWORD=SuperSecret123\nDB_NAME=production',
      access_count: 8,
      last_accessed_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
      created_at: new Date(Date.now() - 25 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: 'decoy-3',
      name: 'SSH Private Key',
      path: '/root/.ssh/id_rsa',
      type: 'ssh_key',
      size_bytes: 1679,
      content_preview: '-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA1234567890...',
      access_count: 23,
      last_accessed_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
      created_at: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: 'decoy-4',
      name: 'API Keys',
      path: '/home/admin/api_keys.json',
      type: 'token',
      size_bytes: 342,
      content_preview: '{"stripe": "sk_live_123456", "twilio": "AC123456", "sendgrid": "SG.123456"}',
      access_count: 5,
      last_accessed_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
      created_at: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: 'decoy-5',
      name: 'Password File',
      path: '/opt/passwords.txt',
      type: 'file',
      size_bytes: 128,
      content_preview: 'admin:P@ssw0rd123\nroot:SuperSecure456\nuser:Welcome2024',
      access_count: 12,
      last_accessed_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
      created_at: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
    },
  ];
};

export const generateMockLabels = (events: Event[]): Label[] => {
  return events.slice(0, 20).map((event, i) => ({
    id: `label-${i}`,
    event_id: event.id,
    signature: `${event.event_type}_${event.decoy_path}`,
    label: event.score > 70 ? 'attack' : event.score > 40 ? 'benign' : 'false_positive',
    notes: i % 3 === 0 ? 'Verified by security team' : '',
    labeled_by: 'admin',
    created_at: event.timestamp,
    event,
  })) as Label[];
};
