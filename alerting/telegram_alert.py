"""
PhantomGuard Telegram Alerting (production-ready)
Sends alerts via Telegram with HMAC signing, rate-limiting, config, and robust error handling.
"""
import os
import time
import json
import hmac
import hashlib
import threading
from collections import deque
from typing import Dict, Any
import requests  


class TelegramAlerter:
    """
    Handles sending alerts to Telegram, with rate limiting and HMAC signing.
    """

    def __init__(
            self,
            token: str,
            chat_id: str,
            hmac_key: str,
            alert_limit: int = 5,
            alert_window: int = 60):
        self.token = token
        self.chat_id = chat_id
        self.hmac_key = hmac_key.encode()
        self.alert_limit = alert_limit
        self.alert_window = alert_window
        self._alert_times = deque()
        self._lock = threading.Lock()
        from collections import deque as _DequeType
        self._alert_times: '_DequeType[float]' = self._alert_times

    def _rate_allow(self) -> bool:
        """Checks if an alert can be sent based on the rate limit."""
        with self._lock:
            now = time.time()
            while self._alert_times and self._alert_times[0] < now - \
                    self.alert_window:
                self._alert_times.popleft()
            if len(self._alert_times) >= self.alert_limit:
                return False
            self._alert_times.append(now)
            return True

    def send_alert(self,
                   event: Dict[str,
                               Any],
                   urgent: bool = False,
                   dry_run: bool = False) -> bool:
        """
        Sends a formatted alert to the configured Telegram chat.

        Args:
            event: The event dictionary to be sent.
            urgent: If True, prepends an urgent marker to the message.
            dry_run: If True, prints the message instead of sending it.

        Returns:
            True if the alert was sent successfully, False otherwise.
        """
        if not self._rate_allow():
            print("[alerting] Rate limit exceeded, dropping alert")
            return False

        payload = json.dumps(event, sort_keys=True).encode()
        sig = hmac.new(self.hmac_key, payload, hashlib.sha256).hexdigest()
        text = (
            f"PhantomGuard ALERT: {
                event.get('event_type')} {
                event.get('path')}\n" f"score={
                event.get(
                    'score',
                    0)}")
        if urgent:
            text = "🚨 " + text
        if dry_run:
            print("[alerting] DRY-RUN send message:", text)
        else:
            try:
                resp = requests.post(
                    f'https://api.telegram.org/bot{self.token}/sendMessage',
                    json={'chat_id': self.chat_id, 'text': text},
                )
                resp.raise_for_status()
            except Exception as e:
                print(f"[alerting] Telegram send failed: {e}")
                return False

        # Log signature
        try:
            os.makedirs('/var/log/phantomguard', exist_ok=True)
            with open('/var/log/phantomguard/alerts.log', 'a') as f:
                f.write(f"{time.time()} {sig} {payload.decode()}\n")
        except Exception as e:
            print(f"[alerting] Log write failed: {e}")

        return True
