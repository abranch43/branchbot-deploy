# Revenue Tracking Agent – Notion Page Structure

## Overview

The Revenue Tracking Agent is the money radar for BranchOS. It maintains a unified ledger across Stripe, Gumroad, and offline POs/contracts, and powers the Financial Infrastructure Engine with real-time and historical revenue data. It supports dashboards, scheduled summaries for leadership, and anomaly alerts for unusual patterns.

## Setup Instructions

### Webhook Configuration

#### Stripe Webhook Setup
1. Log in to your Stripe Dashboard
2. Navigate to **Developers → Webhooks**
3. Click **Add endpoint**
4. Enter webhook URL: `https://<YOUR-API-DOMAIN>/webhooks/stripe`
5. Select events to listen for:
   - `charge.succeeded`
   - `payment_intent.succeeded`
   - `checkout.session.completed`
6. Copy the **Signing secret** (starts with `whsec_`)
7. Add to Railway environment as `STRIPE_WEBHOOK_SECRET`

#### Gumroad Webhook Setup
1. Log in to Gumroad
2. Navigate to **Settings → Advanced → Webhooks**
3. Add webhook URL: `https://<YOUR-API-DOMAIN>/webhooks/gumroad`
4. Generate a shared secret (or use a secure random string)
5. Add to Railway environment as `GUMROAD_WEBHOOK_SECRET`

### Deployment via branchbot-deploy on Railway

1. **Fork or Clone Repository**
   ```bash
   git clone https://github.com/abranch43/branchbot-deploy.git
   cd branchbot-deploy
   ```

2. **Deploy to Railway**
   - Click the "Deploy on Railway" button in the README
   - Or manually create a new project on Railway and link the repository

3. **Railway will automatically provision:**
   - `branchberg-api` service (FastAPI backend)
   - `branchberg-dashboard` service (Streamlit dashboard)
   - PostgreSQL database (shared for both services)

### Database Provisioning and Schema

#### Automatic Database Provisioning
Railway automatically provisions a PostgreSQL database when you deploy. The `DATABASE_URL` environment variable is automatically injected into your services.

#### Schema Setup
Run database migrations to create the required tables:

```bash
# From the Railway dashboard, open a terminal for branchberg-api service
python -m alembic upgrade head
```

Or manually create tables using the schema defined in `AGENTS.md`:
- `revenue_events`
- `revenue_summaries`
- `revenue_alerts`

**Schema Links:**
- Full schema specification: See `AGENTS.md` → Revenue Tracking Agent → Database Schema
- Migration scripts: `database/migrations/` (if using Alembic)

### Environment Variables

Set the following environment variables in Railway:

**Required:**
- `STRIPE_WEBHOOK_SECRET` — Stripe webhook signing secret
- `GUMROAD_WEBHOOK_SECRET` — Gumroad webhook signing secret
- `DATABASE_URL` — PostgreSQL connection (auto-set by Railway)
- `SAFE_MODE=true` — Recommended for production

**Optional:**
- `SLACK_WEBHOOK_URL` — For Slack notifications
- `OPENAI_API_KEY` — For AI-powered revenue insights
- `PORT` — API port (defaults to 8000)

### Secret Storage

**Railway Secrets:**
- All secrets are encrypted at rest in Railway
- Never commit secrets to the repository
- Use Railway's environment variable UI to set secrets
- Enable **Variable Masking** for sensitive values

**Best Practices:**
- Rotate webhook secrets quarterly
- Use separate secrets for development/staging/production
- Enable Railway's secret scanning
- Monitor access logs for unauthorized access

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Revenue Data Flow                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────┐         ┌──────────┐         ┌──────────┐
│  Stripe  │         │ Gumroad  │         │ Manual   │
│ Webhooks │         │ Webhooks │         │  Entry   │
└────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                    │
     └──────────┬─────────┴──────────┬─────────┘
                │                    │
                ▼                    ▼
     ┌──────────────────────────────────────┐
     │      FastAPI Backend (API)            │
     │  • Webhook signature verification     │
     │  • Input validation & sanitization    │
     │  • Event deduplication                │
     └──────────────┬───────────────────────┘
                    │
                    ▼
     ┌──────────────────────────────────────┐
     │      PostgreSQL Database              │
     │  • revenue_events                     │
     │  • revenue_summaries                  │
     │  • revenue_alerts                     │
     └──────────────┬───────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│Summarizer│ │Dashboard │ │BranchOS/ │
