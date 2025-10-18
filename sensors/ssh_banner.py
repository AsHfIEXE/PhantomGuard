"""
PhantomGuard Fake SSH Banner Listener
Listens on a port and sends a fake SSH banner to all connections, logging each as an event.
"""
import socket
import threading
import time
from typing import Callable

FAKE_BANNER = b'SSH-2.0-OpenSSH_7.9p1 PhantomGuard\r\n'


class SSHBannerServer(threading.Thread):
    def __init__(self, emit: Callable, port: int = 2222):
        super().__init__(daemon=True)
        self.emit = emit
        self.port = port
        self.running = True

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', self.port))
            s.listen(100)
            print(f"[SSH Banner] Listening on port {self.port}")
            while self.running:
                try:
                    conn, addr = s.accept()
                    conn.sendall(FAKE_BANNER)
                    event = {
                        'event_type': 'ssh_banner',
                        'remote': addr[0],
                        'port': addr[1],
                        'ts': time.time(),
                    }
                    self.emit(event)
                    conn.close()
                except Exception:
                    continue

    def stop(self):
        self.running = False
