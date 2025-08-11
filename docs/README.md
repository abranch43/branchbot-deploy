# BranchBot Deploy

[![Build Status](https://github.com/${GITHUB_OWNER:-your-org}/${GITHUB_REPO:-your-repo}/actions/workflows/daily-scan.yml/badge.svg)](https://github.com/${GITHUB_OWNER:-your-org}/${GITHUB_REPO:-your-repo}/actions/workflows/daily-scan.yml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](../LICENSE)

A production-ready, money-first system for A+ Enterprise LLC (SDVOSB/MBE/SDVE):
- Capture leads and take payments
- Auto-hunt contract opportunities
- Notify and log everything

## Features
- Leadgen site (Next.js, Vercel-ready): hero offer, services, certifications, case bullets, CTA
- Book a Call form: appends to `data/leads.json` and emails you
- Buy Now button via Stripe Payment Link (`STRIPE_CHECKOUT_URL`)
- Contracts bot: SAM.gov and MissouriBUYS with keyword filters, retry/backoff, dedupe by solicitation ID
- Outputs `data/contracts/YYYY-MM-DD.json`, rolling `latest.json` and CSV, and `latest.meta.json`
- Logging with rotating files in `logs/`
- Optional sinks: Notion, Google Sheets (CSV is default)
- CI: daily scan, auto-commit new data, open issue summary, email notification
- Windows-friendly: `.env.template`, PowerShell scheduler scripts, `ops.bat`

## Quick Start
1. Clone repo and create virtualenv
2. Copy `.env.template` to `.env` and fill required keys
3. Run bot once and send notification

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements_branchbot.txt
PYTHONPATH=bots/contracts-bot python -m contracts_bot run --since 7
python ops/notify.py
```

## Environment Setup (.env)
See `ops/.env.template` for all keys:
- EMAIL_FROM, EMAIL_TO, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
- STRIPE_CHECKOUT_URL
- Optional: NOTION_TOKEN, NOTION_DB_ID, GOOGLE_SHEETS_JSON, SAM_API_KEY, SAM_KEYWORDS

## How to make money today
- Ensure `STRIPE_CHECKOUT_URL` is set to a live payment link
- Deploy leadgen site to Vercel, add your domain
- Add SMTP creds to send lead notifications
- Enable GitHub Actions with secrets configured
- Set Windows Task Scheduler as backup to run daily

## Deploy Leadgen Site to Vercel
- In `apps/leadgen-site`, run `npm i && npm run build`
- Connect repo to Vercel and set environment variables from `.env`
- Note: Writing to `data/leads.json` is best-effort locally. On Vercel, filesystem is ephemeral; email is the source of truth. Consider adding a GitHub token write-back if persistence is required.

## GitHub Actions Secrets
Set in repo Settings → Secrets and variables → Actions:
- EMAIL_FROM, EMAIL_TO, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
- Optional: NOTION_TOKEN, NOTION_DB_ID, GOOGLE_SHEETS_JSON, SAM_API_KEY, SAM_KEYWORDS

## Windows Scheduler
- `ops/win/register_task.ps1` schedules daily run at 07:00 local
- `ops/win/run_once.ps1` runs end-to-end once for verification

## Security & Ethics
- Keys stored via environment variables; see SECURITY.md
- Scrapers use request timeouts and respect site stability
- Only collect necessary lead data; avoid PII beyond contact info
- Respect robots.txt and terms when scraping

## Go Live in 10 Minutes
1) Create `.env` from `ops/.env.template`
2) Set GitHub repo secrets (SMTP_*, STRIPE_CHECKOUT_URL, optional NOTION/GOOGLE/SAM)
3) Enable Actions → `daily-scan.yml`
4) Deploy `apps/leadgen-site` to Vercel and paste URL below
5) Run `ops/win/run_once.ps1` to verify end-to-end

Production URL: <PASTE VERCEL URL HERE>