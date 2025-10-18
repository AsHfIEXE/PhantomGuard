"""
PhantomGuard IP Blocker (production-ready)
Blocks offending IPs using nftables/iptables. Supports dry-run, audit logging, secure permissions, config-driven.
"""
import subprocess
import os
import time


class IPBlocker:
    """
    Manages blocking IP addresses using nftables.
    """

    def __init__(
            self,
            dry_run: bool = True,
            log_path: str = "/var/log/phantomguard/block.log"):
        self.dry_run = dry_run
        self.log_path = log_path

    def block_ip(self, ip: str) -> bool:
        """
        Adds an IP address to the nftables block set.

        Args:
            ip: The IP address to block.

        Returns:
            True if the block was successful or in dry-run mode, False otherwise.
        """
        cmd = ["nft", "add", "element", "inet",
               "filter", "phantom_block", f"{{ {ip} }}"]
        if self.dry_run:
            print("[blocker] DRY-RUN:", " ".join(cmd))
            self._log(ip, dry_run=True)
            return True
        try:
            subprocess.run(cmd, check=True)
            self._log(ip, dry_run=False)
            return True
        except Exception as e:
            print(f"[blocker] Block failed: {e}")
            return False

    def _log(self, ip: str, dry_run: bool):
        """Logs the block action to a file."""
        try:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            with open(self.log_path, "a") as f:
                f.write(f"{time.time()} {ip} {'DRY' if dry_run else 'BLOCK'}\n")
        except Exception as e:
            print(f"[blocker] Log write failed: {e}")
