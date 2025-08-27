#!/bin/bash

# CI/CD Dashboard Database Setup Script
# This script automates the database initialization and data seeding process

set -e  # Exit on any error

echo "🚀 CI/CD Dashboard Database Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install it and try again."
    exit 1
fi

print_status "Starting database services..."
docker-compose up -d postgres

print_status "Waiting for PostgreSQL to be ready..."
sleep 10

# Check if PostgreSQL is ready
max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
    if docker-compose exec -T postgres pg_isready -U cicd_user -d cicd_health > /dev/null 2>&1; then
        print_success "PostgreSQL is ready!"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "PostgreSQL failed to start after $max_attempts attempts"
        exit 1
    fi
    
    print_status "Waiting for PostgreSQL... (attempt $attempt/$max_attempts)"
    sleep 2
    attempt=$((attempt + 1))
done

print_status "Setting up database schema and sample data..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if required Python packages are available
cd backend
if ! python3 -c "import psycopg2" 2>/dev/null; then
    print_warning "psycopg2 not found. Installing required packages..."
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
    else
        pip3 install psycopg2-binary sqlalchemy fastapi
    fi
fi

# Run database setup
print_status "Initializing database schema..."
python3 seed_db.py --action init

print_status "Seeding database with sample data..."
python3 seed_db.py --action seed

cd ..

print_success "Database setup completed successfully!"
echo ""
echo "🎉 You can now start the full application:"
echo "   docker-compose up -d"
echo ""
echo "📊 Access the dashboard at: http://localhost:5173"
echo "🔧 API documentation at: http://localhost:8000/docs"
echo ""
echo "🛠️  Useful commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop services: docker-compose down"
echo "   - Reset data: cd backend && python3 seed_db.py --action reset"
echo "   - Clear data: cd backend && python3 seed_db.py --action clear"
echo ""

# Ask if user wants to start the full application
read -p "Would you like to start the full application now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Starting full application..."
    docker-compose up -d
    print_success "Application started! Dashboard available at http://localhost:5173"
else
    print_status "You can start the application later with: docker-compose up -d"
fi

