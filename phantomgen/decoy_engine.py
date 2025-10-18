import os
import random
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

DEFAULT_DECOYS = [
    {"path": "/tmp/.ssh/id_rsa", "type": "file", "size_kb": 2},
    {"path": "/tmp/.env", "type": "file", "size_kb": 1},
    {"path": "/tmp/backup.sql", "type": "file", "size_kb": 8},
    {"path": "/tmp/.aws/credentials", "type": "honeytoken", "size_kb": 1},
    {"path": "/tmp/fake_cron", "type": "cron", "size_kb": 1},
]


def create_decoy_file(
        path: str,
        size_kb: int = 4,
        owner_uid: Optional[int] = None) -> str:
    """Create a decoy file with random content and plausible mtime/ownership."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "wb") as f:
        f.write(os.urandom(size_kb * 1024))
    ts = time.time() - random.randint(3600, 86400 * 30)
    os.utime(p, (ts, ts))
    if owner_uid is not None:
        chown_func = getattr(os, 'chown', None)
        if chown_func:
            try:
                chown_func(p, owner_uid, -1)
            except PermissionError:
                pass  # best effort
    return str(p)


def create_honeytoken(
        path: str,
        token_type: str = "aws",
        owner_uid: Optional[int] = None) -> str:
    """Create a honeytoken file (e.g., fake AWS credentials)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if token_type == "aws":
        content = "[default]\naws_access_key_id=FAKEKEY1234567890\naws_secret_access_key=FAKESECRET1234567890\n"
    else:
        content = "honeytoken=FAKE_TOKEN"
    with open(p, "w") as f:
        f.write(content)
    ts = time.time() - random.randint(3600, 86400 * 30)
    os.utime(p, (ts, ts))
    if owner_uid is not None:
        chown_func = getattr(os, 'chown', None)
        if chown_func:
            try:
                chown_func(p, owner_uid, -1)
            except PermissionError:
                pass
    return str(p)


def create_fake_cron(path: str, owner_uid: Optional[int] = None) -> str:
    """Create a fake cron job file."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    content = "* * * * * root /usr/bin/fakejob # PhantomGuard decoy\n"
    with open(p, "w") as f:
        f.write(content)
    ts = time.time() - random.randint(3600, 86400 * 30)
    os.utime(p, (ts, ts))
    if owner_uid is not None:
        chown_func = getattr(os, 'chown', None)
        if chown_func:
            try:
                chown_func(p, owner_uid, -1)
            except PermissionError:
                pass
    return str(p)


def load_decoy_config(
        config_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Loads decoy configurations from a JSON file.

    Args:
        config_path: Path to the JSON configuration file.

    Returns:
        A list of decoy dictionaries.
    """
    if config_path and os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
            return config.get("decoys", DEFAULT_DECOYS)
    return DEFAULT_DECOYS


def main(config_path: Optional[str] = None):
    """Main CLI entrypoint for decoy generation."""
    decoys = load_decoy_config(config_path)
    for d in decoys:
        t = d.get("type", "file")
        path = d["path"]
        size = d.get("size_kb", 4)
        if t == "file":
            print(f"[decoy] {create_decoy_file(path, size)}")
        elif t == "honeytoken":
            print(f"[honeytoken] {create_honeytoken(path)}")
        elif t == "cron":
            print(f"[cron] {create_fake_cron(path)}")
        else:
            print(f"[skip] Unknown decoy type: {t} for {path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PhantomGuard Decoy Engine")
    parser.add_argument(
        "--config",
        help="Path to decoy config JSON",
        default=None)
    args = parser.parse_args()
    main(args.config)
