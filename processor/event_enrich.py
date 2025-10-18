"""
PhantomGuard Event Enrichment
Adds process ID, user, and source IP to events.
"""
import os
import getpass
import socket
from typing import Dict


def enrich_event(event: Dict) -> Dict:
    event['pid'] = os.getpid()
    event['user'] = getpass.getuser()
    event['source_ip'] = event.get(
        'remote', socket.gethostbyname(
            socket.gethostname()))
    return event
