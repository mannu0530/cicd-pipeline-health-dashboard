"""
Random Pipeline Data Generator for CI/CD Dashboard

This module provides functions to generate random pipeline data for testing
and demonstration purposes. It can be used to create realistic CI/CD scenarios.
"""

import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Any

def generate_random_pipeline_name(provider: str) -> str:
    """Generate a realistic pipeline name based on provider"""
    prefixes = {
        'github': ['web-app', 'api-service', 'mobile-app', 'backend', 'frontend', 'docs'],
        'gitlab': ['data-pipeline', 'ml-service', 'analytics', 'etl', 'infrastructure'],
        'jenkins': ['deployment', 'testing', 'security', 'performance', 'docker', 'kubernetes']
    }
    
    suffixes = ['-prod', '-staging', '-dev', '-test', '-main', '-release']
    
    prefix = random.choice(prefixes.get(provider, ['pipeline']))
    suffix = random.choice(suffixes) if random.random() > 0.3 else ''
    
    return f"{prefix}{suffix}"

def generate_random_build_status() -> str:
    """Generate a random build status with realistic distribution"""
    statuses = ["success", "failed", "running", "cancelled", "pending", "skipped"]
    weights = [0.65, 0.20, 0.05, 0.03, 0.05, 0.02]  # Realistic distribution
    
    return random.choices(statuses, weights=weights)[0]

def generate_random_build_duration(pipeline_type: str) -> int:
    """Generate realistic build duration based on pipeline type"""
    if "ml" in pipeline_type or "data" in pipeline_type:
        return random.randint(1800, 7200)  # 30 min - 2 hours
    elif "deployment" in pipeline_type or "kubernetes" in pipeline_type:
        return random.randint(300, 1800)   # 5 min - 30 min
    elif "testing" in pipeline_type or "security" in pipeline_type:
        return random.randint(600, 2400)   # 10 min - 40 min
    elif "docker" in pipeline_type:
        return random.randint(180, 900)    # 3 min - 15 min
    else:
        return random.randint(120, 2700)   # 2 min - 45 min

def generate_random_error_log() -> str:
    """Generate realistic error logs for failed builds"""
    error_templates = [
        "Build failed: Test suite failed with {count} failures",
        "Compilation error: Syntax error in {file} at line {line}",
        "Deployment timeout: Kubernetes deployment stuck in pending state",
        "Security scan failed: {vuln_count} vulnerabilities detected",
        "Performance regression: Response time increased by {percent}%",
        "Dependency issue: Package {package} version {version} not found",
        "Resource limit exceeded: Memory usage {memory}MB exceeds {limit}MB",
        "Network error: Connection timeout to {service} after {timeout}s"
    ]
    
    template = random.choice(error_templates)
    
    # Fill in template variables
    replacements = {
        'count': random.randint(1, 8),
        'file': random.choice(['src/main.js', 'src/app.py', 'src/index.ts', 'src/config.yml']),
        'line': random.randint(1, 100),
        'vuln_count': random.randint(1, 15),
        'percent': random.randint(20, 80),
        'package': random.choice(['lodash', 'axios', 'react', 'express', 'django']),
        'version': f"{random.randint(1, 9)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
        'memory': random.randint(512, 2048),
        'limit': random.randint(1024, 4096),
        'service': random.choice(['database', 'redis', 'elasticsearch', 'api-gateway']),
        'timeout': random.randint(30, 300)
    }
    
    for key, value in replacements.items():
        template = template.replace(f"{{{key}}}", str(value))
    
    return template

