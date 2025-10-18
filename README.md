# PhantomGuard
Lightweight, deception-based threat detection for solo developers.

This project provides a stealthy, autonomous system for detecting and responding to threats on a personal machine using a variety of deception techniques.

## Quickstart

1.  **Configure:** Copy `config.json.example` to `config.json` and fill in your details (especially Telegram credentials).
2.  **Install:** Run `sudo ./tools/install.sh`. This sets up a virtual environment, installs dependencies, and configures the systemd service.
3.  **Run:** Start the service with `sudo systemctl start phantomguard`.
4.  **Monitor:** View alerts and actions on the Streamlit dashboard, typically at `http://localhost:8501`.

## Features

-   **Config-driven Decoys:** Generate realistic fake files, SSH keys, and honeytokens based on a simple JSON configuration.
-   **Real-time Monitoring:** Uses `inotify` to watch for any interaction with decoys.
-   **Rule-Based Scoring:** A flexible scoring engine evaluates the severity of events.
-   **Automated Playbooks:** Triggers actions like alerts and IP blocks based on event scores.
-   **Telegram Alerts:** Receive instant, rate-limited notifications with HMAC-signed payloads.
-   **Autonomous Blocking:** Automatically block suspicious IP addresses using `nftables`.
-   **Web Dashboard:** A simple Streamlit UI for viewing event timelines and system actions.

## Developer Quickstart

For local development and testing:

1. Create a Python venv and activate it.

```powershell
C:/Python313/python.exe -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
C:/Python313/python.exe -m pip install -r requirements.txt
```

3. Run tests:

```powershell
C:/Python313/python.exe -m pytest -q
```

4. Run Streamlit UI (optional):

```powershell
streamlit run ui/dashboard.py
```

Notes:
- Optional dependencies (scikit-learn, torch) are required for ML features.
- Use `processor/train_daily_anomaly.py` to retrain the hybrid anomaly model; it will read `ui/labels.jsonl` for labeled benign events.

For development guidelines, architecture details, and project principles, see `.github/copilot-instructions.md`.
