## Summary
- What does this change and why?

## Scope
- Lane: Contracts Ops / Family Tech / Visibility (Funnels)
- Modules touched: apps/*, jobs/*, tests/*, out/*

## Changes
- Key changes (bullets):

## Test Plan
- Commands run:
```
python -m venv .venv && .venv/Scripts/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
```
- Outputs verified in `out/` (list samples):

## Checklist
- [ ] Human-readable commits (imperative)
- [ ] Tests added/updated and passing
- [ ] Sample artifacts added/updated in `out/` (if applicable)
- [ ] No secrets committed; `.env.local` only
- [ ] CI green (lint + tests)

## Linked Issues
- Closes #

