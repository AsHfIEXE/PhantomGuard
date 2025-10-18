#!/usr/bin/env bash
# PhantomGuard demo: simulate attacks on decoys
set -euo pipefail

echo "[Demo] Setting up decoys from config.json.example..."
python3 phantomgen/decoy_engine.py --config config.json.example

echo "[Demo] Triggering a high-severity event by touching a fake SSH key..."
touch /tmp/.ssh/id_rsa
sleep 2 # Give the watcher time to pick it up

echo "[Demo] Triggering a medium-severity event..."
touch /opt/backups/db.sql.gz
sleep 2

echo "[Demo] Running a simulated port scan..."
if command -v nmap >/dev/null 2>&1; then
  nmap -p 22,80,443 localhost
fi

echo "[Demo] Demo actions completed. Check logs and dashboard."
