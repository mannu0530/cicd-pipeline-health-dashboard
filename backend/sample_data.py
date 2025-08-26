from datetime import datetime, timedelta
import random
from db import get_session, Pipeline, Build

# Sample pipeline data with more variety
SAMPLE_PIPELINES = [
    # GitHub Actions - Frontend/Web apps
    {"provider": "github", "name": "frontend-app", "external_id": "12345", "url": "https://github.com/company/frontend-app"},
    {"provider": "github", "name": "backend-api", "external_id": "67890", "url": "https://github.com/company/backend-api"},
    {"provider": "github", "name": "mobile-app", "external_id": "11111", "url": "https://github.com/company/mobile-app"},
    {"provider": "github", "name": "docs-site", "external_id": "22222", "url": "https://github.com/company/docs-site"},
    
    # GitLab CI - Data/ML services
    {"provider": "gitlab", "name": "data-pipeline", "external_id": "33333", "url": "https://gitlab.com/company/data-pipeline"},
    {"provider": "gitlab", "name": "ml-service", "external_id": "44444", "url": "https://gitlab.com/company/ml-service"},
    {"provider": "gitlab", "name": "analytics-engine", "external_id": "55555", "url": "https://gitlab.com/company/analytics-engine"},
    {"provider": "gitlab", "name": "etl-processor", "external_id": "66666", "url": "https://gitlab.com/company/etl-processor"},
    
    # Jenkins - Infrastructure/Deployment
    {"provider": "jenkins", "name": "deployment-jobs", "external_id": "77777", "url": "http://jenkins.company.com/job/deployment-jobs"},
    {"provider": "jenkins", "name": "integration-tests", "external_id": "88888", "url": "http://jenkins.company.com/job/integration-tests"},
    {"provider": "jenkins", "name": "security-scan", "external_id": "99999", "url": "http://jenkins.company.com/job/security-scan"},
    {"provider": "jenkins", "name": "performance-tests", "external_id": "10101", "url": "http://jenkins.company.com/job/performance-tests"},
    {"provider": "jenkins", "name": "docker-builds", "external_id": "12121", "url": "http://jenkins.company.com/job/docker-builds"},
]

# Enhanced build statuses with more realistic distribution
BUILD_STATUSES = ["success", "failed", "running", "cancelled", "pending", "skipped"]
STATUS_WEIGHTS = [0.65, 0.20, 0.05, 0.03, 0.05, 0.02]  # More realistic failure rate

