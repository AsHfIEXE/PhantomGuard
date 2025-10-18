"""
PhantomGuard: Main Application Runner
Orchestrates all modules: configuration, watcher, event processing, and response playbook.
"""
import json
import queue
import threading
import time
import logging
import sys
import asyncio
from typing import Dict, Any

from alerting.telegram_alert import TelegramAlerter
from processor.event_scorer import EventScorer
from processor.ip_blocker import IPBlocker
from processor.playbook import Playbook
from sensors.fs_watcher import DecoyEventHandler, Observer
from processor.event_queue import PersistentQueue
from sensors.http_honeypot import run_honeypot
from sensors.ssh_banner import SSHBannerServer
from processor.event_enrich import enrich_event
# kept for API compatibility (may be used elsewhere)
from processor.hybrid_anomaly import HybridAnomalyModel

# Setup structured JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    stream=sys.stdout
)


def log_json(event_type, **kwargs):
    logging.info(json.dumps({'event': event_type, **kwargs}))


def load_config(path: str) -> Dict[str, Any]:
    """Loads and validates the JSON configuration."""
    try:
        with open(path, 'r') as f:
            config = json.load(f)
        # Add validation logic here as needed
        return config
    except Exception as e:
        log_json('config_error', error=str(e), path=path)
        sys.exit(1)


def event_processor(
        event_queue: queue.Queue,
        scorer: EventScorer,
        playbook: Playbook,
        anomaly: Any):
    """Processes events: enrich, score, suppress FPs, and respond."""
    import json
    import os
    fp_state_path = 'ui/fp_state.json'

    def load_fp_state():
        if os.path.exists(fp_state_path):
            return json.loads(open(fp_state_path).read())
        return []
    fp_list = load_fp_state()
    while True:
        try:
            event = event_queue.get()
            if event is None:
                time.sleep(0.5)
                continue
            # Enrich event
            enriched = enrich_event(event)
            # Score anomaly (hybrid model)
            anomaly_score = anomaly.score(enriched)
            enriched['anomaly_score'] = anomaly_score
            # Suppress if marked as FP
            sig = enriched.get('sig') or str(hash(json.dumps(enriched)))
            enriched['sig'] = sig
            if sig in fp_list:
                log_json('suppressed_fp', path=enriched.get('path'), sig=sig)
                event_queue.task_done()
                continue
            # Score and respond
            score, matches = scorer.score_event(enriched)
            if scorer.is_suspicious(enriched):
                log_json(
                    'suspicious_event',
                    path=enriched.get('path'),
                    score=score,
                    matches=matches,
                    anomaly_score=anomaly_score)
                enriched['score'] = score
                enriched['matches'] = matches
                playbook.handle_event(enriched, score, matches)
            event_queue.task_done()
        except Exception as e:
            log_json('processor_error', error=str(e))


def main():
    """Initializes and starts all PhantomGuard components."""
    config = load_config('config.json')

    # 1. Initialize components
    alerter = TelegramAlerter(
        token=config['telegram']['bot_token'],
        chat_id=config['telegram']['chat_id'],
        hmac_key=config['telegram']['hmac_key']
    )
    blocker = IPBlocker(dry_run=config['blocker']['dry_run'])
    playbook = Playbook(
        alert_func=alerter.send_alert,
        block_func=blocker.block_ip)
    scorer = EventScorer(
        rules=config['scorer']['rules'],
        threshold=config['scorer']['threshold'])
    # Use hybrid anomaly model for best-in-class detection
    input_dim = 5  # Adjust if you add more features
    anomaly = HybridAnomalyModel(input_dim)
    # Optionally train hybrid anomaly model on benign events (load from file or config)
    # anomaly.fit(benign_events)

    # 2. Setup persistent event bus and processor thread
    event_queue = PersistentQueue(
        path=config.get(
            'event_queue_path',
            '/var/log/phantomguard/events.log'))
    processor_thread = threading.Thread(
        target=event_processor,
        args=(event_queue, scorer, playbook, anomaly),
        daemon=True
    )
    processor_thread.start()

    # 3. Start the filesystem watcher
    event_bus = type("EventBus", (), {"emit": event_queue.put})
    handler = DecoyEventHandler(event_bus)
    observer = Observer()

    watch_paths = config['watcher']['paths']
    print(f"[Watcher] Monitoring paths: {', '.join(watch_paths)}")
    log_json('watcher_start', paths=watch_paths)
    for path in watch_paths:
        observer.schedule(handler, path, recursive=True)
    observer.start()
    # Start network deception modules
    loop = asyncio.get_event_loop()
    # start honeypot (task object intentionally not stored)
    loop.create_task(
        run_honeypot(
            event_queue.put,
            port=config.get(
                'http_honeypot_port',
                8080)))
    ssh_server = SSHBannerServer(
        event_queue.put, port=config.get(
            'ssh_banner_port', 2222))
    ssh_server.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log_json('shutdown', message='Shutting down PhantomGuard')
        observer.stop()
        ssh_server.stop()
        event_queue.put(None)  # Signal processor to exit
    observer.join()
    processor_thread.join()
    log_json('shutdown_complete', message='PhantomGuard stopped')


if __name__ == "__main__":
    main()
