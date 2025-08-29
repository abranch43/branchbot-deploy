# Family – Tech Microservice

Purpose: Produce Jennise iPhone upgrade checklist (CSV/PDF) and Justice screen repair intake (PDF).

Run locally:
- Env: `python -m venv .venv && .venv\\Scripts\\activate && pip install -r requirements.txt`
- Generate samples: `python apps/family/main.py --out out/family`

Outputs:
- `out/family/iphone_upgrade_checklist.csv`
- `out/family/screen_repair_intake.pdf` (placeholder PDF)

Notes:
- Store secrets in `.env.local` only; avoid logging sensitive data.
- Extend with `checklist_generator.py` and `intake_generator.py` as needed.

