"""System and webhook routes."""
import importlib.util
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from branchberg.app.database import get_db
from branchberg.app.revenue_agent.config import AgentSettings
from branchberg.app.revenue_agent.webhooks.gumroad import handle_gumroad_webhook
from branchberg.app.revenue_agent.webhooks.stripe import handle_stripe_webhook

APP_NAME = "BranchOS Revenue API"
DEFAULT_VERSION = "0.0.0"
router = APIRouter(tags=["system"])


def _load_toml(path: Path) -> Optional[dict]:
    if importlib.util.find_spec("tomllib"):
        import tomllib

        with path.open("rb") as handle:
            return tomllib.load(handle)
    if importlib.util.find_spec("tomli"):
        import tomli

        with path.open("rb") as handle:
            return tomli.load(handle)
    return None


def _find_pyproject(start: Path) -> Optional[Path]:
    for parent in [start, *start.parents]:
        candidate = parent / "pyproject.toml"
        if candidate.is_file():
            return candidate
    return None


def resolve_version() -> str:
    pyproject_path = _find_pyproject(Path(__file__).resolve())
    if not pyproject_path:
        return DEFAULT_VERSION
    try:
        toml_data = _load_toml(pyproject_path)
    except OSError:
        return DEFAULT_VERSION
    if not toml_data:
        return DEFAULT_VERSION
    return toml_data.get("project", {}).get("version") or DEFAULT_VERSION


def resolve_git_sha() -> str:
    for key in ("GIT_SHA", "GITHUB_SHA", "RAILWAY_GIT_COMMIT_SHA", "COMMIT_SHA"):
        if os.getenv(key):
            return os.getenv(key)
    return "unknown"


@router.get("/")
def read_root():
    return {"status": "ok", "service": APP_NAME}


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/version")
def version():
    return {"name": APP_NAME, "version": resolve_version(), "git_sha": resolve_git_sha()}


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    from branchberg.app.main import AGENT_SETTINGS
    settings: AgentSettings = AGENT_SETTINGS
    body, status_code = await handle_stripe_webhook(request, db, settings)
    return JSONResponse(status_code=status_code, content=body.model_dump())


@router.post("/webhooks/gumroad")
async def gumroad_webhook(request: Request, db: Session = Depends(get_db)):
    from branchberg.app.main import AGENT_SETTINGS
    settings: AgentSettings = AGENT_SETTINGS
    body, status_code = await handle_gumroad_webhook(request, db, settings)
    return JSONResponse(status_code=status_code, content=body.model_dump())