│  Jobs    │ │ Updates  │ │  Atlas   │
│(Daily/   │ │(Real-time│ │Financial │
│ Weekly)  │ │ Metrics) │ │ Engine   │
└────┬─────┘ └──────────┘ └────┬─────┘
     │                          │
     ▼                          ▼
┌──────────┐            ┌──────────────┐
│  Slack   │            │    Notion    │
│Notifications          │   Database   │
│(Optional)│            │  (Optional)  │
└──────────┘            └──────────────┘
```

**Flow Description:**

1. **Providers → API**: Revenue events arrive via webhooks or manual entry
2. **API → Postgres**: Events are validated, deduplicated, and stored
3. **Summarizer**: Scheduled jobs compute daily/weekly totals
4. **Dashboard**: Streamlit UI pulls real-time metrics from Postgres
5. **BranchOS/Atlas**: Financial engine consumes revenue data for insights
6. **Slack/Notion**: Summaries and alerts pushed to collaboration tools

## Integration Points

### BranchOS/Atlas Integration

The Revenue Tracking Agent integrates with the BranchOS Financial Infrastructure Engine to provide:

- **Real-time Revenue API**: RESTful endpoints for current totals and trends
  - `GET /api/v1/revenue/totals` — Current day/week/month totals
  - `GET /api/v1/revenue/trends` — Historical trends and growth rates
  - `GET /api/v1/revenue/events` — Recent revenue events with pagination

- **Webhook Subscriptions**: BranchOS can subscribe to revenue events
  - `POST /api/v1/subscriptions` — Register webhook for revenue events
  - Notifications sent on configurable thresholds

- **Data Export**: Bulk export for Atlas analytics
  - `GET /api/v1/revenue/export?format=csv` — CSV export
  - `GET /api/v1/revenue/export?format=json` — JSON export

### Slack Notifications

When `SLACK_WEBHOOK_URL` is configured:

- **Daily Summaries**: Posted at 06:00 Central with yesterday's totals
- **Anomaly Alerts**: Immediate notifications for unusual patterns
- **Threshold Alerts**: Notifications when revenue crosses configured thresholds

**Example Slack Message:**
```
💰 Daily Revenue Summary (2025-12-04)

A+ Enterprise LLC: $12,450.00
Legacy Unchained Inc: $8,320.00
Total: $20,770.00

Events: 47 (Stripe: 32, Gumroad: 12, Manual: 3)
```

### Optional Notion Database Integration

If connecting to Notion:

1. Create a Notion integration and get API key
2. Set `NOTION_API_KEY` and `NOTION_DATABASE_ID` in Railway
3. Revenue summaries will sync to Notion database
4. Allows for custom views, filters, and reporting in Notion

### Admin UI

The admin UI (available at `https://<API-DOMAIN>/admin`) provides:

- **Reconciliation Dashboard**: Compare webhook events to bank deposits
- **Manual Entry Form**: Add offline contracts and POs
- **Alert Management**: View, resolve, or dismiss alerts
- **Backfill Tool**: Upload historical revenue data via CSV

**Access Control:**
- Requires admin authentication (configure `ADMIN_PASSWORD` or OAuth)
- All actions are logged for audit trail

## Operational Runbook

### Common Failures

#### 1. Webhook Signature Verification Failed

**Symptoms:**
- Webhooks return 401 or 403 errors
- No revenue events appearing in dashboard

**Diagnosis:**
```bash
# Check Railway logs for branchberg-api
railway logs --service branchberg-api --tail 100
```

**Resolution:**
1. Verify `STRIPE_WEBHOOK_SECRET` and `GUMROAD_WEBHOOK_SECRET` are correct
2. Check webhook configuration in provider dashboards
3. Ensure secrets don't have leading/trailing whitespace
4. Re-save environment variables in Railway to refresh

#### 2. Database Connection Errors

**Symptoms:**
- API returns 500 errors
- Dashboard shows "Database connection failed"

**Diagnosis:**
```bash
# Check DATABASE_URL is set
railway variables --service branchberg-api | grep DATABASE_URL

# Test database connection
railway run python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"
```

**Resolution:**
1. Verify PostgreSQL service is running in Railway
2. Check database connection limits (Railway free tier has limits)
3. Restart API service to refresh connection pool

