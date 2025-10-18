"""
PhantomGuard REST API Server - Enhanced for React Dashboard
Provides REST endpoints for the React frontend to connect to PhantomGuard.
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
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Paths
LOG_PATH = Path('logs/phantomguard/alerts.log')
BLOCK_LOG_PATH = Path('logs/phantomguard/block.log')
FP_STATE_PATH = Path('ui/fp_state.json')
LABELS_PATH = Path('ui/labels.jsonl')
CONFIG_PATH = Path('config.json')
EVENT_QUEUE_PATH = Path('logs/phantomguard/events.log')

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
    events = load_events(limit=1)
    is_running = False
    uptime = 0
    last_event_time = None
    
    if events:
        last_event_time = events[-1].get('timestamp', 0)
        is_running = (time.time() - last_event_time) < 300
    
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
    
    if filter_type:
        events = [e for e in events if e.get('event_type') == filter_type]
    
    if min_score is not None:
        events = [e for e in events if e.get('score', 0) >= min_score]
    
    events = events[offset:offset + limit]
    
    return jsonify({
        'events': events,
        'total': len(events),
        'limit': limit,
        'offset': offset
    })

@app.route('/api/events/<event_id>/label', methods=['POST'])
def label_event(event_id):
    """Label an event."""
    data = request.json
    label = data.get('label')
    
    if label not in ['benign', 'attack', 'fp']:
        return jsonify({'error': 'Invalid label'}), 400
    
    events = load_events()
    event = None
    for e in events:
        if e.get('sig') == event_id:
            event = e
            break
    
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    append_label(event_id, label, event.get('timestamp'))
    
    if label == 'fp':
        fp_list = load_fp_state()
        if event_id not in fp_list:
            fp_list.append(event_id)
            save_fp_state(fp_list)
    
    return jsonify({'success': True, 'label': label})

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get high-severity alerts."""
    limit = int(request.args.get('limit', 50))
    
    events = load_events(limit=200)
    alerts = [e for e in events if e.get('score', 0) >= 50]
    alerts = alerts[-limit:]
    
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
        
        events = load_events(limit=1000)
        for decoy in decoys:
            path = decoy.get('path', '')
            accesses = [e for e in events if path in e.get('path', '')]
            decoy['access_count'] = len(accesses)
            decoy['last_access'] = accesses[-1].get('timestamp') if accesses else None
        
        return jsonify({'decoys': decoys})
    except:
        return jsonify({'decoys': []})

@app.route('/api/analytics/metrics', methods=['GET'])
def get_metrics():
    """Get dashboard metrics."""
    events = load_events(limit=1000)
    
    now = time.time()
    today_start = now - 86400
    week_start = now - 7 * 86400
    
    events_today = len([e for e in events if e.get('timestamp', 0) >= today_start])
    events_week = len([e for e in events if e.get('timestamp', 0) >= week_start])
    
    alerts = [e for e in events if e.get('score', 0) >= 50]
    alerts_today = len([a for a in alerts if a.get('timestamp', 0) >= today_start])
    
    blocked_ips = set()
    if BLOCK_LOG_PATH.exists():
        for line in BLOCK_LOG_PATH.read_text().splitlines():
            parts = line.split()
            if len(parts) >= 2:
                blocked_ips.add(parts[1])
    
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
    
    hours = 24
    if range_param.endswith('h'):
        hours = int(range_param[:-1])
    elif range_param.endswith('d'):
        hours = int(range_param[:-1]) * 24
    
    events = load_events(limit=5000)
    now = time.time()
    start_time = now - (hours * 3600)
    
    events = [e for e in events if e.get('timestamp', 0) >= start_time]
    
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
            sources[ip] = {'ip': ip, 'count': 0, 'total_score': 0}
        sources[ip]['count'] += 1
        sources[ip]['total_score'] += event.get('score', 0)
    
    for ip_data in sources.values():
        ip_data['avg_score'] = ip_data['total_score'] / ip_data['count'] if ip_data['count'] > 0 else 0
    
    top_sources = sorted(sources.values(), key=lambda x: x['count'], reverse=True)[:10]
    
    return jsonify({'sources': top_sources})

@app.route('/api/labels', methods=['GET'])
def get_labels():
    """Get all labels."""
    labels = load_labels()
    return jsonify({'labels': labels})

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration."""
    if not CONFIG_PATH.exists():
        return jsonify({'error': 'Config not found'}), 404
    
    try:
        config = json.loads(CONFIG_PATH.read_text())
        if 'telegram' in config:
            config['telegram']['bot_token'] = '***REDACTED***'
            config['telegram']['hmac_key'] = '***REDACTED***'
        return jsonify(config)
    except:
        return jsonify({'error': 'Invalid config'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({'status': 'ok', 'version': '2.0'})

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 PhantomGuard API Server")
    print("=" * 60)
    print("\n📊 API Running at: http://localhost:5000")
    print("\n📍 Endpoints:")
    print("  GET  /api/status          - System status")
    print("  GET  /api/events          - Get all events")
    print("  GET  /api/alerts          - Get high-severity alerts")
    print("  GET  /api/metrics         - Dashboard metrics")
    print("  GET  /api/timeline        - Time series data")
    print("  POST /api/events/<id>/label - Label an event")
    print("  GET  /health              - Health check")
    print("\n🎯 Connect your React dashboard to http://localhost:5000")
    print("\n⏹️  Press Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)