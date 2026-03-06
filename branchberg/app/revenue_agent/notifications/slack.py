"""Slack notifier.

Uses `SLACK_WEBHOOK_URL` if configured; otherwise behaves as a no-op.
"""

from __future__ import annotations

from typing import Any, Optional

import requests

from .base import AlertMessage


class SlackWebhookNotifier:
    def __init__(self, webhook_url: str | None):
        self._webhook_url = (webhook_url or "").strip() or None

    def notify_alert(self, alert: AlertMessage) -> None:
        if not self._webhook_url:
            return

        # TODO: format blocks/attachments consistently across alert types.
        payload = {
            "text": f"[{alert.severity.upper()}] {alert.alert_type}: {alert.message}",
        }
        try:
            requests.post(self._webhook_url, json=payload, timeout=10)
        except Exception:
            # TODO: add structured logging; do not raise to avoid breaking ingest.
            return

    def notify_summary(self, *, text: str, metadata: Optional[dict[str, Any]] = None) -> None:
        if not self._webhook_url:
            return

        payload = {"text": text}
        try:
            requests.post(self._webhook_url, json=payload, timeout=10)
        except Exception:
            return
