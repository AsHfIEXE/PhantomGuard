#!/usr/bin/env python3
"""
PhantomGuard Attack Simulator
Simulates various attack patterns to test decoy detection.
"""
import time
import sys
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any

class AttackSimulator:
    """Simulates different types of attacks on decoys."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.attacks_run = []
    
    def log(self, message: str):
        """Print a log message."""
        if self.verbose:
            print(f"[Simulator] {message}")
    
    def simulate_credential_theft(self):
        """Simulate an attacker reading credential files."""
        self.log("🔑 Simulating credential theft...")
        
        targets = [
            "/tmp/.ssh/id_rsa",
            "/tmp/.aws/credentials",
            "/tmp/.env",
        ]
        
        for target in targets:
            if Path(target).exists():
                try:
                    self.log(f"  Reading {target}")
                    with open(target, 'r') as f:
                        _ = f.read()
                    time.sleep(1)
                    self.attacks_run.append(("credential_theft", target))
                except Exception as e:
                    self.log(f"  Error reading {target}: {e}")
            else:
                self.log(f"  ⚠ Decoy not found: {target}")
    
    def simulate_backup_exfiltration(self):
        """Simulate an attacker accessing backup files."""
        self.log("💾 Simulating backup file access...")
        
        targets = [
            "/tmp/backup.sql",
            "/tmp/db_backup.sql",
        ]
        
        for target in targets:
            if Path(target).exists():
                try:
                    self.log(f"  Accessing {target}")
                    with open(target, 'rb') as f:
                        _ = f.read(1024)  # Read first KB
                    time.sleep(1)
                    self.attacks_run.append(("backup_exfiltration", target))
                except Exception as e:
                    self.log(f"  Error accessing {target}: {e}")
            else:
                self.log(f"  ⚠ Decoy not found: {target}")
    
    def simulate_persistence_check(self):
        """Simulate checking for persistence mechanisms."""
        self.log("⚙️ Simulating persistence mechanism check...")
        
        targets = [
            "/tmp/fake_cron",
        ]
        
        for target in targets:
            if Path(target).exists():
                try:
                    self.log(f"  Reading {target}")
                    with open(target, 'r') as f:
                        _ = f.read()
                    time.sleep(1)
                    self.attacks_run.append(("persistence_check", target))
                except Exception as e:
                    self.log(f"  Error reading {target}: {e}")
            else:
                self.log(f"  ⚠ Decoy not found: {target}")
    
    def simulate_config_discovery(self):
        """Simulate discovering configuration files."""
        self.log("📝 Simulating config file discovery...")
        
        search_dirs = [
            "/tmp/.config",
            "/tmp/.decoy-home/user/.config",
        ]
        
        for search_dir in search_dirs:
            if Path(search_dir).exists():
                try:
                    self.log(f"  Listing {search_dir}")
                    files = list(Path(search_dir).rglob("*"))
                    for f in files[:5]:  # Check first 5 files
                        if f.is_file():
                            self.log(f"    Found: {f}")
                            with open(f, 'rb') as fh:
                                _ = fh.read(512)
                            time.sleep(0.5)
                            self.attacks_run.append(("config_discovery", str(f)))
                except Exception as e:
                    self.log(f"  Error in {search_dir}: {e}")
            else:
                self.log(f"  ⚠ Directory not found: {search_dir}")
    
    def simulate_ssh_key_manipulation(self):
        """Simulate SSH key access and manipulation attempts."""
        self.log("🔐 Simulating SSH key manipulation...")
        
        ssh_dir = Path("/tmp/.ssh")
        if ssh_dir.exists():
            try:
                # List SSH directory
                self.log(f"  Listing {ssh_dir}")
                files = list(ssh_dir.glob("*"))
                
                for f in files:
                    if f.is_file() and 'id_rsa' in f.name:
                        self.log(f"    Checking permissions on {f}")
                        stat_info = f.stat()
                        
                        # Try to read the key
                        self.log(f"    Reading {f}")
                        with open(f, 'r') as fh:
                            _ = fh.read()
                        
                        time.sleep(1)
                        self.attacks_run.append(("ssh_key_access", str(f)))
            except Exception as e:
                self.log(f"  Error: {e}")
        else:
            self.log(f"  ⚠ SSH directory not found: {ssh_dir}")
    
    def simulate_network_scan(self):
        """Simulate a simple network scan."""
        self.log("🌐 Simulating network scan...")
        
        # Try to connect to honeypot ports
        ports = [2222, 8080]  # SSH banner and HTTP honeypot
        
        for port in ports:
            try:
                import socket
                self.log(f"  Scanning port {port}")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('localhost', port))
                
                if result == 0:
                    self.log(f"    Port {port} is open")
                    # Try to read banner
                    try:
                        banner = sock.recv(1024)
                        self.log(f"    Banner: {banner[:50]}")
                    except:
                        pass
                else:
                    self.log(f"    Port {port} is closed")
                
                sock.close()
                time.sleep(1)
                self.attacks_run.append(("network_scan", f"localhost:{port}"))
            except Exception as e:
                self.log(f"  Error scanning port {port}: {e}")
    
    def simulate_file_enumeration(self):
        """Simulate file enumeration in common directories."""
        self.log("📂 Simulating file enumeration...")
        
        dirs = ["/tmp", "/tmp/phantomguard-decoys"]
        
        for directory in dirs:
            if Path(directory).exists():
                try:
                    self.log(f"  Enumerating {directory}")
                    files = list(Path(directory).glob("*"))[:10]
                    
                    for f in files:
                        if f.is_file() and any(keyword in f.name.lower() 
                                              for keyword in ['secret', 'password', 'backup', 'key', '.env']):
                            self.log(f"    Interesting file: {f}")
                            try:
                                with open(f, 'rb') as fh:
                                    _ = fh.read(256)
                                time.sleep(0.3)
                                self.attacks_run.append(("file_enumeration", str(f)))
                            except:
                                pass
                except Exception as e:
                    self.log(f"  Error: {e}")
    
    def run_all_attacks(self):
        """Run all attack simulations."""
        self.log("=" * 60)
        self.log("Starting PhantomGuard Attack Simulation")
        self.log("=" * 60)
        
        attacks = [
            self.simulate_credential_theft,
            self.simulate_ssh_key_manipulation,
            self.simulate_backup_exfiltration,
            self.simulate_config_discovery,
            self.simulate_persistence_check,
            self.simulate_file_enumeration,
            self.simulate_network_scan,
        ]
        
        for attack in attacks:
            try:
                attack()
                time.sleep(2)  # Wait between attack types
            except Exception as e:
                self.log(f"Attack failed: {e}")
        
        self.log("=" * 60)
        self.log(f"Simulation complete: {len(self.attacks_run)} actions performed")
        self.log("=" * 60)
        self.log("\nNext steps:")
        self.log("1. Check logs: cat /var/log/phantomguard/alerts.log")
        self.log("2. View dashboard: streamlit run ui/dashboard.py")
        self.log("3. Check alerts in Telegram (if configured)")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="PhantomGuard Attack Simulator")
    parser.add_argument('--quiet', '-q', action='store_true', 
                       help='Suppress verbose output')
    parser.add_argument('--attack', '-a', 
                       choices=['credential', 'backup', 'persistence', 
                               'config', 'ssh', 'scan', 'enum', 'all'],
                       default='all',
                       help='Specific attack to simulate')
    args = parser.parse_args()
    
    simulator = AttackSimulator(verbose=not args.quiet)
    
    attack_map = {
        'credential': simulator.simulate_credential_theft,
        'backup': simulator.simulate_backup_exfiltration,
        'persistence': simulator.simulate_persistence_check,
        'config': simulator.simulate_config_discovery,
        'ssh': simulator.simulate_ssh_key_manipulation,
        'scan': simulator.simulate_network_scan,
        'enum': simulator.simulate_file_enumeration,
        'all': simulator.run_all_attacks,
    }
    
    attack_map[args.attack]()


if __name__ == "__main__":
    main()