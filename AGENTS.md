# AGENTS.md — BranchOS Agent Specifications

## Codex Guide
### Purpose
# AGENTS.md — Codex Guide
## Purpose
- Code review focus: security, error handling, env/secret hygiene, performance.
- Project areas: /branchbot, /api, deployment (Railway), tests in /branchbot/tests.

### Commands Codex may run
- python -m unittest
- uv run pytest || pytest
- ruff, mypy (if present)
- railway logs (read-only)



## Revenue Tracking Agent

### Purpose
Listens to financial events (Stripe, Gumroad, manual contract entries), stores unified revenue events, and powers real-time cashflow insights and alerts.

### Description
The Revenue Tracking Agent monitors provider webhooks and offline purchase orders for **A+ Enterprise LLC** and **Legacy Unchained Inc**. It maintains an up-to-date ledger, powers dashboards, reports, and anomaly alerts, and can send summaries via Slack/email.

### Permissions Required
- **Read** Stripe/Gumroad webhooks
- **Write** to Postgres revenue database
- **Access** BranchOS API for totals/trends
- **Send** notifications (Slack/email)

### Inputs/Outputs

#### Inputs
- Webhook events from Stripe and Gumroad
- Manual revenue entries (contracts, offline POs)

#### Outputs
- Unified revenue records in database
- Dashboard updates (real-time metrics)
- Alerts for anomalies or thresholds
- Daily/weekly revenue summaries

### Integration Notes

#### Webhook Endpoints
- **Stripe**: `/webhooks/stripe`
- **Gumroad**: `/webhooks/gumroad`
- **Manual Entry**: Secure manual-entry endpoint (admin-authenticated)

#### Environment Variables
- `STRIPE_WEBHOOK_SECRET` — Stripe webhook signing secret (required)
- `GUMROAD_WEBHOOK_SECRET` — Gumroad webhook signing secret (required)
- `SAFE_MODE` — When `true`, disables risky external integrations (recommended for production)
- `DATABASE_URL` — PostgreSQL connection string (required)
- `SLACK_WEBHOOK_URL` — Slack incoming webhook URL (optional)
- `OPENAI_API_KEY` — OpenAI API key for AI-powered insights (optional)

#### Integration with Atlas/BranchOS Financial Infrastructure Engine
The Revenue Tracking Agent feeds real-time and historical revenue data to the BranchOS Financial Infrastructure Engine, enabling:
- Real-time cashflow dashboards
- Trend analysis and forecasting
- Anomaly detection for unusual revenue patterns

#### Security
- **Webhook signature verification**: All incoming webhooks are cryptographically verified
- **Input validation**: All revenue data is validated and sanitized before storage
- **Environment encryption**: Secrets stored in encrypted environment variables
- **HTTPS/SSL**: All endpoints require secure connections

### Database Schema

#### Suggested Tables

**`revenue_events`**
- `id` — UUID primary key
- `event_id` — Unique event identifier from provider
- `provider` — Enum: `stripe`, `gumroad`, `manual`
- `event_type` — String (e.g., `charge.succeeded`, `sale`)
- `amount_cents` — Integer (amount in cents)
- `currency` — String (ISO 4217, e.g., `USD`)
- `customer_email` — String (nullable)
- `customer_id` — String (nullable)
- `metadata` — JSONB (additional provider-specific data)
- `created_at` — Timestamp
- `processed_at` — Timestamp
- `entity` — String: `A+ Enterprise LLC` or `Legacy Unchained Inc`

**`revenue_summaries`**
- `id` — UUID primary key
- `period` — String: `daily`, `weekly`, `monthly`
- `start_date` — Date
- `end_date` — Date
- `total_amount_cents` — Integer
- `event_count` — Integer
- `entity` — String: `A+ Enterprise LLC` or `Legacy Unchained Inc`
- `created_at` — Timestamp

**`revenue_alerts`**
- `id` — UUID primary key
- `alert_type` — Enum: `threshold`, `anomaly`, `duplicate`
- `severity` — Enum: `info`, `warning`, `critical`
- `message` — Text
- `metadata` — JSONB
- `resolved` — Boolean
- `created_at` — Timestamp
- `resolved_at` — Timestamp (nullable)

### Operational Notes

#### Idempotent Webhook Handling
- All webhook events are deduplicated using `event_id`
- Prevents duplicate revenue recording from webhook retries

#### Backfill Endpoint
- Admin-only endpoint to backfill historical revenue data
- Supports CSV/JSON upload for bulk import

#### Admin UI
- Reconciliation dashboard for manual review
- Allows flagging and resolving discrepancies

#### Scheduled Summary Jobs
- **Daily at 06:00 Central**: Compute yesterday's totals and push summary to BranchOS/Slack
- **Weekly on Monday at 06:00 Central**: Weekly rollup and trends
- **Monthly on 1st at 06:00 Central**: Monthly financial summary

#### Daily Job Details
The daily job at 06:00 Central computes:
- Total revenue for the previous day (midnight to midnight Central)
- Breakdown by provider (Stripe, Gumroad, manual)
- Breakdown by entity (A+ Enterprise LLC, Legacy Unchained Inc)
- Event count and average transaction value
- Pushes summary to BranchOS Financial Infrastructure Engine
- Optionally posts to Slack channel for leadership visibility

### Contact

**Maintainer**: Antonio Branch — antonio.branch31@gmail.com

**Slack Channel**: #revenue-ops (or #finance-ops in your workspace)
