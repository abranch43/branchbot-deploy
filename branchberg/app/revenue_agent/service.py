"""Revenue Tracking Agent service layer.

This is the orchestration point for:
- webhook handlers (real-time ingest)
- scheduled jobs (summaries/alerts)
- notifications

Right now, jobs are TODO (the repo has no scheduler wired in yet).
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from branchberg.app.revenue_agent.config import AgentSettings
from branchberg.app.revenue_agent.notifications.slack import SlackWebhookNotifier


class RevenueTrackingAgent:
    def __init__(self, settings: AgentSettings):
        self.settings = settings
        self.notifier = SlackWebhookNotifier(settings.slack_webhook_url)

    def run_daily_summary_job(self, db: Session) -> None:
        """Compute daily summary totals and send notifications.

        TODO:
        - compute yesterday's totals (Central time) per AGENTS.md
        - write to `revenue_summaries` table (model not yet implemented)
        - send Slack/email if configured and SAFE_MODE is false
        """
        if self.settings.safe_mode:
            return

        # TODO: implement.
        return

    def run_alerts_job(self, db: Session) -> None:
        """Detect anomalies/thresholds/duplicates and notify.

        TODO:
        - implement threshold alerts
        - implement anomaly detection (rolling baseline)
        - write to `revenue_alerts` table (model not yet implemented)
        """
        if self.settings.safe_mode:
            return

        # TODO: implement.
        return
