import os
import random
import time
from pathlib import Path
from typing import Optional


def create_decoy(
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


if __name__ == "__main__":
    # Example decoys
    print(create_decoy("/tmp/.ssh/id_rsa", size_kb=2))
    print(create_decoy("/tmp/.env", size_kb=1))
    print(create_decoy("/tmp/backup.sql", size_kb=8))
