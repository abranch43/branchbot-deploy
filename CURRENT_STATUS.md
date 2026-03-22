# Current Status

This document is the source of truth for what `branchbot-deploy` is today.

## Product Identity

**Primary product identity:** BranchOS Revenue Stack  
**Repository name:** `branchbot-deploy`  
**Purpose:** revenue ingest, PO-to-paid lifecycle tracking, audit visibility, and operator dashboarding.

The repo currently contains a FastAPI backend, a Streamlit dashboard, and a database layer for revenue and billing operations.

## Working Now

The following capabilities are implemented in the repository and reflected in the application code:

- FastAPI application with health and version endpoints
- Manual transaction ingest
- CSV transaction ingest
- Revenue summary endpoint
- Revenue event history endpoint
- Purchase order creation
- Invoice creation from purchase orders
- Payment recording against invoices
- Audit logging for PO / invoice / payment actions
- Stripe webhook endpoint
- Gumroad webhook endpoint
- Streamlit dashboard with manual entry, CSV upload, summary, and history views
- SQLite fallback for local development and PostgreSQL support through `DATABASE_URL`

## Partially Implemented / Needs Validation

These capabilities are present in docs or code paths but should be treated as requiring deployment validation before production claims are made:

- Full multi-service cloud deployment flow
- Production-ready webhook signature enforcement across all providers
- CI as a strict blocker for code quality regressions
- End-to-end production dashboard and API service orchestration
- Security controls beyond the code paths already visible in the repository

## Not Yet Proven in This Repository

The following should not be presented as complete without additional implementation or deployment proof:

- Full one-click production deployment with zero manual adjustments
- Comprehensive enterprise security posture
- Complete API documentation set
- Mature migration system for schema evolution
- Hardened operations runbooks for incident response and recovery

## Recommended Positioning

Use this repository as:

- an internal operating system prototype,
- a deployable foundation for revenue and billing workflows,
- and a proof-of-capability asset for BranchOS / A+ Enterprise automation work.

Do **not** present it as a finished commercial SaaS product without completing deployment validation and cleanup.
