# Deployment Truth

This document exists to align the repository story with the implementation that is currently visible.

## What the Codebase Clearly Supports

The repository contains:

- a FastAPI backend at `branchberg/app/main.py`
- a Streamlit dashboard at `branchberg/dashboard/streamlit_app.py`
- a database layer at `branchberg/app/database.py`
- environment-driven configuration for `DATABASE_URL` and `API_URL`

That means the project is architected as an API + dashboard + database stack.

## What Must Be Verified Before Claiming Full Cloud Deployment

Before presenting this repo as a fully proven one-click deploy, verify all of the following in a live environment:

1. API service boots successfully from the intended deployment platform.
2. Dashboard service boots successfully and can reach the API.
3. `DATABASE_URL` is injected correctly.
4. Health and version endpoints respond successfully.
5. Manual ingest, CSV ingest, PO creation, invoice creation, and payment recording all work end to end.
6. Stripe and Gumroad webhook handlers accept and process valid events correctly.
7. Service URLs, domains, and environment variable names match the documentation.

## Current Safe Positioning

The safe and accurate deployment statement is:

> This repository contains the components required for a revenue operations stack and is structured for API + dashboard + database deployment, but production deployment should be validated against the active platform configuration before being presented as fully one-click.

## Recommended Next Deployment Cleanup

- Replace stale or mismatched platform config with a single authoritative deployment path.
- Keep one source of truth for service names.
- Add a smoke-test checklist to the README after deployment validation is complete.
- Publish the actual run commands used in production.
