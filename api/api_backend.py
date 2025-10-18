"""
PhantomGuard REST API Server
Flask-based REST API for web UI integration.
Run with: python api/server.py
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta
import threading

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Paths
LOG_PATH = Path('logs/phantomguard/alerts.log')
BLOCK_LOG_PATH = Path('logs/phantomguard/block.log')
FP_STATE_PATH = Path('ui/fp_state.json')
LABELS_PATH = Path('ui/labels.jsonl')
CONFIG_PATH = Path('config.json')
EVENT_QUEUE_PATH = Path('logs/phantomguard/events.log')

# In-memory cache
cache = {
    'events': [],
    'alerts': [],
    'last_update': 0
}

def load_events(limit: int = 200) -> List[Dict]:
    """Load events from log file."""
    if not LOG_PATH.exists():
        return []
    
    events = []
    try:
        lines = LOG_PATH.read_text().strip().splitlines()[-limit:]
        for line in lines:
            try:
                parts = line.split(' ', 2)
                if len(parts) >= 3:
                    timestamp, sig, payload = parts
                    event = json.loads(payload)
                    event['sig'] = sig
                    event['timestamp'] = float(timestamp)
                    events.append(event)
            except:
                continue
    except:
        pass
    
    return events

def load_labels() -> List[Dict]:
    """Load labels from JSONL file."""
    if not LABELS_PATH.exists():
        return []
    
    labels = []
    for line in LABELS_PATH.read_text().splitlines():
        try:
            labels.append(json.loads(line))
        except:
            continue
    return labels

def load_fp_state() -> List[str]:
    """Load false positive signatures."""
    if not FP_STATE_PATH.exists():
        return []
    try:
        return json.loads(FP_STATE_PATH.read_text())
    except:
        return []

def save_fp_state(fp_list: List[str]):
    """Save false positive signatures."""
    FP_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FP_STATE_PATH.write_text(json.dumps(fp_list, indent=2))

def append_label(sig: str, label: str, timestamp: float = None):
    """Append a label to the labels file."""
    LABELS_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        'sig': sig,
        'label': label,
        'timestamp': timestamp or time.time()
    }
    with LABELS_PATH.open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')

# Routes

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status."""
    # Check if PhantomGuard is running by checking recent events
    events = load_events(limit=1)
    is_running = False
    uptime = 0
    last_event_time = None
    
    if events:
        last_event_time = events[-1].get('timestamp', 0)
        # Consider running if event within last 5 minutes
        is_running = (time.time() - last_event_time) < 300
    
    # Try to read uptime from a status file if it exists
    status_file = Path('logs/phantomguard/status.json')
    if status_file.exists():
        try:
            status_data = json.loads(status_file.read_text())
            uptime = time.time() - status_data.get('start_time', time.time())
            is_running = status_data.get('running', False)
        except:
            pass
    
    return jsonify({
        'status': 'running' if is_running else 'stopped',
        'uptime': int(uptime),
        'last_event': last_event_time,
        'version': '2.0'
    })

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get events with optional filtering."""
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    filter_type = request.args.get('type')
    min_score = request.args.get('min_score', type=int)
    
    events = load_events(limit=limit + offset)
    
    # Apply filters
    if filter_type:
        events = [e for e in events if e.get('event_type') == filter_type]
    
    if min_score is not None:
        events = [e for e in events if e.get('score', 0) >= min_score]
    
    # Pagination
    events = events[offset:offset + limit]
    
    return jsonify({
        'events': events,
        'total': len(events),
        'limit': limit,
        'offset': offset
    })

@app.route('/api/events/<event_id>', methods=['GET'])
def get_event(event_id):
    """Get a specific event by signature."""
    events = load_events()
    for event in events:
        if event.get('sig') == event_id:
            return jsonify(event)
    
    return jsonify({'error': 'Event not found'}), 404

@app.route('/api/events/<event_id>/label', methods=['POST'])
def label_event(event_id):
    """Label an event."""
    data = request.json
    label = data.get('label')
    
    if label not in ['benign', 'attack', 'fp']:
        return jsonify({'error': 'Invalid label'}), 400
    
    # Find event
    events = load_events()
    event = None
    for e in events:
        if e.get('sig') == event_id:
            event = e
            break
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Save label
    append_label(event_id, label, event.get('timestamp'))
    
    # If FP, add to FP list
    if label == 'fp':
        fp_list = load_fp_state()
        if event_id not in fp_list:
            fp_list.append(event_id)
            save_fp_state(fp_list)
    
    return jsonify({'success': True, 'label': label})

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get alerts (high-score events)."""
    limit = int(request.args.get('limit', 50))
    
    events = load_events(limit=200)
    # Filter for alerts (score >= 50)
    alerts = [e for e in events if e.get('score', 0) >= 50]
    alerts = alerts[-limit:]  # Get most recent
    
    return jsonify({
        'alerts': alerts,
        'total': len(alerts)
    })