def generate_random_pipeline_data(
    count: int = 10,
    days_back: int = 30,
    include_failures: bool = True
) -> List[Dict[str, Any]]:
    """
    Generate random pipeline data for testing
    
    Args:
        count: Number of pipelines to generate
        days_back: How many days back to generate builds
        include_failures: Whether to include failed builds with error logs
    
    Returns:
        List of pipeline data dictionaries
    """
    providers = ['github', 'gitlab', 'jenkins']
    pipelines = []
    
    for i in range(count):
        provider = random.choice(providers)
        pipeline_name = generate_random_pipeline_name(provider)
        
        # Generate builds for this pipeline
        build_count = random.randint(15, 35)
        builds = []
        
        for j in range(build_count):
            # Random time within the specified range
            days_ago = random.uniform(0, days_back)
            started_at = datetime.utcnow() - timedelta(days=days_ago)
            
            status = generate_random_build_status()
            duration = None
            finished_at = None
            logs = None
            
            if status in ["running", "pending"]:
                duration = None
                finished_at = None
            elif status == "skipped":
                duration = 0
                finished_at = started_at
            else:
                duration = generate_random_build_duration(pipeline_name)
                finished_at = started_at + timedelta(seconds=duration)
            
            # Generate error logs for failed builds
            if status == "failed" and include_failures:
                logs = generate_random_error_log()
            
            # Generate external ID based on provider
            if provider == "github":
                external_id = f"gh-{random.randint(1000000, 9999999)}"
            elif provider == "gitlab":
                external_id = f"gl-{random.randint(100000, 999999)}"
            else:  # jenkins
                external_id = f"jk-{random.randint(1000, 99999)}"
            
            builds.append({
                "external_id": external_id,
                "status": status,
                "started_at": started_at,
                "finished_at": finished_at,
                "duration_seconds": duration,
                "web_url": f"https://{provider}.example.com/{pipeline_name}/{external_id}",
                "logs": logs
            })
        
        pipelines.append({
            "provider": provider,
            "name": pipeline_name,
            "external_id": f"{provider}-{i+1}",
            "url": f"https://{provider}.example.com/{pipeline_name}",
            "builds": builds
        })
    
    return pipelines

def generate_random_metrics() -> Dict[str, Any]:
    """Generate random metrics data for testing"""
    total_builds = random.randint(100, 500)
    success_rate = random.uniform(60, 85)
    failure_rate = 100 - success_rate
    
    # Generate some random build times
    build_times = [random.randint(120, 3600) for _ in range(20)]
    avg_build_time = sum(build_times) / len(build_times)
    
    return {
        "success_rate": round(success_rate, 2),
        "failure_rate": round(failure_rate, 2),
        "total_builds": total_builds,
        "avg_build_time_seconds": round(avg_build_time, 2),
        "last_build_status": random.choice(["success", "failed", "running"]),
        "last_build_at": datetime.utcnow() - timedelta(minutes=random.randint(5, 120))
    }

def generate_random_chart_data(days: int = 7) -> Dict[str, List]:
    """Generate random chart data for testing"""
    success_data = []
    failure_data = []
    avg_time_data = []
    
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=i)
        success_count = random.randint(5, 25)
        failure_count = random.randint(1, 8)
        avg_time = random.randint(300, 1800)
        
        success_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "success": success_count,
            "failed": failure_count
        })
        
        avg_time_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "avg": avg_time
        })
    
    return {
        "success_failure": success_data,
        "avg_time": avg_time_data
    }

if __name__ == "__main__":
    # Example usage
    print("Generating sample pipeline data...")
    pipelines = generate_random_pipeline_data(count=5, days_back=14)
    
    print(f"Generated {len(pipelines)} pipelines:")
    for pipeline in pipelines:
        print(f"- {pipeline['provider']}: {pipeline['name']} ({len(pipeline['builds'])} builds)")
    
    print("\nGenerating sample metrics...")
    metrics = generate_random_metrics()
    print(f"Success Rate: {metrics['success_rate']}%")
    print(f"Failure Rate: {metrics['failure_rate']}%")
    print(f"Total Builds: {metrics['total_builds']}")
    print(f"Avg Build Time: {metrics['avg_build_time_seconds']}s")
