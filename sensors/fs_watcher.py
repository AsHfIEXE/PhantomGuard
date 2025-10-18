"""
PhantomGuard Filesystem Watcher (production-ready)
Monitors decoy paths using watchdog/inotify, normalizes events, and emits to event bus (stub).
Config-driven, robust error handling, docstrings, and CLI.
"""
import time
import json
import argparse
import os
from pathlib import Path
from typing import List, Any, Protocol, Optional, Union
import importlib

# Optional dependency: watchdog. Provide lightweight fallbacks when
# unavailable to keep imports safe.
try:
    watchdog_observers = importlib.import_module('watchdog.observers')
    watchdog_events = importlib.import_module('watchdog.events')
    Observer = getattr(watchdog_observers, 'Observer')
    FileSystemEventHandler = getattr(watchdog_events, 'FileSystemEventHandler')
    FileSystemEvent = getattr(watchdog_events, 'FileSystemEvent')
    WATCHDOG_AVAILABLE = True
except Exception:
    WATCHDOG_AVAILABLE = False
    # Minimal fallbacks to preserve API surface used elsewhere

    class _FallbackFileSystemEvent:
    class FileSystemEvent:
        def __init__(self, src_path: str, event_type: str, is_directory: bool = False):
            self.src_path = src_path
            self.event_type = event_type
            self.is_directory = is_directory

    class _FallbackFileSystemEventHandler(Protocol):
    class FileSystemEventHandler(Protocol):
        def on_any_event(self, event: Any) -> None:
            pass

    class _FallbackObserver:
    class Observer:
        def __init__(self) -> None:
            pass

        def schedule(self, handler: Any, path: str, recursive: bool = False) -> None:
            pass

        def start(self) -> None:
            # runtime note: filesystem watching disabled when watchdog is not
            # installed
            print('[warn] watchdog not installed; fs_watcher will be a no-op')

        def stop(self) -> None:
            pass

        def join(self) -> None:
            pass
    FileSystemEvent = _FallbackFileSystemEvent

# Define a union type for both real and fallback events
FSEvent = Union[FileSystemEvent, _FallbackFileSystemEvent]


class EventBus:
    """A generic event bus interface for emitting events."""

    def emit(self, event: dict) -> None:
        """Emit an event to subscribers."""
        raise NotImplementedError


class FSEventLike(Protocol):
    """Protocol for filesystem events."""
    src_path: str
    event_type: str
    is_directory: bool

class DecoyEventHandler(FileSystemEventHandler):  # type: ignore
    """
    Handles filesystem events and normalizes them for the event bus.
    """

    def __init__(self, event_bus: EventBus) -> None:
        super().__init__()  # type: ignore
        self.event_bus = event_bus

    def on_any_event(self, event: FSEventLike) -> None:
        """Handle any filesystem event by normalizing and emitting it."""
        try:
            payload = {
                "path": event.src_path,
                "event_type": event.event_type,
                "is_dir": event.is_directory,
                "ts": time.time(),
            }
            self.event_bus.emit(payload)
        except Exception as e:
            print(f"[error] Failed to process event: {e}")


def main(paths: List[str]):
    """
    Main CLI entrypoint for the filesystem watcher.
    Initializes and runs the observer on the specified paths.
    """

    class PrintBus(EventBus):
        """A simple event bus that prints events to stdout."""

        def emit(self, event: dict):
            print(json.dumps(event))

    obs = Observer()
    handler = DecoyEventHandler(PrintBus())
    for p in paths:
        # Ensure parent directory exists for watching
        parent_dir = str(Path(p).parent)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        obs.schedule(handler, parent_dir, recursive=True)
    obs.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="PhantomGuard Filesystem Watcher")
    parser.add_argument("paths", nargs="+", help="Paths to watch")
    args = parser.parse_args()
    main(args.paths)
