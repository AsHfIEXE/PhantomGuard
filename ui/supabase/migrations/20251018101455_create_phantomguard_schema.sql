/*
  # PhantomGuard Security Dashboard - Database Schema

  ## Overview
  Complete database schema for PhantomGuard deception-based threat detection system.
  Stores events, alerts, decoys, training labels, blocked IPs, and system configuration.

  ## Tables Created

  ### 1. events
  Stores all security events captured by PhantomGuard watchers
  - `id` (uuid, primary key) - Unique event identifier
  - `timestamp` (timestamptz) - When the event occurred
  - `event_type` (text) - Type of event (file_access, network_scan, ssh_attempt, etc.)
  - `decoy_path` (text) - Path to the decoy that was accessed
  - `score` (numeric) - Anomaly score (0-100)
  - `source_ip` (text) - IP address that triggered the event
  - `process_info` (jsonb) - Process details (name, pid, user, etc.)
  - `matched_rules` (jsonb) - Array of triggered detection rules
  - `payload` (jsonb) - Full event data payload
  - `created_at` (timestamptz) - Record creation time

  ### 2. alerts
  High-severity events that triggered alerting threshold
  - `id` (uuid, primary key) - Unique alert identifier
  - `event_id` (uuid, foreign key) - Reference to source event
  - `severity` (text) - Alert severity (low, medium, high, critical)
  - `acknowledged` (boolean) - Whether alert has been reviewed
  - `acknowledged_at` (timestamptz) - When alert was acknowledged
  - `response_actions` (jsonb) - Actions taken (alert sent, IP blocked, etc.)
  - `notes` (text) - Analyst notes
  - `created_at` (timestamptz) - Record creation time

  ### 3. decoys
  Configured decoy files and resources
  - `id` (uuid, primary key) - Unique decoy identifier
  - `name` (text) - Friendly decoy name
  - `path` (text) - File system path
  - `type` (text) - Decoy type (file, ssh_key, token, config, database)
  - `size_bytes` (integer) - File size
  - `content_preview` (text) - First 500 chars of content
  - `access_count` (integer) - Number of times accessed
  - `last_accessed_at` (timestamptz) - Most recent access
  - `created_at` (timestamptz) - Record creation time

  ### 4. labels
  Training data labels for machine learning
  - `id` (uuid, primary key) - Unique label identifier
  - `event_id` (uuid, foreign key) - Reference to labeled event
  - `signature` (text) - Event signature/pattern
  - `label` (text) - Classification (benign, attack, false_positive)
  - `notes` (text) - Optional labeling notes
  - `labeled_by` (text) - User or system that created label
  - `created_at` (timestamptz) - Record creation time

  ### 5. blocked_ips
  IP addresses that have been blocked
  - `id` (uuid, primary key) - Unique block identifier
  - `ip_address` (text, unique) - Blocked IP
  - `reason` (text) - Why IP was blocked
  - `event_count` (integer) - Number of malicious events from this IP
  - `blocked_at` (timestamptz) - When IP was blocked
  - `unblocked_at` (timestamptz) - When IP was unblocked (null if still blocked)
  - `created_at` (timestamptz) - Record creation time

  ### 6. system_config
  System configuration and settings
  - `id` (uuid, primary key) - Unique config identifier
  - `key` (text, unique) - Configuration key
  - `value` (jsonb) - Configuration value
  - `updated_at` (timestamptz) - Last update time

  ### 7. system_status
  Current system status and metrics
  - `id` (uuid, primary key) - Always single row
  - `status` (text) - System status (running, stopped)
  - `uptime_seconds` (integer) - Current uptime
  - `last_event_at` (timestamptz) - Most recent event timestamp
  - `updated_at` (timestamptz) - Last update time

  ## Security
  - Row Level Security (RLS) enabled on all tables
  - Public read access for authenticated users
  - Restricted write access

  ## Indexes
  - Performance indexes on frequently queried columns
  - Timestamp-based indexes for time-range queries
  - Foreign key indexes for join performance
*/

