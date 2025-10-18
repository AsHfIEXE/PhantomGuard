"""
PhantomGuard Persistent Event Queue
File-backed event queue for reliability and crash recovery.
"""
import json
import os
import threading
from queue import Queue, Empty, Queue as TypingQueue
from typing import Any


class PersistentQueue:
    def __init__(self, path: str, maxsize: int = 1000):
        self.path = path
        self.queue: TypingQueue[Any] = Queue(maxsize=maxsize)
        self.lock: threading.Lock = threading.Lock()
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                for line in f:
                    try:
                        self.queue.put_nowait(json.loads(line.strip()))
                    except Exception:
                        continue

    def put(self, item: Any):
        with self.lock:
            self.queue.put(item)
            with open(self.path, 'a') as f:
                f.write(json.dumps(item) + '\n')

    def get(self, timeout: float = 1.0):
        try:
            return self.queue.get(timeout=timeout)
        except Empty:
            return None

    def task_done(self):
        self.queue.task_done()