def generate_sample_builds():
    """Generate realistic sample build data with better distribution"""
    builds = []
    now = datetime.utcnow()
    
    for pipeline_data in SAMPLE_PIPELINES:
        pipeline_id = pipeline_data.get("id")  # Will be set after pipeline creation
        
        # Generate 20-35 builds per pipeline over the last 30 days
        num_builds = random.randint(20, 35)
        
        for i in range(num_builds):
            # Random start time within last 30 days, with more recent builds
            days_ago = random.betavariate(2, 5) * 30  # Beta distribution for more recent bias
            started_at = now - timedelta(days=days_ago)
            
            # Random status based on weights
            status = random.choices(BUILD_STATUSES, weights=STATUS_WEIGHTS)[0]
            
            # Duration varies by status, pipeline type, and provider
            if status in ["running", "pending"]:
                duration_seconds = None
                finished_at = None
            elif status == "skipped":
                duration_seconds = 0
                finished_at = started_at
            else:
                # Realistic build durations based on pipeline type
                if "ml-service" in pipeline_data["name"] or "data-pipeline" in pipeline_data["name"]:
                    duration_seconds = random.randint(1800, 7200)  # 30 min - 2 hours
                elif "analytics" in pipeline_data["name"] or "etl" in pipeline_data["name"]:
                    duration_seconds = random.randint(900, 3600)   # 15 min - 1 hour
                elif "deployment" in pipeline_data["name"]:
                    duration_seconds = random.randint(300, 1800)   # 5 min - 30 min
                elif "security" in pipeline_data["name"] or "performance" in pipeline_data["name"]:
                    duration_seconds = random.randint(600, 2400)   # 10 min - 40 min
                elif "docker" in pipeline_data["name"]:
                    duration_seconds = random.randint(180, 900)    # 3 min - 15 min
                else:
                    duration_seconds = random.randint(120, 2700)   # 2 min - 45 min
                
                finished_at = started_at + timedelta(seconds=duration_seconds)
            
            # External ID format varies by provider
            if pipeline_data["provider"] == "github":
                external_id = f"gh-{random.randint(1000000, 9999999)}"
            elif pipeline_data["provider"] == "gitlab":
                external_id = f"gl-{random.randint(100000, 999999)}"
            else:  # jenkins
                external_id = f"jk-{random.randint(1000, 99999)}"
            
            # Web URL
            if pipeline_data["provider"] == "github":
                web_url = f"{pipeline_data['url']}/actions/runs/{external_id}"
            elif pipeline_data["provider"] == "gitlab":
                web_url = f"{pipeline_data['url']}/-/pipelines/{external_id}"
            else:  # jenkins
                web_url = f"{pipeline_data['url']}/{external_id}"
            
            # Sample logs for failed builds with different error types
            logs = None
            if status == "failed":
                error_types = [
                    f"""Build failed at {finished_at}
Error: Test suite failed
- Unit tests: {random.randint(1, 5)} failures
- Integration tests: {random.randint(0, 3)} failures
- Build step 'npm test' exited with code 1
See full logs at: {web_url}""",
                    
                    f"""Build failed at {finished_at}
Error: Compilation error
- Syntax error in src/main.js:45
- Missing dependency: lodash
- Build step 'npm run build' failed
See full logs at: {web_url}""",
                    
                    f"""Build failed at {finished_at}
Error: Deployment timeout
- Kubernetes deployment stuck in pending state
- Resource quota exceeded
- Build step 'kubectl apply' timed out
See full logs at: {web_url}""",
                    
                    f"""Build failed at {finished_at}
Error: Security scan failed
- High severity vulnerability detected
- CVE-2024-1234: SQL injection in login form
- Build step 'security-scan' failed
See full logs at: {web_url}""",
                    
                    f"""Build failed at {finished_at}
Error: Performance regression
- Response time increased by 45%
- Memory usage exceeded threshold
- Build step 'performance-test' failed
See full logs at: {web_url}"""
                ]
                logs = random.choice(error_types)
            
            builds.append({
                "pipeline_id": pipeline_id,
                "external_id": external_id,
                "status": status,
                "started_at": started_at,
                "finished_at": finished_at,
                "duration_seconds": duration_seconds,
                "web_url": web_url,
                "event_source": "sample_data",
                "logs": logs
            })
    
    return builds

def seed_sample_data():
    """Seed the database with sample data"""
    with next(get_session()) as session:
        # Check if data already exists
        existing_pipelines = session.query(Pipeline).count()
        if existing_pipelines > 0:
            print("Sample data already exists, skipping...")
            return
        
        print("Seeding database with sample data...")
        
        # Create pipelines
        for pipeline_data in SAMPLE_PIPELINES:
            pipeline = Pipeline(**pipeline_data)
            session.add(pipeline)
        
        session.commit()
        
        # Get pipeline IDs for builds
        pipelines = session.query(Pipeline).all()
        pipeline_map = {p.name: p.id for p in pipelines}
        
        # Update pipeline IDs in sample data
        for pipeline_data in SAMPLE_PIPELINES:
            pipeline_data["id"] = pipeline_map[pipeline_data["name"]]
        
        # Generate and create builds
        builds_data = generate_sample_builds()
        for build_data in builds_data:
            build = Build(**build_data)
            session.add(build)
        
        session.commit()
        print(f"Created {len(SAMPLE_PIPELINES)} pipelines and {len(builds_data)} builds")
        print("Sample data includes:")
        print(f"- {len([p for p in SAMPLE_PIPELINES if p['provider'] == 'github'])} GitHub Actions pipelines")
        print(f"- {len([p for p in SAMPLE_PIPELINES if p['provider'] == 'gitlab'])} GitLab CI pipelines") 
        print(f"- {len([p for p in SAMPLE_PIPELINES if p['provider'] == 'jenkins'])} Jenkins pipelines")
        print(f"- Builds spanning the last 30 days with realistic status distribution")
        print(f"- Sample error logs for failed builds")
