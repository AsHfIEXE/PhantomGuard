You are coding for PhantomGuard --- a lightweight, deception-first threat detection system for solo developers. Follow these rules strictly:

#### ✅ Core Principles

-   Finish by Oct 29, 2025 --- prioritize MUST-HAVE features only (decoys, inotify watcher, scorer, Telegram alerts, nftables block, Streamlit UI, install script).
-   No demos, no filler --- every line must contribute to a working, stealthy, autonomous system.
-   Deception realism > complexity: fake files must look real (timestamps, size, names like `id_rsa`, `.env`, `backup.sql`).

#### 📁 Project Structure & Tech Stack

-   Language: Python 3.10+, type hints, minimal deps (`watchdog`, `aiohttp`, `python-telegram-bot`, `streamlit`, `pydantic`).
-   Modules:
    -   `phantomgen/`: generate decoys (files, SSH keys, fake cron)
    -   `sensors/`: `inotify` watcher (primary), optional `auditd`
    -   `processor/`: rule-based scorer + playbook (no ML unless Day 10+)
    -   `alerting/`: Telegram + HMAC-signed webhook + rate-limiting
    -   `ui/`: Streamlit dashboard (view events, mark FP)
    -   `tools/`: `install.sh`, `systemd` unit, demo simulator
-   Run natively on Linux; Windows-compatible only where trivial.

#### 🔒 Security & Safety

-   Never hardcode secrets --- use config + file perms (`600`) or keyring.
-   Blocker (`nftables`) must support `dry_run=True` and require explicit enable.
-   All file writes/executions from decoys must be non-functional traps (e.g., `svchost_backup.exe` is unreadable or fake).
-   Include a kill-switch to disable auto-response during dev.

#### 📝 Code Quality

-   Add docstrings for public functions.
-   Handle exceptions (especially in `sensors/` and `alerting/`).
-   Log to `/var/log/phantomguard/` in structured JSON.
-   Prefer readability and correctness over cleverness.

#### 🚫 Avoid

-   Heavy frameworks (Django, FastAPI unless needed for honeypot)
-   Unnecessary encryption on decoys (makes them look *too* protected)
-   Default honeypot banners or obvious names like `honey.txt`

You are helping build a spooky but practical ghost that watches, lures, and quietly locks out attackers --- not a toy.