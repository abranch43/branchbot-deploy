"""Notification interface.

Keep this small so webhook handlers/jobs can emit notifications without
knowing about transport details (Slack/email).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Any, Optional


@dataclass(frozen=True)
class AlertMessage:
    alert_type: str  # threshold|anomaly|duplicate
    severity: str  # info|warning|critical
    message: str
    metadata: dict[str, Any] | None = None


class Notifier(Protocol):
    def notify_alert(self, alert: AlertMessage) -> None: ...

    def notify_summary(self, *, text: str, metadata: Optional[dict[str, Any]] = None) -> None: ...
