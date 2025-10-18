

You are helping develop **PhantomGuard**: a lightweight, deception-first threat detection system for solo developers and personal laptops.  

It must be **real, stealthy, autonomous**, and **production-grade**---not a demo or proof-of-concept.

## 🎯 Core Philosophy

- **Deception is the sensor**: High-fidelity decoys (files, tokens, services) are the primary detection mechanism.

- **Autonomy with safety**: The system can alert, log, and block---but always with dry-run support, a kill-switch, and least-privilege execution.

- **Finishable scope**: Prioritize simplicity, correctness, and integration over novelty. Avoid over-engineering.

- **Spooky but practical**: It should feel like a silent ghost---present, observant, and quietly disruptive to attackers.

## 📁 Architecture & Modules

Respect this structure and its responsibilities:

```

phantomgen/     # Generates realistic decoys: files, SSH keys, fake cron, fake HTTP endpoints

sensors/        # Efficient watchers: inotify (primary), optional auditd or eBPF for syscall tracing

processor/      # Normalizes events, applies rule-based scoring, executes playbooks

alerting/       # Secure alerting: Telegram + HMAC-signed webhooks + rate-limiting

ui/             # Minimal Streamlit dashboard: view events, scores, acknowledge false positives

tools/          # install.sh, systemd unit, demo simulator, packaging

```

## ⚙️ Technical Constraints

- **Language**: Python 3.10+, with type hints and minimal dependencies (`watchdog`, `python-telegram-bot`, `streamlit`, `pydantic`).

- **Platform**: Native on Linux; Windows compatibility only where trivial and safe.

- **Privilege model**: Sensors run unprivileged. Only the response module (`nftables`/`iptables`) uses `sudo`---with strict command whitelisting.

- **Packaging**: Single `install.sh`, `systemd` service, and config-driven setup. No Docker in production (dev container OK).

## 🔒 Security & Operational Rules

- **Secrets**: Never hardcode. Use file-based config with `600` permissions or system keyring.

- **Decoy realism**: Files must have believable names (`id_rsa`, `.env`, `backup.sql`), sizes (1--10 KB), and timestamps (1h--30d old).

- **Non-functional traps**: Decoy executables/services must **not** be functional---only lures.

- **Logging**: Structured JSON to `/var/log/phantomguard/`. Forensic captures (if enabled) must be encrypted at rest.

- **Kill-switch**: A config flag (`auto_response_enabled: false`) must disable all blocking actions during development.

## ✍️ Code Quality Expectations

- Prefer **readability and correctness** over cleverness.

- Add minimal but clear docstrings for public functions.

- Handle exceptions gracefully---especially in sensors and alerting.

- Include unit tests for scoring logic and playbook actions.

- Validate all external inputs (e.g., IPs before blocking).

## 🚫 Strictly Avoid

- Heavy frameworks (Django, FastAPI) unless absolutely necessary for a honeypot.

- Obvious decoy names (`honey.txt`, `fake_token.txt`).

- Default or fingerprintable honeypot banners.

- Unnecessary encryption on decoy files (makes them look "too protected" and less believable).

- ML/anomaly models unless explicitly requested---start with deterministic rules.

## 💡 When Generating Code

Assume this system will face real attackers. Every line must contribute to **detection**, **response**, or **forensic value**. Be efficient, silent, and precise.

> "It's not a honeypot. It's a ghost that watches, lures, and locks the door behind you."

---
You are helping build a spooky but practical ghost that watches, lures, and quietly locks out attackers --- not a toy.