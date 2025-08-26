# GitHub Actions Integration Guide

This guide provides detailed steps for monitoring GitHub Actions pipelines and integrating them with the CI/CD Pipeline Health Dashboard.

## Overview

The dashboard supports GitHub Actions integration through two methods:
1. **Polling-based collection** - Periodic API calls to fetch workflow runs
2. **Webhook-based updates** - Real-time notifications when workflows complete

## Prerequisites

### 1. GitHub Personal Access Token (PAT)
- Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
- Click "Generate new token (classic)"
- Select scopes:
  - `repo` - Full control of private repositories
  - `workflow` - Update GitHub Action workflows
  - `read:org` - Read organization data (if monitoring org repos)
- Copy the generated token

### 2. Repository Access
- Ensure the token has access to all repositories you want to monitor
- For organization repositories, the token owner must have access

## Configuration

### 1. Environment Variables
Add these to your `.env` file:

```bash
# GitHub Configuration
GITHUB_TOKEN=ghp_your_token_here
GITHUB_REPOS=owner/repo1,owner/repo2,org/repo3

# Webhook Configuration (optional)
WEBHOOK_SECRET=your_webhook_secret_here
FRONTEND_ORIGIN=http://localhost:5173
```

### 2. Repository Format
The `GITHUB_REPOS` variable accepts comma-separated repository names:
- **User repositories**: `username/repository-name`
- **Organization repositories**: `org-name/repository-name`
- **Multiple repositories**: `owner/repo1,owner/repo2,org/repo3`

Example:
```bash
GITHUB_REPOS=mycompany/frontend-app,mycompany/backend-api,mycompany/mobile-app
```

## Integration Methods

### Method 1: Polling-Based Collection (Recommended for Start)

The dashboard automatically polls GitHub Actions API every 30 seconds (configurable) to fetch recent workflow runs.

#### How It Works:
1. **Background Task**: Runs every `COLLECTOR_POLL_SECONDS` (default: 30)
2. **API Calls**: Fetches up to 10 recent runs per repository
3. **Data Processing**: Normalizes workflow run data into dashboard format
4. **Database Storage**: Updates local database with latest build information

#### Configuration:
```bash
# Polling interval (seconds)
COLLECTOR_POLL_SECONDS=30

# Number of recent runs to fetch per repository
# (This is hardcoded to 10 in the current implementation)
```

#### Advantages:
- Simple setup
- No external webhook configuration required
- Works with private repositories
- Handles network issues gracefully

#### Disadvantages:
- 30-second delay for updates
- API rate limiting considerations
- Higher API usage

### Method 2: Webhook-Based Updates (Real-time)

For real-time updates, configure GitHub webhooks to notify the dashboard when workflows complete.

#### 1. Configure GitHub Webhook

**For Individual Repository:**
1. Go to your repository on GitHub
2. Click **Settings** → **Webhooks** → **Add webhook**
3. Configure:
   - **Payload URL**: `https://your-dashboard-domain.com/api/webhooks/github`
   - **Content type**: `application/json`
   - **Secret**: Set the same value as `WEBHOOK_SECRET` in your `.env`
   - **Events**: Select "Let me select individual events"
   - **Events to send**: Check "Workflow runs"
4. Click **Add webhook**

**For Organization (Multiple Repositories):**
1. Go to your organization on GitHub
2. Click **Settings** → **Webhooks** → **Add webhook**
3. Configure the same settings as above
4. The webhook will apply to all repositories in the organization

#### 2. Webhook Security

The dashboard validates webhooks using the `WEBHOOK_SECRET`:
```bash
# Set a strong, unique secret
WEBHOOK_SECRET=your_super_secret_webhook_key_here
```

#### 3. Webhook Payload Processing

The dashboard automatically processes these GitHub webhook events:
- `workflow_run` - When a workflow run starts, completes, or fails
- Automatically extracts:
  - Repository name
  - Workflow run ID
  - Status and conclusion
  - Start/finish times
  - Duration
  - Web URL

## Monitoring Features

### 1. Real-time Dashboard Updates
- **WebSocket Connection**: Frontend receives live updates via WebSocket
- **Build Status Changes**: Immediate notification when builds transition states
- **Metrics Updates**: Success/failure rates update in real-time

### 2. Build Information Displayed
- **Pipeline Name**: Repository name (e.g., `mycompany/frontend-app`)
- **Build Status**: `success`, `failed`, `running`, `cancelled`, `skipped`
- **Timing**: Start time, finish time, duration
- **Links**: Direct link to GitHub Actions run
- **Provider**: Identified as "github"

### 3. Filtering and Search
- Filter by provider (GitHub)
- Filter by status
- Search by pipeline name
- Sort by build time

