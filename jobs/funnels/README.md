# Funnels – Pulse Job

Purpose: Aggregate Gumroad, Fiverr, and Upwork signals into a single markdown snapshot.

Run locally:
- `python jobs/funnels/run.py --out out/funnels/funnels_snapshot.md`

Output:
- `out/funnels/funnels_snapshot.md` (sample snapshot; extend with real adapters later)

Notes:
- No network calls by default; plug in adapters once approvals are granted.
- Keep transformations pure and deterministic for easy testing.

