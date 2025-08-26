
import os
import asyncio
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select, func

from db import get_session, Build, Pipeline, init_db
from collectors.base import CollectorResult, upsert_builds
from collectors.github import GitHubCollector
from collectors.gitlab import GitLabCollector
from collectors.jenkins import JenkinsCollector
from alerts.slack import SlackAlerter
from alerts.emailer import EmailAlerter
from sample_data import seed_sample_data

# Import webhook routes
from routes import webhooks

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

app = FastAPI(title="CI/CD Pipeline Health Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://localhost:5173", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register webhooks router
app.include_router(webhooks.router)

# DB init
init_db()
# Seed with sample data for demo
seed_sample_data()

class MetricsOverview(BaseModel):
    success_rate: float
    failure_rate: float
    avg_build_time_seconds: Optional[float]
    last_build_status: Optional[str]
    last_build_at: Optional[datetime]

@app.get("/api/metrics/overview", response_model=MetricsOverview)
def metrics_overview(session=Depends(get_session)):
    total = session.scalar(select(func.count()).select_from(Build)) or 0
    success = session.scalar(select(func.count()).select_from(Build).where(Build.status=="success")) or 0
    failure = session.scalar(select(func.count()).select_from(Build).where(Build.status=="failed")) or 0
    avg = session.scalar(select(func.avg(Build.duration_seconds)))
    last = session.execute(select(Build.status, Build.started_at).order_by(Build.started_at.desc()).limit(1)).first()
    last_status, last_at = (last[0], last[1]) if last else (None, None)
    return MetricsOverview(
        success_rate = round((success/total)*100,2) if total else 0.0,
        failure_rate = round((failure/total)*100,2) if total else 0.0,
        avg_build_time_seconds = float(avg) if avg is not None else None,
        last_build_status = last_status,
        last_build_at = last_at,
    )

class BuildOut(BaseModel):
    id: int
    provider: str
    pipeline: str
    status: str
    duration_seconds: int | None
    started_at: datetime | None
    web_url: str | None

@app.get("/api/builds", response_model=List[BuildOut])
def list_builds(
    provider: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    q: Optional[str] = Query(default=None),
    session=Depends(get_session),
):
    stmt = select(Build, Pipeline).join(Pipeline, Build.pipeline_id==Pipeline.id).order_by(Build.started_at.desc()).limit(limit)
    if provider:
        stmt = stmt.where(Pipeline.provider==provider)
    if status:
        stmt = stmt.where(Build.status==status)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(Pipeline.name.ilike(like))
    rows = session.execute(stmt).all()
    results = []
    for b, p in rows:
        results.append(BuildOut(
            id=b.id,
            provider=p.provider,
            pipeline=p.name,
            status=b.status,
            duration_seconds=b.duration_seconds,
            started_at=b.started_at,
            web_url=b.web_url,
        ))
    return results

@app.get("/api/builds/{build_id}")
def get_build(build_id: int, session=Depends(get_session)):
    row = session.execute(select(Build, Pipeline).join(Pipeline, Build.pipeline_id==Pipeline.id).where(Build.id==build_id)).first()
    if not row:
        return {"error": "not found"}
    b, p = row
    return {
        "id": b.id, "provider": p.provider, "pipeline": p.name, "status": b.status,
        "duration_seconds": b.duration_seconds, "started_at": b.started_at, "finished_at": b.finished_at,
        "web_url": b.web_url, "external_id": b.external_id, "logs": b.logs
    }

@app.get("/api/logs/{provider}/{external_id}")
def get_logs(provider: str, external_id: str):
    # For demo, we do not persist full logs. Return logs column if available or instruct to fetch from provider.
    with next(get_session()) as session:
        row = session.execute(select(Build).where(Build.external_id==external_id)).scalar_one_or_none()
        if row and getattr(row, "logs", None):
            return {"provider": provider, "external_id": external_id, "logs": row.logs}
    return {"provider": provider, "external_id": external_id, "logs": "Log retrieval not implemented in demo. Use provider UI."}

@app.post("/api/collect/trigger")
async def trigger_collect():
    asyncio.create_task(run_collectors_once())
    return {"ok": True}

# WebSocket
clients: list[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    try:
        while True:
            await ws.receive_text()  # Keep alive / ignore client messages
    except WebSocketDisconnect:
        clients.remove(ws)

async def notify_clients(event: dict):
    stale = []
    for ws in clients:
        try:
            await ws.send_json(event)
        except Exception:
            stale.append(ws)
    for ws in stale:
        if ws in clients:
            clients.remove(ws)

# Background collectors
async def run_collectors_once():
    providers = os.getenv("PROVIDERS", "github,gitlab,jenkins").split(",")
    alerters = [SlackAlerter(), EmailAlerter()]
    results: list[CollectorResult] = []

    if "github" in providers:
        results += await GitHubCollector().list_recent_builds()
    if "gitlab" in providers:
        results += await GitLabCollector().list_recent_builds()
    if "jenkins" in providers:
        results += await JenkinsCollector().list_recent_builds()

    # persist and detect transitions
    transitions = upsert_builds(results)
    # alerts and websocket
    for t in transitions:
        event = {"type": "build_updated", "build": t}
        await notify_clients(event)
        for a in alerters:
            try:
                a.notify(t)
            except Exception as e:
                print("Alert error:", e)

@app.on_event("startup")
async def startup_event():
    poll = int(os.getenv("COLLECTOR_POLL_SECONDS", "30"))
    async def loop():
        while True:
            try:
                await run_collectors_once()
            except Exception as e:
                print("Collector loop error:", e)
            await asyncio.sleep(poll)
    asyncio.create_task(loop())
