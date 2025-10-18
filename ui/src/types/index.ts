export interface Event {
  id: string;
  timestamp: string;
  event_type: string;
  decoy_path: string;
  score: number;
  source_ip?: string;
  process_info: {
    name?: string;
    pid?: number;
    user?: string;
    command?: string;
  };
  matched_rules: string[];
  payload: Record<string, any>;
  created_at: string;
}

export interface Alert {
  id: string;
  event_id: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  acknowledged: boolean;
  acknowledged_at?: string;
  response_actions: {
    action: string;
    timestamp: string;
    status: string;
  }[];
  notes: string;
  created_at: string;
  event?: Event;
}

export interface Decoy {
  id: string;
  name: string;
  path: string;
  type: 'file' | 'ssh_key' | 'token' | 'config' | 'database';
  size_bytes: number;
  content_preview: string;
  access_count: number;
  last_accessed_at?: string;
  created_at: string;
}

export interface Label {
  id: string;
  event_id: string;
  signature: string;
  label: 'benign' | 'attack' | 'false_positive';
  notes: string;
  labeled_by: string;
  created_at: string;
  event?: Event;
}

export interface BlockedIP {
  id: string;
  ip_address: string;
  reason: string;
  event_count: number;
  blocked_at: string;
  unblocked_at?: string;
  created_at: string;
}

export interface SystemConfig {
  id: string;
  key: string;
  value: Record<string, any>;
  updated_at: string;
}

export interface SystemStatus {
  id: string;
  status: 'running' | 'stopped';
  uptime_seconds: number;
  last_event_at?: string;
  updated_at: string;
}

export interface DashboardMetrics {
  totalEvents: number;
  totalEventsToday: number;
  alertsTriggered: number;
  ipsBlocked: number;
  activeDecoys: number;
  threatLevel: 'low' | 'medium' | 'high' | 'critical';
}

export interface TimeSeriesDataPoint {
  timestamp: string;
  count: number;
  avgScore: number;
}

export interface SourceIPStat {
  ip_address: string;
  country?: string;
  event_count: number;
  avg_score: number;
  is_blocked: boolean;
}

export interface DecoyStats {
  decoy_name: string;
  decoy_path: string;
  access_count: number;
  avg_score: number;
}

export type EventFilter = {
  timeRange?: '1h' | '6h' | '24h' | '7d' | 'custom';
  startDate?: string;
  endDate?: string;
  eventType?: string;
  minScore?: number;
  maxScore?: number;
  searchTerm?: string;
};

export type SortDirection = 'asc' | 'desc';

export type EventSort = {
  field: 'timestamp' | 'score' | 'event_type';
  direction: SortDirection;
};
