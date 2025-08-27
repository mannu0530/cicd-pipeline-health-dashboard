
import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select, func, and_, desc

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
    total_builds: int
    avg_build_time_seconds: Optional[float]
    last_build_status: Optional[str]
    last_build_at: Optional[datetime]
    total_pipelines: int
    active_pipelines: int
    builds_today: int
    builds_this_week: int

class ChartDataPoint(BaseModel):
    time: str
    success: int
    failed: int
    running: int
    avg_duration: float

class BuildTrendData(BaseModel):
    date: str
    total_builds: int
    success_count: int
    failure_count: int
    avg_duration: float

class PipelineMetrics(BaseModel):
    pipeline_name: str
    total_builds: int
    success_rate: float
    avg_duration: float
    last_build_status: str
    last_build_at: Optional[datetime]

@app.get("/api/metrics/overview", response_model=MetricsOverview)
def metrics_overview(session=Depends(get_session)):
    total = session.scalar(select(func.count()).select_from(Build)) or 0
    success = session.scalar(select(func.count()).select_from(Build).where(Build.status=="success")) or 0
    failure = session.scalar(select(func.count()).select_from(Build).where(Build.status=="failed")) or 0
    avg = session.scalar(select(func.avg(Build.duration_seconds)))
    last = session.execute(select(Build.status, Build.started_at).order_by(Build.started_at.desc()).limit(1)).first()
    last_status, last_at = (last[0], last[1]) if last else (None, None)
    
    # Additional metrics
    total_pipelines = session.scalar(select(func.count()).select_from(Pipeline)) or 0
    active_pipelines = session.scalar(select(func.count()).select_from(Pipeline).where(Pipeline.is_active == True)) or 0
    
    # Time-based metrics
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    builds_today = session.scalar(select(func.count()).select_from(Build).where(
        func.date(Build.started_at) == today
    )) or 0
    builds_this_week = session.scalar(select(func.count()).select_from(Build).where(
        Build.started_at >= week_ago
    )) or 0
    
    return MetricsOverview(
        success_rate = round((success/total)*100,2) if total else 0.0,
        failure_rate = round((failure/total)*100,2) if total else 0.0,
        total_builds = total,
        avg_build_time_seconds = float(avg) if avg is not None else None,
        last_build_status = last_status,
        last_build_at = last_at,
        total_pipelines = total_pipelines,
        active_pipelines = active_pipelines,
        builds_today = builds_today,
        builds_this_week = builds_this_week,
    )

@app.get("/api/metrics/chart-data", response_model=List[ChartDataPoint])
def get_chart_data(
    days: int = Query(default=7, ge=1, le=30),
    session=Depends(get_session)
):
    """Get time-series chart data for the specified number of days"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Group builds by day and calculate metrics
    stmt = select(
        func.date(Build.started_at).label('date'),
        func.count().label('total'),
        func.sum(func.case((Build.status == 'success', 1), else_=0)).label('success'),
        func.sum(func.case((Build.status == 'failed', 1), else_=0)).label('failed'),
        func.sum(func.case((Build.status == 'running', 1), else_=0)).label('running'),
        func.avg(Build.duration_seconds).label('avg_duration')
    ).where(
        Build.started_at >= start_date
    ).group_by(
        func.date(Build.started_at)
    ).order_by(
        func.date(Build.started_at)
    )
    
    results = session.execute(stmt).all()
    
    chart_data = []
    for row in results:
        chart_data.append(ChartDataPoint(
            time=row.date.strftime('%m/%d'),
            success=row.success or 0,
            failed=row.failed or 0,
            running=row.running or 0,
            avg_duration=float(row.avg_duration) if row.avg_duration else 0.0
        ))
    
    return chart_data

@app.get("/api/metrics/build-trends", response_model=List[BuildTrendData])
def get_build_trends(
    days: int = Query(default=14, ge=1, le=90),
    session=Depends(get_session)
):
    """Get build trend data over time"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    stmt = select(
        func.date(Build.started_at).label('date'),
        func.count().label('total_builds'),
        func.sum(func.case((Build.status == 'success', 1), else_=0)).label('success_count'),
        func.sum(func.case((Build.status == 'failed', 1), else_=0)).label('failure_count'),
        func.avg(Build.duration_seconds).label('avg_duration')
    ).where(
        Build.started_at >= start_date
    ).group_by(
        func.date(Build.started_at)
    ).order_by(
        func.date(Build.started_at)
    )
    
    results = session.execute(stmt).all()
    
    trend_data = []
    for row in results:
        trend_data.append(BuildTrendData(
            date=row.date.strftime('%Y-%m-%d'),
            total_builds=row.total_builds or 0,
            success_count=row.success_count or 0,
            failure_count=row.failure_count or 0,
            avg_duration=float(row.avg_duration) if row.avg_duration else 0.0
        ))
    
    return trend_data

@app.get("/api/metrics/pipeline-performance", response_model=List[PipelineMetrics])
def get_pipeline_performance(
    limit: int = Query(default=10, ge=1, le=50),
    session=Depends(get_session)
):
    """Get performance metrics for individual pipelines"""
    stmt = select(
        Pipeline.name,
        func.count(Build.id).label('total_builds'),
        func.avg(func.case((Build.status == 'success', 1), else_=0)).label('success_rate'),
        func.avg(Build.duration_seconds).label('avg_duration'),
        func.max(Build.status).label('last_build_status'),
        func.max(Build.started_at).label('last_build_at')
    ).join(
        Build, Pipeline.id == Build.pipeline_id
    ).group_by(
        Pipeline.id, Pipeline.name
    ).order_by(
        desc(func.count(Build.id))
    ).limit(limit)
    
    results = session.execute(stmt).all()
    
    pipeline_metrics = []
    for row in results:
        pipeline_metrics.append(PipelineMetrics(
            pipeline_name=row.name,
            total_builds=row.total_builds or 0,
            success_rate=round((row.success_rate or 0) * 100, 2),
            avg_duration=float(row.avg_duration) if row.avg_duration else 0.0,
            last_build_status=row.last_build_status or 'unknown',
            last_build_at=row.last_build_at
        ))
    
    return pipeline_metrics

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
