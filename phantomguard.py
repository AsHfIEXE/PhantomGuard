"""
PhantomGuard v2: Enhanced Main Application
Production-ready with config validation, health monitoring, and resilient sensors.
"""
import json
import queue
import threading
import time
import logging
import sys
import asyncio
import signal
from typing import Dict, Any
from pathlib import Path

from alerting.telegram_alert import TelegramAlerter
from processor.event_scorer import EventScorer
from processor.ip_blocker import IPBlocker
from processor.playbook import Playbook
from sensors.fs_watcher import DecoyEventHandler, Observer
from processor.event_queue import PersistentQueue
from sensors.http_honeypot import run_honeypot
from sensors.ssh_banner import SSHBannerServer
from processor.event_enrich import enrich_event
from processor.hybrid_anomaly import HybridAnomalyModel
from processor.config_validator import ConfigValidator
from sensors.sensor_manager import SensorManager, HealthMonitor

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/phantomguard/phantomguard.log')
    ]
)
logger = logging.getLogger('PhantomGuard')


class PhantomGuardApp:
    """Main PhantomGuard application with enhanced error handling."""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = config_path
        self.config = None
        self.sensor_manager = SensorManager()
        self.health_monitor = HealthMonitor()
        self.event_queue = None
        self.processor_thread = None
        self.observer = None
        self.ssh_server = None
        self.running = False
    
    def load_and_validate_config(self) -> bool:
        """Load and validate configuration file."""
        try:
            print(f"📄 Loading configuration from {self.config_path}...")
            
            if not Path(self.config_path).exists():
                print(f"❌ Configuration file not found: {self.config_path}")
                print("💡 Copy config.json.example to config.json and edit it")
                return False
            
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            
            print("✅ Configuration loaded\n")
            
            # Validate configuration
            print("🔍 Validating configuration...")
            if not ConfigValidator.validate_and_print(self.config):
                return False
            
            print()
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {self.config_path}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return False
    
    def initialize_components(self):
        """Initialize all PhantomGuard components."""
        print("🔧 Initializing components...\n")
        
        # 1. Alerting
        self.alerter = TelegramAlerter(
            token=self.config['telegram']['bot_token'],
            chat_id=self.config['telegram']['chat_id'],
            hmac_key=self.config['telegram']['hmac_key']
        )
        print("✅ Telegram alerter initialized")
        
        # 2. IP Blocker
        self.blocker = IPBlocker(dry_run=self.config['blocker']['dry_run'])
        if self.config['blocker']['dry_run']:
            print("✅ IP blocker initialized (DRY-RUN MODE)")
        else:
            print("⚠️  IP blocker initialized (ACTIVE MODE - Real blocking enabled!)")
        
        # 3. Playbook
        self.playbook = Playbook(
            alert_func=self.alerter.send_alert,
            block_func=self.blocker.block_ip
        )
        print("✅ Response playbook initialized")
        
        # 4. Event Scorer
        self.scorer = EventScorer(
            rules=self.config['scorer']['rules'],
            threshold=self.config['scorer']['threshold']
        )
        print(f"✅ Event scorer initialized (threshold: {self.config['scorer']['threshold']})")
        
        # 5. Anomaly Detection
        input_dim = 5
        self.anomaly = HybridAnomalyModel(input_dim)
        print("✅ Hybrid anomaly model initialized")
        
        # 6. Event Queue
        queue_path = self.config.get('event_queue_path', 'logs/phantomguard/events.log')
        Path(queue_path).parent.mkdir(parents=True, exist_ok=True)
        self.event_queue = PersistentQueue(path=queue_path)
        print(f"✅ Persistent event queue initialized ({queue_path})")
        
        print()
    
    def setup_filesystem_watcher(self):
        """Setup filesystem watcher for decoy monitoring."""
        event_bus = type("EventBus", (), {"emit": self.event_queue.put})()
        handler = DecoyEventHandler(event_bus)
        self.observer = Observer()
        
        watch_paths = self.config['watcher']['paths']
        
        for path in watch_paths:
            try:
                # Ensure parent directory exists
                parent = Path(path).parent
                parent.mkdir(parents=True, exist_ok=True)
                
                self.observer.schedule(handler, str(parent), recursive=True)
            except Exception as e:
                logger.error(f"Failed to watch {path}: {e}")
                self.health_monitor.record_error(f"Watcher setup failed for {path}")
        
        return len(watch_paths)
    
    def event_processor(self):
        """Process events from the queue."""
        fp_state_path = Path('ui/fp_state.json')
        
        def load_fp_state():
            if fp_state_path.exists():
                try:
                    with open(fp_state_path) as f:
                        return json.load(f)
                except Exception:
                    return []
            return []
        
        fp_list = load_fp_state()
        last_fp_reload = time.time()
        
        while self.running:
            try:
                event = self.event_queue.get(timeout=1.0)
                if event is None:
                    continue
                
                # Reload FP list every 60 seconds
                if time.time() - last_fp_reload > 60:
                    fp_list = load_fp_state()
                    last_fp_reload = time.time()
                
                # Enrich event
                enriched = enrich_event(event)
                self.health_monitor.record_event()
                
                # Score anomaly
                try:
                    anomaly_score = self.anomaly.score(enriched)
                    enriched['anomaly_score'] = anomaly_score
                except Exception as e:
                    logger.error(f"Anomaly scoring failed: {e}")
                    enriched['anomaly_score'] = 0.0
                    self.health_monitor.record_error(f"Anomaly scoring: {e}")
                
                # Generate signature for FP tracking
                sig = enriched.get('sig') or str(hash(json.dumps(enriched, sort_keys=True)))
                enriched['sig'] = sig
                
                # Suppress if marked as FP
                if sig in fp_list:
                    logger.debug(f"Suppressed FP: {enriched.get('path')}")
                    self.event_queue.task_done()
                    continue
                
                # Score and respond
                score, matches = self.scorer.score_event(enriched)
                
                if self.scorer.is_suspicious(enriched):
                    logger.info(f"Suspicious event: {enriched.get('path')} (score: {score})")
                    enriched['score'] = score
                    enriched['matches'] = matches
                    
                    try:
                        self.playbook.handle_event(enriched, score, matches)
                        if score >= 60:
                            self.health_monitor.record_alert()
                        if score >= 80:
                            self.health_monitor.record_block()
                    except Exception as e:
                        logger.error(f"Playbook execution failed: {e}")
                        self.health_monitor.record_error(f"Playbook: {e}")
                
                self.event_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Event processor error: {e}")
                self.health_monitor.record_error(f"Processor: {e}")
    
    def start_sensors(self):
        """Start all sensors with resilient error handling."""
        
        # 1. Filesystem Watcher
        def start_fs_watcher():
            watch_count = self.setup_filesystem_watcher()
            self.observer.start()
            return self.observer
        
        def stop_fs_watcher(obs):
            obs.stop()
            obs.join(timeout=5)
        
        self.sensor_manager.register_sensor(
            "Filesystem Watcher",
            start_fs_watcher,
            stop_fs_watcher
        )
        
        # 2. SSH Banner Server
        def start_ssh_banner():
            ssh_port = self.config.get('ssh_banner_port', 2222)
            server = SSHBannerServer(self.event_queue.put, port=ssh_port)
            server.start()
            return server
        
        def stop_ssh_banner(server):
            server.stop()
        
        self.sensor_manager.register_sensor(
            "SSH Banner Server",
            start_ssh_banner,
            stop_ssh_banner
        )
        
        # 3. HTTP Honeypot (runs in async context)
        def start_http_honeypot():
            http_port = self.config.get('http_honeypot_port', 8080)
            # Run in separate thread with its own event loop
            def run_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(run_honeypot(self.event_queue.put, port=http_port))
            
            thread = threading.Thread(target=run_async, daemon=True)
            thread.start()
            return thread
        
        self.sensor_manager.register_sensor(
            "HTTP Honeypot",
            start_http_honeypot,
            None  # Daemon thread, will stop with main process
        )
        
        # Start all sensors
        successful, failed = self.sensor_manager.start_all()
        
        if successful == 0:
            print("❌ No sensors started successfully. Cannot continue.")
            return False
        
        return True
    
    def start(self):
        """Start PhantomGuard system."""
        print("\n" + "=" * 60)
        print("👻 PhantomGuard v2 - Starting...")
        print("=" * 60 + "\n")
        
        # Load and validate config
        if not self.load_and_validate_config():
            return False
        
        # Initialize components
        try:
            self.initialize_components()
        except Exception as e:
            print(f"❌ Component initialization failed: {e}")
            return False
        
        # Start event processor thread
        self.running = True
        self.processor_thread = threading.Thread(
            target=self.event_processor,
            daemon=True
        )
        self.processor_thread.start()
        print("✅ Event processor started\n")
        
        # Start sensors
        if not self.start_sensors():
            self.running = False
            return False
        
        print("\n" + "=" * 60)
        print("✅ PhantomGuard is now running!")
        print("=" * 60)
        print("\n📊 Quick Stats:")
        print(f"  • Watching {len(self.config['watcher']['paths'])} paths")
        print(f"  • {len(self.config['scorer']['rules'])} scoring rules loaded")
        print(f"  • Alert threshold: {self.config['scorer']['threshold']}")
        print(f"  • Dry-run mode: {'ON' if self.config['blocker']['dry_run'] else 'OFF (REAL BLOCKING!)'}")
        print("\n💡 Next steps:")
        print("  • View dashboard: streamlit run ui/dashboard.py")
        print("  • Test system: python3 demo/attack_simulator.py")
        print("  • Check logs: tail -f logs/phantomguard/phantomguard.log")
        print("\n⏹️  Press Ctrl+C to stop\n")
        
        return True
    
    def stop(self):
        """Stop PhantomGuard system gracefully."""
        print("\n🛑 Stopping PhantomGuard...")
        
        self.running = False
        
        # Stop sensors
        self.sensor_manager.stop_all()
        
        # Stop processor thread
        if self.processor_thread and self.processor_thread.is_alive():
            self.event_queue.put(None)  # Signal to stop
            self.processor_thread.join(timeout=5)
        
        # Print final stats
        self.health_monitor.print_status()
        
        print("✅ PhantomGuard stopped successfully\n")
    
    def run(self):
        """Run PhantomGuard until interrupted."""
        if not self.start():
            sys.exit(1)
        
        # Setup signal handlers
        def signal_handler(sig, frame):
            print("\n")  # New line after ^C
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Main loop with periodic health checks
        try:
            while True:
                time.sleep(60)  # Check every minute
                
                # Print periodic status
                if not self.sensor_manager.health_check():
                    logger.warning("Health check failed - no active sensors!")
                    self.health_monitor.record_error("Health check failed")
                
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()


def main():
    """Main entry point."""
    # Ensure log directory exists
    Path('logs/phantomguard').mkdir(parents=True, exist_ok=True)
    
    # Create and run application
    app = PhantomGuardApp('config.json')
    app.run()


if __name__ == "__main__":
    main()