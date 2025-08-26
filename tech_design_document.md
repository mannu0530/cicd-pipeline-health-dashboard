
# Technical Design Document

## High-Level Architecture
```
[GitHub]   [GitLab]   [Jenkins]
    \        |         /
     \       |        /           WebSocket
      \  Collector Pollers  --->  Event Bus  ---> Frontend (React)
       \     (FastAPI BG Tasks)      |
        \_____________________________|
                          |
                   REST API + DB
                (FastAPI + SQLAlchemy + Postgres)
```
- Collectors poll external providers and normalize build records.
- DB persists pipelines and build executions.
- API serves metrics and builds; WebSocket pushes updates.
- Alerting subscribers receive transitions for Slack/Email.

## Data Model (PostgreSQL)
```sql
CREATE TABLE pipelines (
  id SERIAL PRIMARY KEY,
  provider VARCHAR(16) NOT NULL,
  name TEXT NOT NULL,
  external_id TEXT,
  url TEXT,
  UNIQUE (provider, name)
);

CREATE TABLE builds (
  id BIGSERIAL PRIMARY KEY,
  pipeline_id INT REFERENCES pipelines(id) ON DELETE CASCADE,
  external_id TEXT NOT NULL,
  status VARCHAR(16) NOT NULL,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  duration_seconds INT,
  web_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (pipeline_id, external_id)
);

CREATE INDEX idx_builds_pipeline_time ON builds (pipeline_id, started_at DESC);
CREATE INDEX idx_builds_status_time ON builds (status, started_at DESC);
```

## API Structure
- `GET /api/metrics/overview` → overall success/failure rate, avg duration, last build status/time
- `GET /api/metrics/pipeline/{pipeline_id}` → per-pipeline metrics (future)
- `GET /api/builds?provider&status&limit&q` → recent builds with filters
- `GET /api/builds/{id}` → build details
- `GET /api/logs/{provider}/{external_id}` → proxied logs (stub)
- `POST /api/collect/trigger` → manual refresh
- `WS /ws` → pushes build events

## Collector Design
- BaseCollector with `list_recent_builds()` normalizing:
  `{provider, pipeline_name, external_id, status, started_at, finished_at, duration_seconds, web_url}`
- GitHub: `/repos/:owner/:repo/actions/runs`
- GitLab: `/projects/:id/pipelines`
- Jenkins: `/job/<job>/api/json` with `builds[number,result,timestamp,duration,url]`

## UI Layout
- Cards: Success Rate | Failure Rate | Avg Build Time | Last Build
- Filters: Provider, Status, Search
- Table: recent builds (pipeline, status pill, duration, started, link)
- Live indicator: WebSocket status

## Alerts
- Slack webhook JSON payload with pipeline, status, link.
- Email via SMTP with STARTTLS.

## Future Enhancements
- Provider webhooks
- Per-team routing, silence windows
- AuthN/Z and multi-tenancy
- Persistent log storage and search
