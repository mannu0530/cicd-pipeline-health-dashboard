
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from db import SessionLocal, Pipeline, Build

@dataclass
class CollectorResult:
    provider: str
    pipeline_name: str
    external_id: str
    status: str
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    duration_seconds: Optional[int]
    web_url: Optional[str]

class BaseCollector:
    provider: str
    async def list_recent_builds(self) -> List[CollectorResult]:
        return []

def upsert_builds(results: List[CollectorResult]):
    transitions = []
    with SessionLocal() as session:
        for r in results:
            pipeline = session.execute(
                select(Pipeline).where(Pipeline.provider==r.provider, Pipeline.name==r.pipeline_name)
            ).scalar_one_or_none()
            if not pipeline:
                pipeline = Pipeline(provider=r.provider, name=r.pipeline_name, url=r.web_url)
                session.add(pipeline)
                session.flush()
            build = session.execute(
                select(Build).where(Build.pipeline_id==pipeline.id, Build.external_id==r.external_id)
            ).scalar_one_or_none()
            if not build:
                build = Build(
                    pipeline_id=pipeline.id,
                    external_id=r.external_id,
                    status=r.status,
                    started_at=r.started_at,
                    finished_at=r.finished_at,
                    duration_seconds=r.duration_seconds,
                    web_url=r.web_url,
                )
                session.add(build)
                transitions.append({
                    "pipeline": r.pipeline_name,
                    "provider": r.provider,
                    "external_id": r.external_id,
                    "status_old": None,
                    "status_new": r.status,
                    "web_url": r.web_url,
                    "duration_seconds": r.duration_seconds,
                    "started_at": r.started_at.isoformat() if r.started_at else None,
                })
            else:
                if build.status != r.status or build.duration_seconds != r.duration_seconds:
                    old = build.status
                    build.status = r.status
                    build.started_at = r.started_at
                    build.finished_at = r.finished_at
                    build.duration_seconds = r.duration_seconds
                    build.web_url = r.web_url or build.web_url
                    transitions.append({
                        "pipeline": r.pipeline_name,
                        "provider": r.provider,
                        "external_id": r.external_id,
                        "status_old": old,
                        "status_new": r.status,
                        "web_url": r.web_url,
                        "duration_seconds": r.duration_seconds,
                        "started_at": r.started_at.isoformat() if r.started_at else None,
                    })
        session.commit()
    return transitions
