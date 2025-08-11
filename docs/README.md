# BranchBot Deploy

[![Build Status](https://github.com/${GITHUB_OWNER:-your-org}/${GITHUB_REPO:-your-repo}/actions/workflows/daily-scan.yml/badge.svg)](https://github.com/${GITHUB_OWNER:-your-org}/${GITHUB_REPO:-your-repo}/actions/workflows/daily-scan.yml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](../LICENSE)

Production-ready, money-first system for A+ Enterprise LLC (SDVOSB/MBE/SDVE):
- Leads + Payments (Next.js + Stripe Payment Link)
- Contract hunting (SAM.gov + MissouriBUYS manual CSV)
- Alerts via email + GitHub Issues

## One-command local runs
- Python bot (from repo root):
```bash
python -m venv .venv && . .venv/bin/activate && pip install -r requirements_branchbot.txt && PYTHONPATH=bots/contracts-bot python -m contracts_bot run --since 7 && python ops/notify.py
```
- Leadgen site:
```bash
cd apps/leadgen-site && npm i && npm run dev
```

## Environment variables (.env)
- STRIPE_PAYMENT_URL: Stripe Payment Link URL
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, FROM_EMAIL, TO_EMAIL
- SAM_API_KEY (optional)
- GH_TOKEN (optional for Issue creation)

## Import MissouriBUYS CSV
- Drop CSV at `data/import/mobuys.csv`
- Headers: `id,title,agency,location,category,url,due_date,created_at`
- Run: `PYTHONPATH=bots/contracts-bot python -m contracts_bot run --since 7`

## Outputs
- `data/opportunities.json` — normalized opportunities
- `reports/opportunities.md` — digest grouped by source
