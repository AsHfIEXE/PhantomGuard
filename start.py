#!/usr/bin/env python3
"""
PhantomGuard All-in-One Launcher
Automatically detects, builds, and runs:
  1. PhantomGuard Core (detection system)
  2. REST API (http://localhost:5000)
  3. React UI (http://localhost:5173)

Just run: python start.py
"""
import subprocess
import sys
import time
import signal
import os
from pathlib import Path
import json

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class PhantomGuardLauncher:
    """All-in-one launcher for PhantomGuard + API + React UI."""
    
    def __init__(self):
        self.processes = []
        self.running = False
        self.ui_dir = None
    
    def print_banner(self):
        """Print startup banner."""
        banner = f"""
{Colors.HEADER}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║               👻 PhantomGuard v2.0                       ║
║          Deception-Based Threat Detection                ║
║                                                           ║
║        🚀 All-in-One Launcher (Core + API + UI)         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
{Colors.ENDC}
"""
        print(banner)
    
    def find_ui_directory(self) -> bool:
        """Find React UI directory."""
        print(f"{Colors.OKBLUE}🔍 Looking for React UI...{Colors.ENDC}\n")
        
        # Check possible locations
        possible_dirs = [
            Path('ui'),
            Path('phantomguard-ui'),
            Path('dashboard'),
            Path('.'),
        ]
        
        for potential_dir in possible_dirs:
            package_json = potential_dir / 'package.json'
            
            if package_json.exists():
                try:
                    with open(package_json) as f:
                        content = json.load(f)
                        if 'react' in str(content).lower() or 'vite' in str(content).lower():
                            self.ui_dir = potential_dir
                            print(f"{Colors.OKGREEN}✓{Colors.ENDC} Found React app at: {Colors.OKBLUE}{potential_dir}{Colors.ENDC}")
                            return True
                except:
                    pass
        
        print(f"{Colors.WARNING}⚠️  React UI not found{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Expected locations:{Colors.ENDC}")
        print(f"  • ./ui/package.json")
        print(f"  • ./phantomguard-ui/package.json")
        print(f"  • ./dashboard/package.json")
        print(f"\n{Colors.WARNING}To fix:{Colors.ENDC}")
        print(f"  1. Place your React app in ./ui folder")
        print(f"  2. Run: python start.py\n")
        return False
    
    def check_config(self) -> bool:
        """Check if configuration exists."""
        config_path = Path('config.json')
        
        if not config_path.exists():
            print(f"{Colors.FAIL}❌ config.json not found!{Colors.ENDC}")
            print(f"\n{Colors.BOLD}Quick fix:{Colors.ENDC}")
            print(f"  cp config.json.example config.json")
            print(f"  nano config.json  # Edit Telegram settings\n")
            return False
        
        try:
            with open(config_path) as f:
                config = json.load(f)
            
            if config['telegram']['bot_token'] == 'YOUR_TELEGRAM_BOT_TOKEN':
                print(f"{Colors.WARNING}⚠️  Telegram not configured (alerts will fail){Colors.ENDC}")
                print(f"   Get token from @BotFather on Telegram\n")
            
            print(f"{Colors.OKGREEN}✓{Colors.ENDC} Configuration valid")
            return True
        except Exception as e:
            print(f"{Colors.FAIL}❌ Invalid config.json: {e}{Colors.ENDC}\n")
            return False
    
    def setup_directories(self):
        """Create necessary directories."""
        dirs = ['logs/phantomguard', 'api', '/tmp/.ssh', '/tmp/phantomguard-decoys']
        
        for directory in dirs:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
            except PermissionError:
                if not directory.startswith('/tmp'):
                    print(f"{Colors.WARNING}⚠️  Cannot create {directory}{Colors.ENDC}")
        
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} Directories ready")
    
    def generate_decoys(self):
        """Generate decoy files if missing."""
        print(f"\n{Colors.OKBLUE}📁 Checking decoys...{Colors.ENDC}")
        
        basic_decoys = ['/tmp/.ssh/id_rsa', '/tmp/.env', '/tmp/backup.sql']
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
            print(f"{Colors.OKGREEN}✓{Colors.ENDC} Decoys exist")
    
    def check_ui_dependencies(self) -> bool:
        """Check if npm and node are installed."""
        try:
            subprocess.run(['npm', '--version'], capture_output=True, check=True)
            subprocess.run(['node', '--version'], capture_output=True, check=True)
            print(f"{Colors.OKGREEN}✓{Colors.ENDC} Node.js and npm found")
            return True
        except Exception:
            print(f"{Colors.FAIL}❌ Node.js/npm not installed!{Colors.ENDC}")
            print(f"\n{Colors.WARNING}Install from: https://nodejs.org/{Colors.ENDC}\n")
            return False
    
    def check_ui_built(self) -> bool:
        """Check if React UI is already built."""
        if not self.ui_dir:
            return False
        
        dist_dir = self.ui_dir / 'dist'
        return dist_dir.exists() and list(dist_dir.glob('*'))
    
    def build_ui(self) -> bool:
        """Build React UI if not already built."""
        if not self.ui_dir:
            return False
        
        if self.check_ui_built():
            print(f"{Colors.OKGREEN}✓{Colors.ENDC} React UI already built")
            return True
        
        print(f"\n{Colors.OKBLUE}🔨 Building React UI...{Colors.ENDC}")
        print(f"   This may take 1-2 minutes on first run...")
        
        try:
            # Install dependencies
            print(f"   Installing npm packages...")
            subprocess.run(
                ['npm', 'install'],
                cwd=str(self.ui_dir),
                capture_output=True,
                timeout=300
            )
            
            # Build
            print(f"   Building...")
            subprocess.run(
                ['npm', 'run', 'build'],
                cwd=str(self.ui_dir),
                capture_output=True,
                timeout=300,
                check=True
            )
            
            print(f"{Colors.OKGREEN}✓{Colors.ENDC} React UI built successfully")
            return True
        except subprocess.TimeoutExpired:
            print(f"{Colors.FAIL}❌ Build timed out{Colors.ENDC}")
            return False
        except Exception as e:
            print(f"{Colors.FAIL}❌ Build failed: {e}{Colors.ENDC}")
            return False
    
    def start_core(self) -> bool:
        """Start PhantomGuard core."""
        print(f"\n{Colors.OKBLUE}🚀 Starting PhantomGuard Core...{Colors.ENDC}")
        
        try:
            process = subprocess.Popen(
                [sys.executable, '-u', 'phantomguard.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            time.sleep(2)
            
            if process.poll() is None:
                print(f"{Colors.OKGREEN}✓{Colors.ENDC} Core started (PID: {process.pid})")
                self.processes.append(('Core', process))
                return True
            else:
                print(f"{Colors.FAIL}❌ Core failed to start{Colors.ENDC}")
                return False
        except Exception as e:
            print(f"{Colors.FAIL}❌ Core start error: {e}{Colors.ENDC}")
            return False
    
    def start_api(self) -> bool:
        """Start REST API server."""
        print(f"{Colors.OKBLUE}🔌 Starting REST API...{Colors.ENDC}")
        
        try:
            process = subprocess.Popen(
                [sys.executable, '-u', 'api/server.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            time.sleep(2)
            
            if process.poll() is None:
                print(f"{Colors.OKGREEN}✓{Colors.ENDC} API started (PID: {process.pid})")
                print(f"   URL: {Colors.OKBLUE}http://localhost:5000{Colors.ENDC}")
                self.processes.append(('API', process))
                return True
            else:
                print(f"{Colors.FAIL}❌ API failed to start{Colors.ENDC}")
                return False
        except Exception as e:
            print(f"{Colors.FAIL}❌ API start error: {e}{Colors.ENDC}")
            return False
    
    def start_ui(self) -> bool:
        """Start React UI."""
        if not self.ui_dir:
            print(f"{Colors.WARNING}⚠️  React UI not found, skipping...{Colors.ENDC}")
            return False
        
        print(f"{Colors.OKBLUE}🎨 Starting React UI...{Colors.ENDC}")
        
        try:
            # Check if dist exists (for serving built app)
            dist_dir = self.ui_dir / 'dist'
            if dist_dir.exists():
                # Serve built app
                print(f"   Serving built UI with npm...")
                process = subprocess.Popen(
                    ['npm', 'run', 'preview'],
                    cwd=str(self.ui_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True
                )
            else:
                # Dev server
                print(f"   Starting dev server...")
                process = subprocess.Popen(
                    ['npm', 'run', 'dev'],
                    cwd=str(self.ui_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True
                )
            
            time.sleep(3)
            
            if process.poll() is None:
                print(f"{Colors.OKGREEN}✓{Colors.ENDC} React UI started (PID: {process.pid})")
                print(f"   URL: {Colors.OKBLUE}http://localhost:5173{Colors.ENDC}")
                self.processes.append(('React UI', process))
                return True
            else:
                print(f"{Colors.FAIL}❌ React UI failed to start{Colors.ENDC}")
                return False
        except Exception as e:
            print(f"{Colors.FAIL}❌ React UI start error: {e}{Colors.ENDC}")
            return False
    
    def print_ready_message(self):
        """Print ready message."""
        print(f"\n{Colors.OKGREEN}✅ PhantomGuard is RUNNING!{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Access Points:{Colors.ENDC}")
        print(f"  👻 PhantomGuard Core: Running in background")
        print(f"  🔌 REST API: {Colors.OKBLUE}http://localhost:5000{Colors.ENDC}")
        print(f"  🎨 Dashboard UI: {Colors.OKBLUE}http://localhost:5173{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Quick Actions:{Colors.ENDC}")
        print(f"  • Test system: {Colors.OKBLUE}python demo/attack_simulator.py{Colors.ENDC}")
        print(f"  • View logs: {Colors.OKBLUE}tail -f logs/phantomguard/phantomguard.log{Colors.ENDC}")
        print(f"  • Stop: {Colors.WARNING}Press Ctrl+C{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Next Step:{Colors.ENDC}")
        print(f"  Open {Colors.OKBLUE}http://localhost:5173{Colors.ENDC} in your browser")
        print("\n" + "=" * 60 + "\n")
    
    def monitor(self):
        """Monitor running processes."""
        try:
            while self.running:
                for name, proc in self.processes:
                    if proc.poll() is not None:
                        print(f"\n{Colors.WARNING}⚠️  {name} stopped unexpectedly{Colors.ENDC}")
                        self.running = False
                        break
                
                time.sleep(2)
        except KeyboardInterrupt:
            pass
    
    def stop_all(self):
        """Stop all processes gracefully."""
        print(f"\n\n{Colors.WARNING}🛑 Stopping PhantomGuard...{Colors.ENDC}\n")
        
        for name, proc in reversed(self.processes):
            try:
                print(f"   Stopping {name}...", end=" ")
                proc.terminate()
                proc.wait(timeout=5)
                print(f"{Colors.OKGREEN}✓{Colors.ENDC}")
            except subprocess.TimeoutExpired:
                print(f"{Colors.WARNING}(forced){Colors.ENDC}")
                proc.kill()
            except Exception as e:
                print(f"{Colors.FAIL}✗{Colors.ENDC}")
        
        print(f"\n{Colors.OKGREEN}✅ PhantomGuard stopped{Colors.ENDC}\n")
    
    def run(self):
        """Main run method."""
        self.print_banner()
        
        print(f"{Colors.BOLD}Pre-flight Checks:{Colors.ENDC}\n")
        
        # Check config
        if not self.check_config():
            sys.exit(1)
        
        # Find UI
        if not self.find_ui_directory():
            print(f"\n{Colors.WARNING}Continuing without UI...{Colors.ENDC}\n")
        
        # Setup directories
        self.setup_directories()
        self.generate_decoys()
        
        # Build UI if found
        if self.ui_dir:
            if not self.check_ui_dependencies():
                print(f"{Colors.WARNING}Continuing without UI...{Colors.ENDC}")
                self.ui_dir = None
            else:
                if not self.build_ui():
                    print(f"{Colors.WARNING}Continuing without UI...{Colors.ENDC}")
                    self.ui_dir = None
        
        print("\n" + "=" * 60 + "\n")
        
        # Start services
        if not self.start_core():
            print(f"{Colors.FAIL}Failed to start core. Exiting.{Colors.ENDC}\n")
            sys.exit(1)
        
        if not self.start_api():
            print(f"{Colors.WARNING}API failed, but core is running{Colors.ENDC}")
        
        if self.ui_dir and not self.start_ui():
            print(f"{Colors.WARNING}UI failed, but core and API are running{Colors.ENDC}")
        
        # Ready message
        self.print_ready_message()
        
        # Monitor
        self.running = True
        
        def signal_handler(sig, frame):
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        self.monitor()
        self.stop_all()


def main():
    """Entry point."""
    launcher = PhantomGuardLauncher()
    launcher.run()


if __name__ == "__main__":
    main()