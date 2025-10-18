# 👻 PhantomGuard

**Lightweight, deception-based threat detection for solo developers**

PhantomGuard is a stealthy, autonomous system that detects and responds to threats on personal machines using realistic decoys (fake credentials, SSH keys, config files) and intelligent monitoring.

---

## 🚀 Quick Start

### 1. **Setup**

```bash
# Clone or download the repository
cd phantomguard

# Run the automated setup script
chmod +x setup_and_test.sh
./setup_and_test.sh

# Or manual setup:
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. **Configure**

```bash
# Copy the example config
cp config.json.example config.json

# Edit config.json and add your Telegram credentials:
# - Get a bot token from @BotFather on Telegram
# - Get your chat ID from @userinfobot
nano config.json  # or use your favorite editor
```

### 3. **Generate Decoys**

```bash
# Create realistic decoy files
python3 phantomgen/decoy_engine.py --config config.json
```

### 4. **Run the System**

```bash
# Start PhantomGuard (main detection system)
python3 phantomguard.py

# In another terminal, start the dashboard
streamlit run ui/dashboard.py
```

### 5. **Test It**

```bash
# In another terminal, simulate attacks
python3 demo/attack_simulator.py

# Or manually trigger alerts
cat /tmp/.ssh/id_rsa
cat /tmp/.env
```

---

## 📋 Features

### ✅ Core Features
- **Config-driven Decoys**: Realistic fake files, SSH keys, and honeytokens
- **Real-time Monitoring**: Uses `inotify`/`watchdog` for instant detection
- **Rule-Based Scoring**: Flexible scoring engine with configurable thresholds
- **Automated Playbooks**: Alert → Block → Quarantine based on threat level
- **Telegram Alerts**: Instant notifications with HMAC-signed payloads
- **IP Blocking**: Autonomous blocking via `nftables` (with dry-run mode)
- **Web Dashboard**: Streamlit UI for viewing events and marking false positives

### 🔬 Advanced Features
- **Hybrid Anomaly Detection**: Combines Isolation Forest, One-Class SVM, and autoencoder
- **Network Honeypots**: Fake SSH banner and HTTP honeypot
- **Forensic Logging**: Structured JSON logs for analysis
- **False Positive Management**: Mark and suppress benign events
- **Persistent Event Queue**: Crash-resistant event storage

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PhantomGuard                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Decoys     │  │   Sensors    │  │  Processor   │ │
│  │              │  │              │  │              │ │
│  │ • Fake SSH   │  │ • FS Watcher │  │ • Scorer     │ │
│  │ • Fake .env  │  │ • HTTP       │  │ • Anomaly ML │ │
│  │ • Fake DBs   │  │ • SSH Banner │  │ • Playbook   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Alerting    │  │   Blocker    │  │      UI      │ │
│  │              │  │              │  │              │ │
│  │ • Telegram   │  │ • nftables   │  │ • Streamlit  │ │
│  │ • HMAC       │  │ • Dry-run    │  │ • FP Mgmt    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
phantomguard/
├── phantomguard.py          # Main application runner
├── config.json              # Configuration (YOU MUST EDIT THIS)
├── config.json.example      # Template configuration
├── requirements.txt         # Python dependencies
│
├── phantomgen/              # Decoy generation
│   ├── decoy_engine.py      # Main decoy generator
│   └── simple_decoy.py      # Simple file decoys
│
├── sensors/                 # Detection sensors
│   ├── fs_watcher.py        # Filesystem monitoring (inotify)
│   ├── http_honeypot.py     # Fake HTTP server
│   └── ssh_banner.py        # Fake SSH banner
│
├── processor/               # Event processing
│   ├── event_scorer.py      # Rule-based scoring
│   ├── event_enrich.py      # Add context to events
│   ├── event_queue.py       # Persistent event storage
│   ├── hybrid_anomaly.py    # ML anomaly detection
│   ├── playbook.py          # Response orchestration
│   └── ip_blocker.py        # nftables integration
│
├── alerting/                # Alert delivery
│   └── telegram_alert.py    # Telegram bot integration
│
├── ui/                      # Web dashboard
│   ├── dashboard.py         # Streamlit UI
│   ├── fp_state.json        # False positive tracking
│   └── labels.jsonl         # User-labeled events
│
├── demo/                    # Testing and demos
│   ├── attack_simulator.py  # Comprehensive attack simulator
│   └── attack_simulator.sh  # Legacy bash version
│
├── tools/                   # Installation and deployment
│   ├── install.sh           # System installation script
│   └── phantomguard.service # Systemd service file
│
└── tests/                   # Unit tests
    ├── test_event_scorer.py
    └── test_labels.py
```

---

## ⚙️ Configuration Guide

### Minimal config.json

```json
{
  "watcher": {
    "paths": ["/tmp/.ssh", "/tmp/.env"]
  },
  "scorer": {
    "threshold": 50,
    "rules": [
      {"name": "ssh_key", "weight": 80, "pattern": "id_rsa"},
      {"name": "env_file", "weight": 70, "pattern": "\\.env"}
    ]
  },
  "telegram": {
    "bot_token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID",
    "hmac_key": "your-secret-key-min-32-chars"
  },
  "blocker": {
    "dry_run": true
  }
}
```