#### 3. Missing Daily Summaries

**Symptoms:**
- No Slack notifications at 06:00 Central
- `revenue_summaries` table not updating

**Diagnosis:**
```bash
# Check if scheduled job is running
railway logs --service branchberg-api --filter "daily_summary"

# Check cron configuration
cat Procfile  # Should include: worker: python jobs/daily_summary.py
```

**Resolution:**
1. Verify Railway worker service is enabled
2. Check timezone configuration (should be America/Chicago)
3. Ensure `SLACK_WEBHOOK_URL` is set if expecting Slack notifications
4. Manually trigger job to test: `railway run python jobs/daily_summary.py`

#### 4. Duplicate Events

**Symptoms:**
- Same transaction appears multiple times
- Revenue totals are inflated

**Diagnosis:**
```sql
-- Connect to database and check for duplicates
SELECT event_id, COUNT(*) 
FROM revenue_events 
GROUP BY event_id 
HAVING COUNT(*) > 1;
```

**Resolution:**
1. Check if idempotency logic is working (should use `event_id` as unique key)
2. Add unique constraint on `event_id` if missing:
   ```sql
   ALTER TABLE revenue_events ADD CONSTRAINT unique_event_id UNIQUE (event_id);
   ```
3. Clean up duplicates manually and investigate root cause

### Oncall/Escalation

**L1 Support** (Railway logs, restarts, env var checks):
- Check Railway dashboard for service health
- Review recent logs for errors
- Restart services if needed
- Verify environment variables

**L2 Support** (Database, webhook debugging):
- Access database for manual queries
- Test webhook endpoints with curl
- Review provider webhook logs (Stripe/Gumroad dashboards)
- Check for network/firewall issues

**L3 Support** (Code changes, escalation):
- Contact: **Antonio Branch** — antonio.branch31@gmail.com
- Slack: #revenue-ops or DM @antonio
- GitHub: Create issue at https://github.com/abranch43/branchbot-deploy/issues
- For critical production issues: Call/text provided in oncall rotation

**Escalation Criteria:**
- Revenue data loss or corruption
- Security incident (unauthorized access, leaked secrets)
- Extended outage (>1 hour)
- Regulatory compliance issue

## Resources

### Repository
- **GitHub**: https://github.com/abranch43/branchbot-deploy
- **Issues**: https://github.com/abranch43/branchbot-deploy/issues
- **Wiki**: https://github.com/abranch43/branchbot-deploy/wiki

### Dashboard
- **Production**: `https://<your-dashboard-domain>.railway.app`
- **API**: `https://<your-api-domain>.railway.app`
- **Health Check**: `https://<your-api-domain>.railway.app/health`

### API Documentation
- **OpenAPI/Swagger**: `https://<your-api-domain>.railway.app/docs`
- **ReDoc**: `https://<your-api-domain>.railway.app/redoc`
- **Schema**: See `AGENTS.md` for database schema

### Contacts

**Primary Maintainer:**
- **Name**: Antonio Branch
- **Email**: antonio.branch31@gmail.com
- **Slack**: #revenue-ops or #finance-ops

**Additional Support:**
- **Slack Channel**: #revenue-ops
- **Email**: support@branchbot.example.com (update with actual support email)

### External Resources
- **Railway Documentation**: https://docs.railway.app
- **Stripe Webhooks**: https://stripe.com/docs/webhooks
- **Gumroad API**: https://help.gumroad.com/article/280-webhooks
- **FastAPI**: https://fastapi.tiangolo.com
- **Streamlit**: https://docs.streamlit.io

## Change Log

### 2025-12-05 — Initial Release
- Revenue Tracking Agent specification created
- Database schema defined (revenue_events, revenue_summaries, revenue_alerts)
- Webhook endpoints implemented (/webhooks/stripe, /webhooks/gumroad)
- Daily summary job at 06:00 Central
- Integration with BranchOS Financial Infrastructure Engine
- Slack notifications for daily summaries and alerts
- Admin UI for reconciliation and manual entry

### Future Enhancements
- [ ] Notion database integration
- [ ] Advanced anomaly detection with ML
- [ ] Multi-currency support with real-time exchange rates
- [ ] Automated reconciliation with bank statements
- [ ] Custom alert rules configuration UI
- [ ] Export to QuickBooks/Xero accounting software
- [ ] Revenue forecasting and predictions
