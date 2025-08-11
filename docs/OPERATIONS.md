# Operations Runbook

## Daily Job
- Trigger: GitHub Actions at 12:00 UTC
- Steps: checkout → setup Python → run bot → commit changes → create issue → notify
- Success Criteria: workflow green. If `new_count > 0`, data committed and issue created.

## On Failure
- Workflow sends email with subject `[BranchBot] Failure detected (DATE)`
- Check logs locally at `logs/contracts_bot.log`, or workflow logs in GitHub.
- Re-run job via `workflow_dispatch` from Actions tab.

## Manual Run
```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements_branchbot.txt
PYTHONPATH=bots/contracts-bot python -m contracts_bot run --since 7
python ops/notify.py
```

## Configuration
- Edit `config/settings.json` for keywords and sinks.
- Env vars provide sensitive integrations: see `ops/.env.template`.

## Data
- Outputs in `data/contracts/` with `latest.*` rolling files and dated snapshots.
- Dedupe is by `solicitation_id` persisted in `seen_ids.json`.

## Leadgen Site
- Development: `cd apps/leadgen-site && npm i && npm run dev`
- Environment: set `EMAIL_*`, `STRIPE_CHECKOUT_URL` in Vercel.

## Backups
- Data changes are committed daily to the repo.