"""
Daily retraining script for PhantomGuard hybrid anomaly model.
Loads recent events, retrains model, saves updated weights.
Run via cron/systemd or manually.
"""
import os
import json
from datetime import datetime, timedelta
from processor.hybrid_anomaly import HybridAnomalyModel
from pathlib import Path

EVENT_LOG = '/var/log/phantomguard/events.jsonl'  # Or wherever events are stored
MODEL_PATH = 'processor/hybrid_anomaly_weights.pt'
INPUT_DIM = 5  # Adjust if you add more features
LABELS_PATH = Path('ui/labels.jsonl')

# Load recent events (last 24h)


def load_recent_events(path, hours=24):
    cutoff = datetime.now() - timedelta(hours=hours)
    events = []
    if not os.path.exists(path):
        return events
    with open(path) as f:
        for line in f:
            try:
                event = json.loads(line)
                ts = event.get('timestamp')
                if ts:
                    event_time = datetime.fromisoformat(ts)
                    if event_time >= cutoff:
                        events.append(event)
            except Exception:
                continue
    return events

# Load labels


def load_labels(path: Path):
    labels = []
    if not path.exists():
        return labels
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            try:
                labels.append(json.loads(line))
            except Exception:
                continue
    return labels


def main():
    events = load_recent_events(EVENT_LOG)
    labels: list[dict] = load_labels(LABELS_PATH)
    # Map sig -> label
    label_map = {label_entry['sig']: label_entry['label']
                 for label_entry in labels if 'sig' in label_entry and 'label' in label_entry}
    # Prefer labeled benign events
    benign = []
    if labels:
        # Pull events that match labeled sigs
        for e in events:
            sig = e.get('sig')
            if sig and label_map.get(sig) == 'benign':
                benign.append(e)
    # Fallback to events with inlined label
    if not benign:
        benign = [e for e in events if e.get('label') == 'benign']
    if not benign:
        print('No benign events to train on.')
        return
    X = [HybridAnomalyModel.extract_features(e) for e in benign]
    model = HybridAnomalyModel(INPUT_DIM)
    model.fit(X)
    # Save model: try a save method if present, otherwise pickle
    try:
        model.save(MODEL_PATH)
        print(f'Retrained and saved hybrid anomaly model to {MODEL_PATH}')
    except Exception:
        import pickle
        with open(MODEL_PATH + '.pkl', 'wb') as f:
            pickle.dump(model, f)
        print(
            f'Retrained and pickled hybrid anomaly model to {MODEL_PATH}.pkl')


if __name__ == '__main__':
    main()
