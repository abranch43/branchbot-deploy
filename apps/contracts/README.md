# Contracts – Compliance Pack

Purpose: Convert MO BUYS forms into PDFs and JSON receipts.

Run locally:
- Create venv and install deps (minimal): `python -m venv .venv && .venv\\Scripts\\activate && pip install -r requirements.txt`
- Generate sample artifacts: `python apps/contracts/main.py --out out/contracts`

Outputs:
- `out/contracts/receipts/receipt.sample.json`
- `out/contracts/pdfs/form.sample.pdf` (placeholder PDF)

Notes:
- Keep secrets in `.env.local` (never commit). No network calls in this module by default.
- Add parsers as `*_parser.py` and generators as `*_generator.py` in this folder.

