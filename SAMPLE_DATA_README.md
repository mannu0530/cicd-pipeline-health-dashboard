# Sample Data for CI/CD Pipeline Health Dashboard

This document describes the sample data that has been added to demonstrate the CI/CD Dashboard functionality.

## Overview

The sample data includes realistic CI/CD pipeline information across three major providers:
- **GitHub Actions** (4 pipelines)
- **GitLab CI** (4 pipelines) 
- **Jenkins** (5 pipelines)

## Sample Pipelines

### GitHub Actions
- `frontend-app` - React frontend application
- `backend-api` - Node.js/Python backend API
- `mobile-app` - React Native mobile application
- `docs-site` - Documentation website

### GitLab CI
- `data-pipeline` - Data processing workflows
- `ml-service` - Machine learning model training
- `analytics-engine` - Analytics data processing
- `etl-processor` - Extract, Transform, Load operations

### Jenkins
- `deployment-jobs` - Kubernetes deployment automation
- `integration-tests` - End-to-end testing suite
- `security-scan` - Security vulnerability scanning
- `performance-tests` - Load and performance testing
- `docker-builds` - Docker image building and testing

## Sample Build Data

### Build Distribution
- **Total builds**: 300-400 builds across all pipelines
- **Time range**: Last 30 days with realistic distribution
- **Build frequency**: 20-35 builds per pipeline

### Status Distribution
- **Success**: 65% (realistic for mature CI/CD)
- **Failed**: 20% (includes various failure scenarios)
- **Running**: 5% (currently executing builds)
- **Pending**: 5% (queued builds)
- **Cancelled**: 3% (manually cancelled)
- **Skipped**: 2% (conditional builds)

### Build Durations
Build times vary by pipeline type:
- **ML/Data pipelines**: 30 minutes - 2 hours
- **Analytics/ETL**: 15 minutes - 1 hour
- **Deployment jobs**: 5 minutes - 30 minutes
- **Security/Performance tests**: 10 minutes - 40 minutes
- **Docker builds**: 3 minutes - 15 minutes
- **Standard builds**: 2 minutes - 45 minutes

## Sample Error Logs

Failed builds include realistic error scenarios:
1. **Test failures** - Unit and integration test failures
2. **Compilation errors** - Syntax errors and missing dependencies
3. **Deployment timeouts** - Kubernetes resource issues
4. **Security failures** - Vulnerability detections
5. **Performance regressions** - Response time and memory issues

## Data Generation

The sample data is automatically generated when the application starts, ensuring:
- Realistic timestamps with recent bias
- Varied build durations based on pipeline type
- Provider-specific external IDs and URLs
- Meaningful error messages for failed builds
- No duplicate data on subsequent runs

## Usage

### Automatic Seeding
The sample data is automatically loaded when the backend starts:
```bash
docker compose up --build
```

### Manual Seeding
To manually seed the database:
```bash
cd backend
python seed_db.py
```

### Viewing the Data
1. **Frontend Dashboard**: http://localhost:5173
   - Metrics cards showing success/failure rates
   - Charts displaying trends over time
   - Builds table with filtering options
   - Log viewer for failed builds

2. **API Endpoints**: http://localhost:8000/docs
   - `/api/metrics/overview` - Overall metrics
   - `/api/builds` - List of builds with filters
   - `/api/builds/{id}` - Individual build details
   - `/api/logs/{provider}/{external_id}` - Build logs

## Customization

To modify the sample data:
1. Edit `backend/sample_data.py`
2. Modify `SAMPLE_PIPELINES` list
3. Adjust `STATUS_WEIGHTS` for different failure rates
4. Customize build duration ranges
5. Add new error log templates

## Notes

- Sample data is only created if no existing data exists
- Build IDs and external IDs are randomly generated
- URLs point to example domains (not real repositories)
- Error logs are templates with randomized values
- Data represents a realistic CI/CD environment for demonstration purposes