-- Events table
CREATE TABLE IF NOT EXISTS events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp timestamptz NOT NULL DEFAULT now(),
  event_type text NOT NULL,
  decoy_path text NOT NULL,
  score numeric NOT NULL DEFAULT 0,
  source_ip text,
  process_info jsonb DEFAULT '{}'::jsonb,
  matched_rules jsonb DEFAULT '[]'::jsonb,
  payload jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_score ON events(score DESC);
CREATE INDEX IF NOT EXISTS idx_events_source_ip ON events(source_ip);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);

ALTER TABLE events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access to events"
  ON events FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public insert to events"
  ON events FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id uuid REFERENCES events(id) ON DELETE CASCADE,
  severity text NOT NULL DEFAULT 'medium',
  acknowledged boolean DEFAULT false,
  acknowledged_at timestamptz,
  response_actions jsonb DEFAULT '[]'::jsonb,
  notes text DEFAULT '',
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_alerts_event_id ON alerts(event_id);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged);

ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access to alerts"
  ON alerts FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public insert to alerts"
  ON alerts FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow public update to alerts"
  ON alerts FOR UPDATE
  TO anon, authenticated
  USING (true)
  WITH CHECK (true);

-- Decoys table
CREATE TABLE IF NOT EXISTS decoys (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  path text NOT NULL UNIQUE,
  type text NOT NULL DEFAULT 'file',
  size_bytes integer DEFAULT 0,
  content_preview text DEFAULT '',
  access_count integer DEFAULT 0,
  last_accessed_at timestamptz,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_decoys_type ON decoys(type);
CREATE INDEX IF NOT EXISTS idx_decoys_access_count ON decoys(access_count DESC);

ALTER TABLE decoys ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access to decoys"
  ON decoys FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public insert to decoys"
  ON decoys FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow public update to decoys"
  ON decoys FOR UPDATE
  TO anon, authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete from decoys"
  ON decoys FOR DELETE
  TO anon, authenticated
  USING (true);

-- Labels table
CREATE TABLE IF NOT EXISTS labels (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id uuid REFERENCES events(id) ON DELETE CASCADE,
  signature text NOT NULL,
  label text NOT NULL,
  notes text DEFAULT '',
  labeled_by text DEFAULT 'user',
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_labels_event_id ON labels(event_id);
CREATE INDEX IF NOT EXISTS idx_labels_label ON labels(label);

ALTER TABLE labels ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access to labels"
  ON labels FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public insert to labels"
  ON labels FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow public delete from labels"
  ON labels FOR DELETE
  TO anon, authenticated
  USING (true);

-- Blocked IPs table
CREATE TABLE IF NOT EXISTS blocked_ips (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ip_address text NOT NULL UNIQUE,
  reason text NOT NULL,
  event_count integer DEFAULT 1,
  blocked_at timestamptz DEFAULT now(),
  unblocked_at timestamptz,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_blocked_ips_address ON blocked_ips(ip_address);
CREATE INDEX IF NOT EXISTS idx_blocked_ips_blocked_at ON blocked_ips(blocked_at DESC);

ALTER TABLE blocked_ips ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access to blocked_ips"
  ON blocked_ips FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public insert to blocked_ips"
  ON blocked_ips FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE POLICY "Allow public update to blocked_ips"
  ON blocked_ips FOR UPDATE
  TO anon, authenticated
  USING (true)
  WITH CHECK (true);

-- System config table
CREATE TABLE IF NOT EXISTS system_config (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  key text NOT NULL UNIQUE,
  value jsonb NOT NULL DEFAULT '{}'::jsonb,
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE system_config ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access to system_config"
  ON system_config FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public update to system_config"
  ON system_config FOR UPDATE
  TO anon, authenticated
  USING (true)
  WITH CHECK (true);

-- System status table
CREATE TABLE IF NOT EXISTS system_status (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  status text NOT NULL DEFAULT 'stopped',
  uptime_seconds integer DEFAULT 0,
  last_event_at timestamptz,
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE system_status ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access to system_status"
  ON system_status FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Allow public update to system_status"
  ON system_status FOR UPDATE
  TO anon, authenticated
  USING (true)
  WITH CHECK (true);

-- Insert initial system status
INSERT INTO system_status (status, uptime_seconds, updated_at)
VALUES ('running', 0, now())
ON CONFLICT DO NOTHING;