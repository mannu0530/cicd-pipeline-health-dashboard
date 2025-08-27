#!/usr/bin/env python3
"""
CI/CD Dashboard Database Setup Script
This script automates the database initialization and data seeding process
"""

import os
import sys
import time
import subprocess
import argparse
from pathlib import Path

def print_status(message):
    print(f"[INFO] {message}")

def print_success(message):
    print(f"[SUCCESS] {message}")

def print_warning(message):
    print(f"[WARNING] {message}")

def print_error(message):
    print(f"[ERROR] {message}")

def check_docker():
    """Check if Docker is running and available"""
    try:
        result = subprocess.run(['docker', 'info'], 
                              capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return True
        else:
            print_error("Docker is not running or not accessible")
            return False
    except FileNotFoundError:
        print_error("Docker is not installed")
        return False

def check_docker_compose():
    """Check if docker-compose is available"""
    try:
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return True
        else:
            print_error("docker-compose is not working properly")
            return False
    except FileNotFoundError:
        print_error("docker-compose is not installed")
        return False

def start_postgres():
    """Start PostgreSQL service"""
    print_status("Starting PostgreSQL service...")
    try:
        subprocess.run(['docker-compose', 'up', '-d', 'postgres'], 
                      check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to start PostgreSQL: {e}")
        return False

def wait_for_postgres():
    """Wait for PostgreSQL to be ready"""
    print_status("Waiting for PostgreSQL to be ready...")
    max_attempts = 30
    attempt = 1
    
    while attempt <= max_attempts:
        try:
            result = subprocess.run([
                'docker-compose', 'exec', '-T', 'postgres', 
                'pg_isready', '-U', 'cicd_user', '-d', 'cicd_health'
            ], capture_output=True, check=False)
            
            if result.returncode == 0:
                print_success("PostgreSQL is ready!")
                return True
        except Exception:
            pass
        
        if attempt == max_attempts:
            print_error("PostgreSQL failed to start after maximum attempts")
            return False
        
        print_status(f"Waiting for PostgreSQL... (attempt {attempt}/{max_attempts})")
        time.sleep(2)
        attempt += 1
    
    return False

def setup_database():
    """Setup database schema and seed data"""
    print_status("Setting up database schema and sample data...")
    
    # Change to backend directory
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print_error("Backend directory not found")
        return False
    
    os.chdir(backend_dir)
    
    # Check Python dependencies
    try:
        import psycopg2
    except ImportError:
        print_warning("psycopg2 not found. Installing required packages...")
        if Path("requirements.txt").exists():
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                          check=True)
        else:
            subprocess.run([sys.executable, "-m", "pip", "install", 
                          "psycopg2-binary", "sqlalchemy", "fastapi"], check=True)
    
    # Initialize database
    print_status("Initializing database schema...")
    try:
        subprocess.run([sys.executable, "seed_db.py", "--action", "init"], check=True)
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to initialize database: {e}")
        return False
    
    # Seed sample data
    print_status("Seeding database with sample data...")
    try:
        subprocess.run([sys.executable, "seed_db.py", "--action", "seed"], check=True)
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to seed sample data: {e}")
        return False
    
    # Return to project root
    os.chdir("..")
    return True

def main():
    parser = argparse.ArgumentParser(description='CI/CD Dashboard Database Setup Tool')
    parser.add_argument('--skip-docker', action='store_true', 
                       help='Skip Docker checks and PostgreSQL startup')
    parser.add_argument('--action', choices=['setup', 'init', 'seed', 'reset', 'clear'], 
                       default='setup', help='Action to perform')
    
    args = parser.parse_args()
    
    print("🚀 CI/CD Dashboard Database Setup")
    print("==================================")
    
    # Check if we're in the right directory
    if not Path("docker-compose.yml").exists():
        print_error("Please run this script from the project root directory")
        sys.exit(1)
    
    if not args.skip_docker:
        # Check Docker requirements
        if not check_docker():
            sys.exit(1)
        
        if not check_docker_compose():
            sys.exit(1)
        
        # Start PostgreSQL
        if not start_postgres():
            sys.exit(1)
        
        # Wait for PostgreSQL to be ready
        if not wait_for_postgres():
            sys.exit(1)
    
    # Setup database based on action
    if args.action == 'setup':
        if not setup_database():
            sys.exit(1)
    else:
        # Handle other actions
        backend_dir = Path("backend")
        if not backend_dir.exists():
            print_error("Backend directory not found")
            sys.exit(1)
        
        os.chdir(backend_dir)
        try:
            subprocess.run([sys.executable, "seed_db.py", "--action", args.action], check=True)
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to execute action '{args.action}': {e}")
            sys.exit(1)
        finally:
            os.chdir("..")
    
    print_success("Database setup completed successfully!")
    print()
    print("🎉 You can now start the full application:")
    print("   docker-compose up -d")
    print()
    print("📊 Access the dashboard at: http://localhost:5173")
    print("🔧 API documentation at: http://localhost:8000/docs")
    print()
    print("🛠️  Useful commands:")
    print("   - View logs: docker-compose logs -f")
    print("   - Stop services: docker-compose down")
    print("   - Reset data: python3 setup_database.py --action reset")
    print("   - Clear data: python3 setup_database.py --action clear")
    print()
    
    # Ask if user wants to start the full application
    if not args.skip_docker:
        try:
            response = input("Would you like to start the full application now? (y/n): ").lower()
            if response in ['y', 'yes']:
                print_status("Starting full application...")
                subprocess.run(['docker-compose', 'up', '-d'], check=True)
                print_success("Application started! Dashboard available at http://localhost:5173")
            else:
                print_status("You can start the application later with: docker-compose up -d")
        except KeyboardInterrupt:
            print("\nSetup interrupted by user")
            print_status("You can start the application later with: docker-compose up -d")

if __name__ == "__main__":
    main()

