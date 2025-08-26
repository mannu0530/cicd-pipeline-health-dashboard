
# CI/CD Pipeline Health Dashboard

Monitor build executions across **GitHub Actions**, **GitLab CI**, and **Jenkins**. View real‑time metrics, inspect logs, and get Slack/Email alerts on failures or successes.

## Quick Start

```bash
git clone <your-repo-url>
cd cicd-pipeline-health-dashboard
cp env.example .env
# Edit .env with your DB creds, provider tokens and alert settings
docker compose up --build
```

**Note**: The application automatically loads with sample data for demonstration purposes. See [SAMPLE_DATA_README.md](SAMPLE_DATA_README.md) for details.

### GitHub Actions Integration

For detailed GitHub Actions monitoring setup, see [GITHUB_ACTIONS_INTEGRATION.md](GITHUB_ACTIONS_INTEGRATION.md) or run the setup script:

```bash
./setup_github_integration.sh
```

- Frontend: http://localhost:5173
- Backend (OpenAPI docs): http://localhost:8000/docs
- DB: Postgres on localhost:5432

## Architecture Summary

- **Frontend (React + Vite)**: Metrics cards, builds table, build details & log viewer. Connects to backend REST + WebSocket.
- **Backend (FastAPI)**: Collectors for GitHub/GitLab/Jenkins, REST API for metrics/builds/logs, WebSocket for near real‑time updates, alerting via Slack + Email.
- **DB (PostgreSQL + SQLAlchemy)**: Stores providers, pipelines, builds, and logs metadata.
- **Background collector**: Polls providers on an interval, stores results, triggers alerts on state changes.
- **Containerization**: `docker-compose` for local dev.

## Setup & Run

1. Copy `.env.example` to `.env` and set tokens (GitHub PAT, GitLab PAT, Jenkins URL & token), Slack webhook and SMTP creds.
2. Start services:

```bash
docker compose up --build
```

3. Open the frontend (http://localhost:5173) and backend docs (http://localhost:8000/docs).

## How AI Tools Were Used (with prompt examples)

- Drafted requirement analysis, technical design, and scaffolding prompts.
- Generated starter collectors, alerting stubs, SQLAlchemy models, and React components.

**Prompt examples**:
- "Design a FastAPI backend with collectors for GitHub/GitLab/Jenkins that tracks build status and times, and exposes metrics endpoints and a WebSocket feed."
- "Create a minimal React dashboard with cards for success rate, average build time, last build status, and a builds table with filtering."
- "Write Dockerfiles for backend and frontend, and a docker-compose with Postgres and healthchecks."

## Key Learnings & Assumptions

- Provider APIs differ in pagination and auth; collectors abstract specifics behind a common model.
- WebSocket push + polling balances simplicity with near real‑time UX.
- Alerts deduplicated on state change (e.g., only notify when a build transitions).

## Security Notes

- Store tokens in environment variables; never commit secrets.
- Restrict CORS to your frontend origin.
- Consider rotating tokens and using secrets managers in production.

---

**Docs in repo**:  
- `prompot_logs.md`  
- `requirement_analysis_document.md`  
- `tech_design_document.md`

Generated: 2025-08-26


## Webhooks Support

The backend exposes webhook endpoints to receive events from providers:

- POST `/api/webhooks/github` for GitHub Actions (`workflow_run` events)
- POST `/api/webhooks/gitlab` for GitLab pipeline/job events
- POST `/api/webhooks/jenkins` for Jenkins job notifications

Set `WEBHOOK_SECRET` in `.env` and configure your provider to send this token in the provider's webhook secret or header (`X-Gitlab-Token`, `X-Jenkins-Token`).

## Frontend

- Added charts (recharts) for success/failure trends and average build time.
- Log viewer component to fetch logs from backend stub.
- Dark/light toggle.
