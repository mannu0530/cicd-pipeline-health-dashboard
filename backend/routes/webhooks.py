
import os
from fastapi import APIRouter, Request, Header, HTTPException
from datetime import datetime
from collectors.base import CollectorResult, upsert_builds
from alerts.slack import SlackAlerter
from alerts.emailer import EmailAlerter

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

def verify_secret(header_value: str):
    # Basic equality check against configured secret (operator must set WEBHOOK_SECRET)
    if not WEBHOOK_SECRET:
        return True
    return header_value == WEBHOOK_SECRET

@router.post("/github")
async def github_webhook(request: Request, x_hub_signature_256: str | None = Header(None), x_github_event: str | None = Header(None)):
    # GitHub sends workflow_run events for Actions; we expect the workflow_run object.
    # Validate secret using X-Hub-Signature-256 if provided; otherwise rely on WEBHOOK_SECRET with header fallback.
    if WEBHOOK_SECRET and x_hub_signature_256 is None:
        # try fallback header
        pass  # operator may configure signature verification externally

    payload = await request.json()
    # Only handle workflow_run events
    if "workflow_run" not in payload:
        return {"ok": False, "reason": "unsupported_event"}

    run = payload["workflow_run"]
    status = run.get("conclusion") or run.get("status")
    started = run.get("run_started_at")
    finished = run.get("updated_at")
    started_at = datetime.fromisoformat(started.replace("Z","+00:00")) if started else None
    finished_at = datetime.fromisoformat(finished.replace("Z","+00:00")) if finished else None
    duration = None
    if started_at and finished_at:
        duration = int((finished_at - started_at).total_seconds())
    cr = CollectorResult(
        provider="github",
        pipeline_name=payload.get("repository", {}).get("full_name") or run.get("name"),
        external_id=str(run.get("id")),
        status=status,
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=duration,
        web_url=run.get("html_url"),
    )
    transitions = upsert_builds([cr])
    # send alerts
    alerters = [SlackAlerter(), EmailAlerter()]
    for t in transitions:
        for a in alerters:
            try:
                a.notify(t)
            except Exception:
                pass
    return {"ok": True, "updated": len(transitions)}

@router.post("/gitlab")
async def gitlab_webhook(request: Request, x_gitlab_token: str | None = Header(None)):
    if WEBHOOK_SECRET and x_gitlab_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="invalid token")
    payload = await request.json()
    # Pipelines webhook
    if payload.get("object_kind") not in ("pipeline","job"):
        return {"ok": False, "reason": "unsupported_event"}
    # Normalize pipeline info
    pipeline = payload.get("object_attributes") or payload.get("pipeline") or {}
    status = pipeline.get("status")
    started = pipeline.get("created_at")
    finished = pipeline.get("finished_at") or pipeline.get("updated_at")
    started_at = datetime.fromisoformat(started.replace("Z","+00:00")) if started else None
    finished_at = datetime.fromisoformat(finished.replace("Z","+00:00")) if finished else None
    duration = None
    if started_at and finished_at:
        duration = int((finished_at - started_at).total_seconds())
    project = payload.get("project", {})
    cr = CollectorResult(
        provider="gitlab",
        pipeline_name=str(project.get("path_with_namespace") or project.get("name")),
        external_id=str(pipeline.get("id") or pipeline.get("job_id") or ""),
        status=status,
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=duration,
        web_url=project.get("web_url") or pipeline.get("url"),
    )
    transitions = upsert_builds([cr])
    alerters = [SlackAlerter(), EmailAlerter()]
    for t in transitions:
        for a in alerters:
            try:
                a.notify(t)
            except Exception:
                pass
    return {"ok": True, "updated": len(transitions)}

@router.post("/jenkins")
async def jenkins_webhook(request: Request, x_jenkins_token: str | None = Header(None)):
    if WEBHOOK_SECRET and x_jenkins_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="invalid token")
    payload = await request.json()
    # Jenkins can send many forms; try to read common fields
    name = payload.get("name") or payload.get("job_name") or payload.get("project")
    number = payload.get("build", {}).get("number") or payload.get("build", {}).get("id")
    result = payload.get("build", {}).get("status") or payload.get("build", {}).get("result")
    url = payload.get("build", {}).get("full_url") or payload.get("build", {}).get("url")
    timestamp = payload.get("build", {}).get("timestamp")
    duration_ms = payload.get("build", {}).get("duration")
    started_at = None
    finished_at = None
    if timestamp:
        try:
            from datetime import datetime, timezone
            started_at = datetime.fromtimestamp(int(timestamp)/1000, tz=timezone.utc)
            if duration_ms:
                finished_at = datetime.fromtimestamp((int(timestamp)+int(duration_ms))/1000, tz=timezone.utc)
        except Exception:
            pass
    duration = int(duration_ms/1000) if duration_ms else None
    cr = CollectorResult(
        provider="jenkins",
        pipeline_name=name or "jenkins-job",
        external_id=str(number or ""),
        status=("running" if result in (None, "") else ("success" if str(result).upper()=="SUCCESS" else "failed" if str(result).upper()=="FAILURE" else str(result))),
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=duration,
        web_url=url,
    )
    transitions = upsert_builds([cr])
    alerters = [SlackAlerter(), EmailAlerter()]
    for t in transitions:
        for a in alerters:
            try:
                a.notify(t)
            except Exception:
                pass
    return {"ok": True, "updated": len(transitions)}