### Key Settings

- **`watcher.paths`**: Directories to monitor (decoy locations)
- **`scorer.threshold`**: Minimum score to trigger alerts (default: 50)
- **`scorer.rules`**: Pattern-matching rules with weights
- **`telegram.*`**: Telegram bot credentials for alerts
- **`blocker.dry_run`**: Set to `false` to enable actual IP blocking (⚠️ USE WITH CAUTION)

---

## 🧪 Testing

### Run System Tests

```bash
# Comprehensive system test
python3 test_system.py

# Run unit tests
pytest tests/ -v
```

### Simulate Attacks

```bash
# Run all attack simulations
python3 demo/attack_simulator.py

# Run specific attack
python3 demo/attack_simulator.py --attack credential
python3 demo/attack_simulator.py --attack ssh
```

### Manual Testing

```bash
# Trigger high-severity alert
cat /tmp/.ssh/id_rsa

# Trigger medium-severity alert
cat /tmp/.env

# Trigger network detection
curl http://localhost:8080/admin
nc localhost 2222
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. **Permission Denied on /var/log/phantomguard**

```bash
# Solution 1: Use local logs directory
mkdir -p logs/phantomguard

# Solution 2: Grant permissions (requires sudo)
sudo mkdir -p /var/log/phantomguard
sudo chown $USER:$USER /var/log/phantomguard
```

#### 2. **Telegram Alerts Not Working**

- Check your bot token and chat ID in `config.json`
- Test with: `curl https://api.telegram.org/bot<TOKEN>/getMe`
- Ensure bot is started (send `/start` to your bot)
- Check logs: `grep telegram /var/log/phantomguard/alerts.log`

#### 3. **Watchdog Not Detecting Events**

```bash
# Check if paths exist
ls -la /tmp/.ssh/id_rsa

# Regenerate decoys
python3 phantomgen/decoy_engine.py --config config.json

# Test watcher directly
python3 sensors/fs_watcher.py /tmp/.ssh
```

#### 4. **Module Import Errors**

```bash
# Install missing dependencies
pip install -r requirements.txt

# For optional ML features
pip install scikit-learn torch
```

#### 5. **Dashboard Won't Start**

```bash
# Check if streamlit is installed
pip install streamlit

# Try alternate port
streamlit run ui/dashboard.py --server.port 8502
```

---

## 🚀 Advanced Usage

### Production Deployment

```bash
# Install as systemd service (Linux)
sudo ./tools/install.sh

# Enable and start
sudo systemctl enable phantomguard
sudo systemctl start phantomguard

# Check status
sudo systemctl status phantomguard

# View logs
sudo journalctl -u phantomguard -f
```

### Enable Real IP Blocking

⚠️ **WARNING**: Only enable on isolated test systems!

```bash
# 1. Setup nftables
sudo nft add table inet filter
sudo nft add chain inet filter phantom_block { type filter hook input priority 0\; }
sudo nft add set inet filter phantom_block { type ipv4_addr\; }
sudo nft add rule inet filter phantom_block ip saddr @phantom_block drop

# 2. Edit config.json
"blocker": {
  "dry_run": false
}
```

### Train Anomaly Model

```bash
# Label events in dashboard first, then:
python3 processor/train_daily_anomaly.py

# Model will be saved to processor/hybrid_anomaly_weights.pt
```

---

## 📊 Metrics & Monitoring

### View Real-time Alerts

```bash
# Tail alert log
tail -f /var/log/phantomguard/alerts.log | jq .

# Count alerts by type
cat /var/log/phantomguard/alerts.log | jq -r '.event_type' | sort | uniq -c
```

### Dashboard Features

- **Alert Timeline**: See all triggered events with severity colors
- **Event Details**: Full JSON payloads for forensic analysis
- **Label Management**: Mark events as benign/attack/false positive
- **Block Log**: View all IP blocking actions

---

## 🛡️ Security Best Practices

1. **Keep dry_run enabled** until thoroughly tested
2. **Isolate from production** networks
3. **Use strong HMAC keys** (32+ characters)
4. **Rotate Telegram tokens** periodically
5. **Review false positives** regularly in dashboard
6. **Monitor system resources** (CPU, disk, memory)

---

## 🔮 Roadmap

- [ ] Windows full support with registry decoys
- [ ] Email alerting in addition to Telegram
- [ ] MITRE ATT&CK mapping for detections
- [ ] Containerized deployment (Docker)
- [ ] Multi-host deployment support
- [ ] Custom webhook integrations
- [ ] Threat intelligence feed integration
- [ ] Memory forensics capture
- [ ] Advanced ML models (transformers)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Test your changes thoroughly
2. Follow the coding style in `.github/copilot-instructions.md`
3. Add tests for new features
4. Update documentation

---

## 📜 License

This project is for educational and research purposes. Use responsibly and only on systems you own or have permission to test.

---

## 🆘 Support

- **Issues**: Check existing issues or create new ones
- **Documentation**: See `.github/prompts/project-1.prompt.md`
- **Testing**: Run `python3 test_system.py` for diagnostics

**Built with ❤️ for defenders, by defenders.**