@app.route('/api/decoys', methods=['GET'])
def get_decoys():
    """Get list of configured decoys."""
    if not CONFIG_PATH.exists():
        return jsonify({'decoys': []})
    
    try:
        config = json.loads(CONFIG_PATH.read_text())
        decoys = config.get('decoys', [])
        
        # Enrich with access stats
        events = load_events(limit=1000)
        for decoy in decoys:
            path = decoy.get('path', '')
            accesses = [e for e in events if path in e.get('path', '')]
            decoy['access_count'] = len(accesses)
            decoy['last_access'] = accesses[-1].get('timestamp') if accesses else None
        
        return jsonify({'decoys': decoys})
    except:
        return jsonify({'decoys': []})

@app.route('/api/decoys', methods=['POST'])
def create_decoy():
    """Create a new decoy (placeholder)."""
    data = request.json
    # TODO: Implement decoy creation
    return jsonify({'success': True, 'message': 'Decoy creation not yet implemented'})

@app.route('/api/analytics/metrics', methods=['GET'])
def get_metrics():
    """Get dashboard metrics."""
    events = load_events(limit=1000)
    
    # Calculate metrics
    now = time.time()
    today_start = now - 86400
    week_start = now - 7 * 86400
    
    events_today = len([e for e in events if e.get('timestamp', 0) >= today_start])
    events_week = len([e for e in events if e.get('timestamp', 0) >= week_start])
    
    alerts = [e for e in events if e.get('score', 0) >= 50]
    alerts_today = len([a for a in alerts if a.get('timestamp', 0) >= today_start])
    
    # Count blocked IPs
    blocked_ips = set()
    if BLOCK_LOG_PATH.exists():
        for line in BLOCK_LOG_PATH.read_text().splitlines():
            parts = line.split()
            if len(parts) >= 2:
                blocked_ips.add(parts[1])
    
    # Active decoys
    if CONFIG_PATH.exists():
        config = json.loads(CONFIG_PATH.read_text())
        active_decoys = len(config.get('decoys', []))
    else:
        active_decoys = 0
    
    return jsonify({
        'events_today': events_today,
        'events_week': events_week,
        'alerts_today': alerts_today,
        'total_alerts': len(alerts),
        'blocked_ips': len(blocked_ips),
        'active_decoys': active_decoys,
        'threat_level': 'medium' if alerts_today > 5 else 'low'
    })

