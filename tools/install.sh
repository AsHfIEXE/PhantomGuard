#!/usr/bin/env bash
set -euo pipefail

# PhantomGuard install script (production-ready)
PYENV_DIR="/opt/phantomguard/venv"
SERVICE_USER="phantom"
INSTALL_DIR="/opt/phantomguard"

mkdir -p ${INSTALL_DIR}
# Copy application files
cp -r phantomguard.py phantomgen sensors processor alerting ui ${INSTALL_DIR}/

python3 -m venv ${PYENV_DIR}
source ${PYENV_DIR}/bin/activate
pip install --upgrade pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi

# Copy config file if it exists
if [ -f config.json ]; then
  sudo cp config.json ${INSTALL_DIR}/config.json
else
  sudo cp config.json.example ${INSTALL_DIR}/config.json
fi

# Create service user
if ! id -u ${SERVICE_USER} >/dev/null 2>&1; then
  sudo useradd --system --no-create-home --shell /usr/sbin/nologin ${SERVICE_USER} || true
fi

# Copy systemd unit (requires sudo)
sudo mkdir -p /var/log/phantomguard
sudo chown ${SERVICE_USER}:${SERVICE_USER} /var/log/phantomguard || true
sudo cp tools/phantomguard.service /etc/systemd/system/phantomguard.service
sudo systemctl daemon-reload

echo "Install complete. Edit /opt/phantomguard/config.json and then:"
echo "  sudo systemctl enable --now phantomguard"
