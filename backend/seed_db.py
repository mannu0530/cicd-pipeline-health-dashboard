#!/usr/bin/env python3
"""
Standalone script to seed the database with sample data for the CI/CD Dashboard.
Run this script to populate the database with realistic sample data for demonstration.
"""

import os
import sys
import argparse

# Add the current directory to Python path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sample_data import seed_sample_data, clear_sample_data, reset_sample_data
from db import init_db

def main():
    """Main function to seed the database"""
    parser = argparse.ArgumentParser(description='CI/CD Dashboard Database Management Tool')
    parser.add_argument('--action', choices=['seed', 'clear', 'reset', 'init'], 
                       default='seed', help='Action to perform (default: seed)')
    parser.add_argument('--force', action='store_true', 
                       help='Force action even if data exists')
    
    args = parser.parse_args()
    
    print("CI/CD Dashboard - Database Management Tool")
    print("=" * 50)
    
    try:
        # Initialize database tables and run migrations
        print("Initializing database...")
        init_db()
        print("✅ Database initialized successfully!")
        
        if args.action == 'init':
            print("Database initialization completed.")
            return
        
        if args.action == 'clear':
            print("Clearing sample data...")
            clear_sample_data()
            print("✅ Sample data cleared successfully!")
            return
        
        if args.action == 'reset':
            print("Resetting sample data...")
            reset_sample_data()
            print("✅ Sample data reset completed!")
            return
        
        # Default action: seed
        print("Seeding database with sample data...")
        seed_sample_data()
        
        print("\n✅ Database seeding completed successfully!")
        print("\nYou can now:")
        print("1. Start the backend: python app.py")
        print("2. Start the frontend: npm run dev")
        print("3. View the dashboard at: http://localhost:5173")
        print("4. Check the API docs at: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("- PostgreSQL is running and accessible")
        print("- Environment variables are set correctly")
        print("- Database exists and user has permissions")
        print("- All required Python packages are installed")
        
        # Print more detailed error information for debugging
        import traceback
        print(f"\nDetailed error information:")
        traceback.print_exc()
        
        sys.exit(1)

if __name__ == "__main__":
    main()
