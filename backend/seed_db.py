#!/usr/bin/env python3
"""
Standalone script to seed the database with sample data for the CI/CD Dashboard.
Run this script to populate the database with realistic sample data for demonstration.
"""

import os
import sys

# Add the current directory to Python path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sample_data import seed_sample_data
from db import init_db

def main():
    """Main function to seed the database"""
    print("CI/CD Dashboard - Database Seeding Tool")
    print("=" * 50)
    
    try:
        # Initialize database tables
        print("Initializing database...")
        init_db()
        
        # Seed with sample data
        print("Seeding database with sample data...")
        seed_sample_data()
        
        print("\n✅ Database seeding completed successfully!")
        print("\nYou can now:")
        print("1. Start the backend: python app.py")
        print("2. Start the frontend: npm run dev")
        print("3. View the dashboard at: http://localhost:5173")
        print("4. Check the API docs at: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        print("\nMake sure:")
        print("- PostgreSQL is running and accessible")
        print("- Environment variables are set correctly")
        print("- Database exists and user has permissions")
        sys.exit(1)

if __name__ == "__main__":
    main()
