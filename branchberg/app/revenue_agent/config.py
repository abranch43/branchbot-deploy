"""Agent configuration.

Source of truth: AGENTS.md env var list.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class AgentSettings:
    """Runtime settings for the Revenue Tracking Agent."""

    safe_mode: bool
    stripe_webhook_secret: str | None
    gumroad_webhook_secret: str | None
    slack_webhook_url: str | None

    @staticmethod
    def from_env() -> "AgentSettings":
        return AgentSettings(
            safe_mode=_env_bool("SAFE_MODE", True),
            stripe_webhook_secret=(os.getenv("STRIPE_WEBHOOK_SECRET") or "").strip() or None,
            gumroad_webhook_secret=(os.getenv("GUMROAD_WEBHOOK_SECRET") or "").strip() or None,
            slack_webhook_url=(os.getenv("SLACK_WEBHOOK_URL") or "").strip() or None,
        )
