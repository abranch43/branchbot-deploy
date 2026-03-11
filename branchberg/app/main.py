"""FastAPI backend for revenue tracking and PO-to-paid workflow."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from branchberg.app.database import init_db
from branchberg.app.routes.po_flow import router as po_flow_router
from branchberg.app.routes.revenue import router as revenue_router
from branchberg.app.revenue_agent.config import AgentSettings
from branchberg.app.routes.system import APP_NAME, router as system_router


AGENT_SETTINGS = AgentSettings.from_env()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    app.state.agent_settings = AGENT_SETTINGS
    yield


app = FastAPI(title=APP_NAME, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system_router)
app.include_router(revenue_router)
app.include_router(po_flow_router)
