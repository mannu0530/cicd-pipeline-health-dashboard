# Troubleshooting Guide

## 🚨 Common Issues and Solutions

### Database Schema Issues

#### Error: "column pipelines.is_active does not exist"

**Problem**: The database schema is outdated and missing the `is_active` column that was added in recent updates.

**Solutions**:

1. **Use Automated Setup (Recommended)**:
   ```bash
   python3 setup_database.py
   ```
   This script automatically handles migrations and schema updates.

2. **Manual Migration**:
   ```bash
   # The migration is now handled automatically in init_db()
   cd backend
   python3 seed_db.py --action init
   ```

3. **Reset Database (Fresh Start)**:
   ```bash
   python3 setup_database.py --action reset
   ```

4. **Manual SQL Fix** (if needed):
   ```sql
   ALTER TABLE pipelines ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL;
   ```

### Database Connection Issues

#### Error: "connection refused" or "database does not exist"

**Solutions**:

1. **Check Docker Services**:
   ```bash
   docker-compose ps
   docker-compose logs postgres
   ```

2. **Restart Database Service**:
   ```bash
   docker-compose restart postgres
   ```

3. **Check Environment Variables**:
   Ensure your `.env` file has correct database credentials:
   ```bash
   POSTGRES_USER=cicd_user
   POSTGRES_PASSWORD=supersecret
   POSTGRES_HOST=postgres
   POSTGRES_DB=cicd_health
   ```

### Python Dependencies Issues

#### Error: "ModuleNotFoundError: No module named 'psycopg2'"

**Solutions**:

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Manual Installation**:
   ```bash
   pip install psycopg2-binary sqlalchemy fastapi
   ```

3. **Use Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Docker Issues

#### Error: "Docker daemon not running"

**Solutions**:

1. **Start Docker Desktop** (Windows/macOS)
2. **Start Docker service** (Linux):
   ```bash
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

3. **Check Docker permissions** (Linux):
   ```bash
   sudo usermod -aG docker $USER
   # Log out and back in
   ```

#### Error: "docker-compose command not found"

**Solutions**:

1. **Install Docker Compose**:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install docker-compose
   
   # On macOS with Homebrew
   brew install docker-compose
   ```

2. **Use Docker Compose V2**:
   ```bash
   docker compose up -d  # Note: no hyphen
   ```

### Frontend Issues

#### Error: "Cannot connect to backend API"

**Solutions**:

1. **Check Backend Status**:
   ```bash
   docker-compose ps
   docker-compose logs backend
   ```

2. **Verify API Endpoint**:
   - Backend should be running on http://localhost:8000
   - Check browser console for CORS errors

3. **Check Environment Variables**:
   Ensure `VITE_API_BASE` is set correctly in frontend

### Sample Data Issues

#### Error: "No data available" in charts

**Solutions**:

1. **Check if Sample Data Exists**:
   ```bash
   python3 setup_database.py --action seed
   ```

2. **Reset Sample Data**:
   ```bash
   python3 setup_database.py --action reset
   ```

3. **Verify Database Content**:
   ```bash
   cd backend
   python3 -c "
   from db import get_session, Pipeline, Build
   with next(get_session()) as session:
       print(f'Pipelines: {session.query(Pipeline).count()}')
       print(f'Builds: {session.query(Build).count()}')
   "
   ```

## 🛠️ Diagnostic Commands

### Check System Status
```bash
# Docker services
docker-compose ps

# Service logs
docker-compose logs -f [service_name]

# Database connectivity
docker-compose exec postgres pg_isready -U cicd_user -d cicd_health

# Python environment
python3 --version
pip list | grep -E "(psycopg2|sqlalchemy|fastapi)"
```

### Database Verification
```bash
# Connect to database
docker-compose exec postgres psql -U cicd_user -d cicd_health

# Check tables
\dt

# Check schema
\d pipelines
\d builds

# Check data
SELECT COUNT(*) FROM pipelines;
SELECT COUNT(*) FROM builds;
```

### Backend Health Check
```bash
# Test API endpoint
curl http://localhost:8000/api/metrics/overview

# Check backend logs
docker-compose logs backend | tail -20
```

## 🔄 Reset and Recovery

### Complete Reset
If you need to start completely fresh:

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: This deletes all data)
docker-compose down -v

# Rebuild and restart
docker-compose up -d --build

# Setup database
python3 setup_database.py
```

### Partial Reset
```bash
# Reset only database
python3 setup_database.py --action reset

# Reset only specific service
docker-compose restart [service_name]
```

## 📞 Getting Help

If you're still experiencing issues:

1. **Check the logs**: `docker-compose logs -f`
2. **Verify environment**: Ensure all required variables are set
3. **Check system requirements**: Docker, Python 3.8+, Node.js 18+
4. **Search issues**: Check GitHub Issues for similar problems
5. **Create new issue**: Provide logs, error messages, and system info

## 🚀 Prevention Tips

1. **Always use the automated setup scripts** for initial setup
2. **Keep Docker and dependencies updated**
3. **Use virtual environments** for Python development
4. **Backup important data** before major changes
5. **Check logs regularly** for early warning signs