### 4. Metrics and Analytics
- **Success Rate**: Percentage of successful builds
- **Failure Rate**: Percentage of failed builds
- **Average Build Time**: Mean duration across all builds
- **Trends**: Success/failure patterns over time

## Advanced Configuration

### 1. Custom Workflow Status Mapping

The dashboard automatically maps GitHub workflow statuses:
```python
# GitHub Status → Dashboard Status
"in_progress" → "running"
"queued" → "running"
"success" → "success"
"failure" → "failed"
"cancelled" → "cancelled"
"skipped" → "skipped"
"neutral" → "success"  # Treated as success
"timed_out" → "failed"  # Treated as failed
```

### 2. Repository-Specific Configuration

For different polling intervals or API limits per repository, you can modify the collector:

```python
# In backend/collectors/github.py
async def list_recent_builds(self):
    # Customize per repository
    repo_configs = {
        "owner/repo1": {"per_page": 20, "poll_interval": 15},
        "owner/repo2": {"per_page": 10, "poll_interval": 60},
    }
    # ... implementation
```

### 3. Rate Limiting Considerations

GitHub API has rate limits:
- **Authenticated requests**: 5,000 requests per hour
- **Unauthenticated requests**: 60 requests per hour

With the default 30-second polling:
- 2 requests per minute × 60 minutes = 120 requests per hour
- Safe for monitoring up to 40+ repositories

## Troubleshooting

### 1. Common Issues

**"GitHub API rate limit exceeded"**
- Increase `COLLECTOR_POLL_SECONDS` to reduce API calls
- Check if you're monitoring too many repositories
- Verify your token has sufficient permissions

**"Repository not found"**
- Verify the repository name format in `GITHUB_REPOS`
- Ensure your token has access to the repository
- Check if the repository is private and your token has `repo` scope

**Webhook not receiving events**
- Verify the webhook URL is accessible from GitHub
- Check the webhook secret matches `WEBHOOK_SECRET`
- Ensure "Workflow runs" events are selected
- Check webhook delivery logs in GitHub

### 2. Debugging

**Enable API Logging:**
```python
# In backend/collectors/github.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Check Webhook Payloads:**
```python
# In backend/routes/webhooks.py
@app.post("/github")
async def github_webhook(request: Request, ...):
    payload = await request.json()
    print(f"GitHub webhook payload: {payload}")  # Debug logging
    # ... rest of the code
```

**Monitor Database:**
```sql
-- Check if builds are being stored
SELECT provider, COUNT(*) FROM builds WHERE provider = 'github' GROUP BY provider;

-- Check recent GitHub builds
SELECT * FROM builds b 
JOIN pipelines p ON b.pipeline_id = p.id 
WHERE p.provider = 'github' 
ORDER BY b.started_at DESC 
LIMIT 10;
```

## Best Practices

### 1. Security
- Use environment variables for sensitive data
- Rotate GitHub tokens regularly
- Use strong webhook secrets
- Limit token scopes to minimum required

### 2. Performance
- Start with polling for simple setups
- Use webhooks for real-time requirements
- Monitor API rate limits
- Adjust polling intervals based on needs

### 3. Monitoring
- Set up alerts for webhook failures
- Monitor API rate limit usage
- Track build success/failure trends
- Regular review of monitored repositories

### 4. Scaling
- Monitor multiple repositories efficiently
- Use organization webhooks when possible
- Consider separate tokens for different repository groups
- Implement caching for frequently accessed data

## Example Workflow

Here's a complete example of setting up GitHub Actions monitoring:

### 1. Setup Environment
```bash
# .env file
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_REPOS=mycompany/frontend-app,mycompany/backend-api
WEBHOOK_SECRET=my_webhook_secret_123
COLLECTOR_POLL_SECONDS=30
```

### 2. Start the Dashboard
```bash
docker compose up --build
```

### 3. Configure Webhook (Optional)
- Go to `mycompany/frontend-app` repository
- Settings → Webhooks → Add webhook
- URL: `https://your-domain.com/api/webhooks/github`
- Secret: `my_webhook_secret_123`
- Events: Workflow runs

### 4. Monitor Results
- Dashboard: http://localhost:5173
- API Docs: http://localhost:8000/docs
- Real-time updates via WebSocket
- Build history and metrics

## Next Steps

After setting up GitHub Actions integration:
1. **Configure GitLab CI** integration for additional pipelines
2. **Set up Jenkins** monitoring for legacy systems
3. **Configure alerts** for Slack/Email notifications
4. **Customize the dashboard** for your team's needs
5. **Set up monitoring** for the dashboard itself

For additional help, refer to:
- [Sample Data Guide](SAMPLE_DATA_README.md)
- [Technical Design Document](tech_design_document.md)
- [API Documentation](http://localhost:8000/docs) (when running)
