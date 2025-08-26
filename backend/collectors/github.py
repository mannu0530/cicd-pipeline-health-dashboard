
import os, httpx
from datetime import datetime
from .base import BaseCollector, CollectorResult

class GitHubCollector(BaseCollector):
    provider = "github"

    async def list_recent_builds(self):
        token = os.getenv("GITHUB_TOKEN")
        repos = os.getenv("GITHUB_REPOS", "")
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        out = []
        if not token or not repos:
            return out
        async with httpx.AsyncClient(timeout=20) as client:
            for repo in repos.split(","):
                repo = repo.strip()
                if not repo:
                    continue
                url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=10"
                r = await client.get(url, headers=headers)
                r.raise_for_status()
                data = r.json()
                for run in data.get("workflow_runs", []):
                    status = "running" if run.get("status") in ("in_progress","queued") else (
                        "success" if run.get("conclusion")=="success" else (
                        "failed" if run.get("conclusion")=="failure" else (run.get("conclusion") or run.get("status"))
                    ))
                    started = run.get("run_started_at")
                    updated = run.get("updated_at")
                    s = datetime.fromisoformat(started.replace("Z","+00:00")) if started else None
                    f = datetime.fromisoformat(updated.replace("Z","+00:00")) if updated and status in ("success","failed","cancelled","skipped") else None
                    dur = int((f - s).total_seconds()) if s and f else None
                    out.append(CollectorResult(
                        provider=self.provider,
                        pipeline_name=repo,
                        external_id=str(run.get("id")),
                        status=str(status),
                        started_at=s,
                        finished_at=f,
                        duration_seconds=dur,
                        web_url=run.get("html_url"),
                    ))
        return out