@app.route('/api/analytics/timeline', methods=['GET'])
def get_timeline():
    """Get time series data for events."""
    range_param = request.args.get('range', '24h')
    
    # Parse range
    hours = 24
    if range_param.endswith('h'):
        hours = int(range_param[:-1])
    elif range_param.endswith('d'):
        hours = int(range_param[:-1]) * 24
    
    events = load_events(limit=5000)
    now = time.time()
    start_time = now - (hours * 3600)
    
    # Filter events in range
    events = [e for e in events if e.get('timestamp', 0) >= start_time]
    
    # Group by hour
    buckets = {}
    for event in events:
        timestamp = event.get('timestamp', 0)
        hour = int(timestamp // 3600) * 3600
        buckets[hour] = buckets.get(hour, 0) + 1
    
    timeline = [
        {'timestamp': ts, 'count': count}
        for ts, count in sorted(buckets.items())
    ]
    
    return jsonify({'timeline': timeline})

@app.route('/api/analytics/sources', methods=['GET'])
def get_sources():
    """Get top source IPs."""
    events = load_events(limit=1000)
    
    sources = {}
    for event in events:
        ip = event.get('source_ip', 'unknown')
        if ip not in sources:
            sources[ip] = {'ip': ip, 'count': 0, 'total_score': 0, 'events': []}
        sources[ip]['count'] += 1
        sources[ip]['total_score'] += event.get('score', 0)
        sources[ip]['events'].append(event)
    
    # Calculate averages
    for ip_data in sources.values():
        ip_data['avg_score'] = ip_data['total_score'] / ip_data['count'] if ip_data['count'] > 0 else 0
        del ip_data['events']  # Remove full events, too large
    
    # Sort by count
    top_sources = sorted(sources.values(), key=lambda x: x['count'], reverse=True)[:10]
    
    return jsonify({'sources': top_sources})

@app.route('/api/labels', methods=['GET'])
def get_labels():
    """Get all labels."""
    labels = load_labels()
    return jsonify({'labels': labels})

@app.route('/api/labels/<int:label_id>', methods=['DELETE'])
def delete_label(label_id):
    """Delete a label."""
    labels = load_labels()
    if 0 <= label_id < len(labels):
        labels.pop(label_id)
        # Rewrite file
        LABELS_PATH.write_text('\n'.join(json.dumps(l) for l in labels) + '\n' if labels else '')
        return jsonify({'success': True})
    return jsonify({'error': 'Label not found'}), 404

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration."""
    if not CONFIG_PATH.exists():
        return jsonify({'error': 'Config not found'}), 404
    
    try:
        config = json.loads(CONFIG_PATH.read_text())
        # Redact sensitive data
        if 'telegram' in config:
            config['telegram']['bot_token'] = '***REDACTED***'
            config['telegram']['hmac_key'] = '***REDACTED***'
        return jsonify(config)
    except:
        return jsonify({'error': 'Invalid config'}), 500

@app.route('/api/config', methods=['PUT'])
def update_config():
    """Update configuration."""
    data = request.json
    
    try:
        # Validate config
        from processor.config_validator import ConfigValidator
        errors = ConfigValidator.validate(data)
        if errors:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        # Save config
        CONFIG_PATH.write_text(json.dumps(data, indent=2))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/control/start', methods=['POST'])
def start_system():
    """Start PhantomGuard (placeholder)."""
    return jsonify({'message': 'Start command not yet implemented. Run: python phantomguard.py'})

@app.route('/api/control/stop', methods=['POST'])
def stop_system():
    """Stop PhantomGuard (placeholder)."""
    return jsonify({'message': 'Stop command not yet implemented. Use Ctrl+C'})

@app.route('/api/train', methods=['POST'])
def train_model():
    """Trigger ML model training."""
    import subprocess
    try:
        result = subprocess.run(
            ['python', 'processor/train_daily_anomaly.py'],
            capture_output=True,
            text=True
        )
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🚀 Starting PhantomGuard API Server...")
    print("📊 API will be available at: http://localhost:5000")
    print("📡 Frontend should connect to this URL")
    print("\nEndpoints:")
    print("  GET  /api/status")
    print("  GET  /api/events")
    print("  GET  /api/alerts")
    print("  GET  /api/decoys")
    print("  GET  /api/analytics/metrics")
    print("  GET  /api/analytics/timeline")
    print("  GET  /api/config")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
