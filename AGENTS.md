# AGENTS.md — Codex Guide
## Purpose
- Code review focus: security, error handling, env/secret hygiene, performance.
- Project areas: /branchbot, /api, deployment (Railway), tests in /branchbot/tests.

## Commands Codex may run
- python -m unittest
- uv run pytest || pytest
- ruff, mypy (if present)
- railway logs (read-only)
