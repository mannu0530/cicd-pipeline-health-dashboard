
import os, httpx
from datetime import datetime, timezone
from .base import BaseCollector, CollectorResult

class JenkinsCollector(BaseCollector):
    provider = "jenkins"

    async def list_recent_builds(self):
        base = os.getenv("JENKINS_BASE_URL")
        user = os.getenv("JENKINS_USER")
        token = os.getenv("JENKINS_API_TOKEN")
        jobs = os.getenv("JENKINS_JOBS","")
        out = []
        if not base or not user or not token or not jobs:
            return out
        auth = (user, token)
        async with httpx.AsyncClient(timeout=20, auth=auth) as client:
            for job in jobs.split(","):
                job = job.strip().strip("/")
                if not job:
                    continue
                url = f"{base}/job/{job}/api/json?tree=builds[number,result,timestamp,duration,url]{{0,10}}"
                r = await client.get(url)
                r.raise_for_status()
                data = r.json()
                for b in data.get("builds", []):
                    ts = b.get("timestamp")
                    dur = b.get("duration")
                    s = datetime.fromtimestamp(ts/1000, tz=timezone.utc) if ts else None
                    f = datetime.fromtimestamp((ts+dur)/1000, tz=timezone.utc) if ts and dur else None
                    result = b.get("result")
                    status = "running" if result is None else ("success" if result=="SUCCESS" else ("failed" if result=="FAILURE" else str(result).lower()))
                    out.append(CollectorResult(
                        provider=self.provider,
                        pipeline_name=job,
                        external_id=str(b.get("number")),
                        status=status,
                        started_at=s,
                        finished_at=f,
                        duration_seconds=int(dur/1000) if dur else None,
                        web_url=b.get("url"),
                    ))
        return out
