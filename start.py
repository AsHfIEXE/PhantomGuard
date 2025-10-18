#!/usr/bin/env python3
"""
PhantomGuard - Single Entry Point
Starts all components: Core detection system + Streamlit Dashboard
Usage: python start.py
"""
import subprocess
import sys
import time
import signal
import os
from pathlib import Path
from typing import List, Optional

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class PhantomGuardLauncher:
    """Manages launching and stopping all PhantomGuard components."""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.running = False
    
    def print_banner(self):
        """Print startup banner."""
        banner = f"""
{Colors.HEADER}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║               👻 PhantomGuard v2.0                       ║
║          Deception-Based Threat Detection                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
{Colors.ENDC}
"""
        print(banner)
    
    def check_config(self) -> bool:
        """Check if configuration exists and is valid."""
        config_path = Path('config.json')
        
        if not config_path.exists():
            print(f"{Colors.FAIL}❌ config.json not found!{Colors.ENDC}")
            print(f"\n{Colors.WARNING}Quick fix:{Colors.ENDC}")
            print("  1. cp config.json.example config.json")
            print("  2. Edit config.json with your settings")
            print("  3. Run: python start.py\n")
            return False
        
        # Quick validation
        try:
            import json
            with open(config_path) as f:
                config = json.load(f)
            
            # Check critical fields
            if config['telegram']['bot_token'] == 'YOUR_TELEGRAM_BOT_TOKEN':
                print(f"{Colors.WARNING}⚠️  Warning: Telegram not configured (alerts will fail){Colors.ENDC}")
                print("   Get token from @BotFather on Telegram\n")
            
            print(f"{Colors.OKGREEN}✓{Colors.ENDC} Configuration loaded")
            return True
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Invalid config.json: {e}{Colors.ENDC}\n")
            return False
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed."""
        required = ['watchdog', 'streamlit', 'requests']
        missing = []
        
        for pkg in required:
            try:
                __import__(pkg.replace('-', '_'))
            except ImportError:
                missing.append(pkg)
        
        if missing:
            print(f"{Colors.FAIL}❌ Missing dependencies: {', '.join(missing)}{Colors.ENDC}")
            print(f"\n{Colors.WARNING}Install with:{Colors.ENDC}")
            print(f"  pip install {' '.join(missing)}\n")
            return False
        
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} All dependencies installed")
        return True
    
    def setup_directories(self):
        """Create necessary directories."""
        dirs = [
            'logs/phantomguard',
            'ui',
            '/tmp/.ssh',
            '/tmp/phantomguard-decoys'
        ]
        
        for directory in dirs:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
            except PermissionError:
                if not directory.startswith('/tmp'):
                    print(f"{Colors.WARNING}⚠️  Cannot create {directory} (permission denied){Colors.ENDC}")
        
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} Directories ready")
    
    def generate_decoys(self):
        """Generate decoy files if they don't exist."""
        print(f"{Colors.OKBLUE}📁 Checking decoys...{Colors.ENDC}")
        
        # Check if basic decoys exist
        basic_decoys = [
            '/tmp/.ssh/id_rsa',
            '/tmp/.env',
            '/tmp/backup.sql'
        ]
        
        missing = [d for d in basic_decoys if not Path(d).exists()]
        
        if missing:
            print(f"   Generating {len(missing)} missing decoys...")
            try:
                subprocess.run(
                    [sys.executable, 'phantomgen/decoy_engine.py', '--config', 'config.json'],
                    capture_output=True,
                    timeout=10
                )
                print(f"{Colors.OKGREEN}✓{Colors.ENDC} Decoys generated")
            except Exception as e:
                print(f"{Colors.WARNING}⚠️  Decoy generation failed: {e}{Colors.ENDC}")
        else:
            print(f"{Colors.OKGREEN}✓{Colors.ENDC} Decoys already exist")
    
    def start_core(self) -> Optional[subprocess.Popen]:
        """Start PhantomGuard core detection system."""
        print(f"\n{Colors.OKBLUE}🚀 Starting PhantomGuard Core...{Colors.ENDC}")
        
        try:
            # Start in new process with output capture
            process = subprocess.Popen(
                [sys.executable, '-u', 'phantomguard.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Wait a moment and check if it started
            time.sleep(2)
            
            if process.poll() is None:
                print(f"{Colors.OKGREEN}✓{Colors.ENDC} Core system started (PID: {process.pid})")
                return process
            else:
                print(f"{Colors.FAIL}❌ Core system failed to start{Colors.ENDC}")
                return None
                
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to start core: {e}{Colors.ENDC}")
            return None
    
    def start_dashboard(self) -> Optional[subprocess.Popen]:
        """Start Streamlit dashboard."""
        print(f"\n{Colors.OKBLUE}🖥️  Starting Streamlit Dashboard...{Colors.ENDC}")
        
        try:
            # Start Streamlit in new process
            process = subprocess.Popen(
                [sys.executable, '-m', 'streamlit', 'run', 'ui/dashboard.py', 
                 '--server.headless', 'true',
                 '--server.port', '8501',
                 '--browser.gatherUsageStats', 'false'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Wait for Streamlit to start
            time.sleep(3)
            
            if process.poll() is None:
                print(f"{Colors.OKGREEN}✓{Colors.ENDC} Dashboard started (PID: {process.pid})")
                print(f"   URL: {Colors.OKBLUE}http://localhost:8501{Colors.ENDC}")
                return process
            else:
                print(f"{Colors.FAIL}❌ Dashboard failed to start{Colors.ENDC}")
                return None
                
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to start dashboard: {e}{Colors.ENDC}")
            return None
    
    def monitor_processes(self):
        """Monitor running processes and restart if needed."""
        print(f"\n{Colors.OKGREEN}✅ PhantomGuard is running!{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Access Points:{Colors.ENDC}")
        print(f"  📊 Dashboard: {Colors.OKBLUE}http://localhost:8501{Colors.ENDC}")
        print(f"  📝 Logs: {Colors.OKBLUE}tail -f logs/phantomguard/phantomguard.log{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Quick Actions:{Colors.ENDC}")
        print(f"  • Test: {Colors.OKBLUE}python demo/attack_simulator.py{Colors.ENDC}")
        print(f"  • Stop: {Colors.WARNING}Press Ctrl+C{Colors.ENDC}")
        print("\n" + "=" * 60 + "\n")
        
        try:
            while self.running:
                # Check if processes are still alive
                for i, proc in enumerate(self.processes):
                    if proc.poll() is not None:
                        name = "Core" if i == 0 else "Dashboard"
                        print(f"\n{Colors.WARNING}⚠️  {name} process stopped unexpectedly{Colors.ENDC}")
                        self.running = False
                        break
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            pass
    
    def stop_all(self):
        """Stop all running processes."""
        print(f"\n\n{Colors.WARNING}🛑 Stopping PhantomGuard...{Colors.ENDC}\n")
        
        for i, proc in enumerate(self.processes):
            name = "Core" if i == 0 else "Dashboard"
            try:
                print(f"   Stopping {name}...", end=" ")
                proc.terminate()
                proc.wait(timeout=5)
                print(f"{Colors.OKGREEN}✓{Colors.ENDC}")
            except subprocess.TimeoutExpired:
                print(f"{Colors.WARNING}(forced){Colors.ENDC}")
                proc.kill()
            except Exception as e:
                print(f"{Colors.FAIL}✗ {e}{Colors.ENDC}")
        
        print(f"\n{Colors.OKGREEN}✅ PhantomGuard stopped{Colors.ENDC}\n")
    
    def run(self):
        """Main run method."""
        self.print_banner()
        
        # Pre-flight checks
        print(f"{Colors.BOLD}Pre-flight Checks:{Colors.ENDC}\n")
        
        if not self.check_dependencies():
            sys.exit(1)
        
        if not self.check_config():
            sys.exit(1)
        
        self.setup_directories()
        self.generate_decoys()
        
        print("\n" + "=" * 60 + "\n")
        
        # Start components
        core_process = self.start_core()
        if not core_process:
            print(f"\n{Colors.FAIL}Failed to start core system. Check logs for details.{Colors.ENDC}\n")
            sys.exit(1)
        
        self.processes.append(core_process)
        
        dashboard_process = self.start_dashboard()
        if dashboard_process:
            self.processes.append(dashboard_process)
        else:
            print(f"{Colors.WARNING}Dashboard failed, but core is running{Colors.ENDC}")
        
        # Monitor
        self.running = True
        
        # Setup signal handlers
        def signal_handler(sig, frame):
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        self.monitor_processes()
        self.stop_all()


def main():
    """Entry point."""
    launcher = PhantomGuardLauncher()
    launcher.run()


if __name__ == "__main__":
    main()
