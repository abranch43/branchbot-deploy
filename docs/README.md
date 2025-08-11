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

## How to get live data
1. Set `SAM_API_KEY` in `.env` (local) or repo Secrets (CI).
2. Download MissouriBUYS CSV to `data/import/mobuys.csv` (headers: `id,title,agency,location,category,url,due_date,created_at`).
3. Run:
```bash
PYTHONPATH=bots/contracts-bot python -m contracts_bot run --since 7
```
Outputs:
- `data/opportunities.json` (normalized)
- `data/contracts/YYYY-MM-DD.json` and `.csv` plus `latest.*`
- `reports/opportunities.md`

Note: SAM.gov API requires an account and API key. Sign up at `https://api.sam.gov/`.
