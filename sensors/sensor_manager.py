"""
PhantomGuard Sensor Manager
Manages sensor lifecycle and health monitoring.
"""
import time
import logging
from typing import Callable, Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)


class HealthMonitor:
    """Monitors system health and tracks events/errors."""
    
    def __init__(self):
        self.start_time = time.time()
        self.events = 0
        self.alerts = 0
        self.blocks = 0
        self.errors: List[str] = []
        self._max_errors = 100  # Keep last 100 errors
    
    def record_event(self):
        """Record a processed event."""
        self.events += 1
    
    def record_alert(self):
        """Record a sent alert."""
        self.alerts += 1
    
    def record_block(self):
        """Record an IP block."""
        self.blocks += 1
    
    def record_error(self, error: str):
        """Record an error message."""
        self.errors.append(error)
        if len(self.errors) > self._max_errors:
            self.errors.pop(0)
    
    def print_status(self):
        """Print current health status."""
        runtime = int(time.time() - self.start_time)
        hours = runtime // 3600
        minutes = (runtime % 3600) // 60
        
        print("\n📊 System Health Report")
        print(f"Runtime: {hours}h {minutes}m")
        print(f"Events Processed: {self.events}")
        print(f"Alerts Sent: {self.alerts}")
        print(f"IPs Blocked: {self.blocks}")
        
        if self.errors:
            print(f"\nLast {len(self.errors)} Errors:")
            for error in self.errors[-5:]:  # Show last 5 errors
                print(f"  • {error}")


class SensorManager:
    """Manages sensor lifecycle and monitors health."""
    
    def __init__(self):
        self.sensors: Dict[str, Dict[str, Any]] = {}
    
    def register_sensor(
        self,
        name: str,
        start_func: Callable[[], Any],
        stop_func: Optional[Callable[[Any], None]] = None
    ):
        """
        Register a new sensor.
        
        Args:
            name: Sensor name for logging
            start_func: Function to start the sensor
            stop_func: Optional function to stop the sensor
        """
        self.sensors[name] = {
            'start_func': start_func,
            'stop_func': stop_func,
            'instance': None,
            'active': False,
            'last_error': None
        }
    
    def start_all(self) -> Tuple[int, int]:
        """
        Start all registered sensors.
        Returns (successful_starts, failed_starts).
        """
        successful = 0
        failed = 0
        
        print("🔌 Starting sensors...")
        for name, sensor in self.sensors.items():
            try:
                print(f"  • Starting {name}...")
                instance = sensor['start_func']()
                sensor['instance'] = instance
                sensor['active'] = True
                sensor['last_error'] = None
                successful += 1
                print(f"    ✅ {name} started successfully")
            except Exception as e:
                sensor['last_error'] = str(e)
                failed += 1
                print(f"    ❌ {name} failed to start: {e}")
        
        return successful, failed
    
    def stop_all(self):
        """Stop all active sensors."""
        for name, sensor in self.sensors.items():
            if sensor['active'] and sensor['stop_func'] and sensor['instance']:
                try:
                    sensor['stop_func'](sensor['instance'])
                    sensor['active'] = False
                    print(f"✅ {name} stopped successfully")
                except Exception as e:
                    print(f"❌ Failed to stop {name}: {e}")
    
    def health_check(self) -> bool:
        """
        Check if any sensors are active.
        Returns False if no sensors are running.
        """
        active = sum(1 for s in self.sensors.values() if s['active'])
        return active > 0