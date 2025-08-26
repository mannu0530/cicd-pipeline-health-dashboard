
import os, httpx
from datetime import datetime
from .base import BaseCollector, CollectorResult

class GitLabCollector(BaseCollector):
    provider = "gitlab"

    async def list_recent_builds(self):
        token = os.getenv("GITLAB_TOKEN")
        projects = os.getenv("GITLAB_PROJECTS", "")
        headers = {"PRIVATE-TOKEN": token} if token else {}
        out = []
        if not token or not projects:
            return out
        async with httpx.AsyncClient(timeout=20) as client:
            for proj in projects.split(","):
                proj = proj.strip()
                if not proj:
                    continue
                url = f"https://gitlab.com/api/v4/projects/{proj}/pipelines?per_page=10"
                r = await client.get(url, headers=headers)
                r.raise_for_status()
                for pipe in r.json():
                    status = pipe.get("status")
                    started_at = pipe.get("created_at")
                    finished_at = pipe.get("updated_at") if status in ("success","failed","canceled","skipped") else None
                    s = datetime.fromisoformat(started_at.replace("Z","+00:00")) if started_at else None
                    f = datetime.fromisoformat(finished_at.replace("Z","+00:00")) if finished_at else None
                    dur = int((f - s).total_seconds()) if s and f else None
                    out.append(CollectorResult(
                        provider=self.provider,
                        pipeline_name=str(proj),
                        external_id=str(pipe.get("id")),
                        status=status,
                        started_at=s,
                        finished_at=f,
                        duration_seconds=dur,
                        web_url=pipe.get("web_url"),
                    ))
        return out
