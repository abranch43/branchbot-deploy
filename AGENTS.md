# Repository Guidelines

## Project Structure & Module Organization
- `apps/contracts/`: Compliance Pack (MO BUYS forms → PDFs/JSON).
- `apps/family/`: Family Tech microservice (Jennise iPhone checklist, Justice intake).
- `jobs/funnels/`: Funnels Pulse job (Gumroad/Fiverr/Upwork → one markdown snapshot).
- `out/`: Generated artifacts (PDF/CSV/MD) checked in for samples.
- `tests/`: Unit tests for parsers/generators.

## Build, Test, and Development Commands
- Python env: `python -m venv .venv && .venv\Scripts\activate`
- Install minimal deps: `pip install -r requirements.txt`
- Run a module: `python apps/contracts/main.py` (or module-specific entry).
- Run a job: `python jobs/funnels/run.py`
- Tests: `pytest -q` (targets `tests/`; add focused unit tests).

## Coding Style & Naming Conventions
- Python: PEP 8, 4 spaces; files/functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.
- Filenames: Parsers `*_parser.py`, generators `*_generator.py`, jobs `run.py`.
- Keep modules small; prefer pure functions for parse/generate steps.

## Testing Guidelines
- Place tests in `tests/` mirroring module paths: `tests/apps/contracts/test_forms_parser.py`.
- Name tests `test_*.py`; avoid network and filesystem side effects; use fixtures and sample inputs.
- Aim for coverage on parsers/generators and edge cases; verify sample outputs under `out/`.

## Commit & Pull Request Guidelines
- One PR per lane (Contracts Ops / Family Tech / Visibility).
- Commits: imperative, human-readable; prefix scope (e.g., `contracts: add pdf generator`).
- PRs: include description, linked issue, test plan, and sample artifacts in `out/`.

## Security, Config, and Approvals
- Secrets live in `.env.local`; never commit or print them. Load with `dotenv` only.
- Approvals: allowed `powershell.exe, node, python, pip, npm, pytest, git`; file RW inside repo only. Ask before network calls, system-wide installs, deletes, or pushes.

## Definition of Done
- Merged PR + passing tests + representative sample outputs committed under `out/`.

## Dev Tooling (Optional)
- Pre-commit hooks: `pip install pre-commit && pre-commit install` (uses `.pre-commit-config.yaml`).
- Ruff config: `ruff.toml` (lint: E/F/I; format via `ruff format`).
