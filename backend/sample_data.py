from datetime import datetime, timedelta
import random
from db import get_session, Pipeline, Build
from random_data_generator import generate_random_pipeline_name, generate_random_build_status, generate_random_build_duration, generate_random_error_log

# Sample pipeline data with more variety
SAMPLE_PIPELINES = [
    # GitHub Actions - Frontend/Web apps
    {"provider": "github", "name": "frontend-app", "external_id": "12345", "url": "https://github.com/company/frontend-app", "is_active": True},
    {"provider": "github", "name": "backend-api", "external_id": "67890", "url": "https://github.com/company/backend-api", "is_active": True},
    {"provider": "github", "name": "mobile-app", "external_id": "11111", "url": "https://github.com/company/mobile-app", "is_active": True},
    {"provider": "github", "name": "docs-site", "external_id": "22222", "url": "https://github.com/company/docs-site", "is_active": True},
    
    # GitLab CI - Data/ML services
    {"provider": "gitlab", "name": "data-pipeline", "external_id": "33333", "url": "https://gitlab.com/company/data-pipeline", "is_active": True},
    {"provider": "gitlab", "name": "ml-service", "external_id": "44444", "url": "https://gitlab.com/company/ml-service", "is_active": True},
    {"provider": "gitlab", "name": "analytics-engine", "external_id": "55555", "url": "https://gitlab.com/company/analytics-engine", "is_active": True},
    {"provider": "gitlab", "name": "etl-processor", "external_id": "66666", "url": "https://gitlab.com/company/etl-processor", "is_active": True},
    
    # Jenkins - Infrastructure/Deployment
    {"provider": "jenkins", "name": "deployment-jobs", "external_id": "77777", "url": "http://jenkins.company.com/job/deployment-jobs", "is_active": True},
    {"provider": "jenkins", "name": "integration-tests", "external_id": "88888", "url": "http://jenkins.company.com/job/integration-tests", "is_active": True},
    {"provider": "jenkins", "name": "security-scan", "external_id": "99999", "url": "http://jenkins.company.com/job/security-scan", "is_active": True},
    {"provider": "jenkins", "name": "performance-tests", "external_id": "10101", "url": "http://jenkins.company.com/job/performance-tests", "is_active": True},
    {"provider": "jenkins", "name": "docker-builds", "external_id": "12121", "url": "http://jenkins.company.com/job/docker-builds", "is_active": True},
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
            
            # Use random generator for status and duration
            status = generate_random_build_status()
            duration_seconds = None
            finished_at = None
            
            if status in ["running", "pending"]:
                duration_seconds = None
                finished_at = None
            elif status == "skipped":
                duration_seconds = 0
                finished_at = started_at
            else:
                duration_seconds = generate_random_build_duration(pipeline_data["name"])
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
            
            # Generate error logs for failed builds using random generator
            logs = None
            if status == "failed":
                logs = generate_random_error_log()
            
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

def clear_sample_data():
    """Clear all sample data from the database"""
    with next(get_session()) as session:
        print("Clearing sample data...")
        
        # Delete builds first (due to foreign key constraint)
        build_count = session.query(Build).count()
        session.query(Build).delete()
        
        # Delete pipelines
        pipeline_count = session.query(Pipeline).count()
        session.query(Pipeline).delete()
        
        session.commit()
        print(f"Cleared {build_count} builds and {pipeline_count} pipelines")

def reset_sample_data():
    """Reset the database by clearing and reseeding sample data"""
    print("Resetting sample data...")
    clear_sample_data()
    seed_sample_data()
    print("✅ Sample data reset completed!")
