
# CI/CD Pipeline Health Dashboard

A comprehensive, real-time dashboard for monitoring CI/CD pipeline health across multiple providers including GitHub Actions, GitLab CI, and Jenkins.

## 🚀 Enhanced Features

### 📊 Advanced Analytics & Visualization
- **Real-time Metrics**: Live updates via WebSocket connections
- **Interactive Charts**: Configurable time-series charts (3, 7, 14, 30 days)
- **Build Trends Analysis**: Success/failure patterns and performance trends
- **Pipeline Performance**: Ranked pipeline metrics with success rates
- **Smart Data Aggregation**: Time-based grouping and statistical analysis

### 🎛️ Enhanced User Experience
- **Modern UI Design**: Clean, professional interface with dark/light themes
- **Responsive Layout**: Mobile-first design that works on all devices
- **Interactive Controls**: Chart toggles, time range selectors, and filters
- **Real-time Updates**: Live data refresh with WebSocket support
- **Enhanced Metrics**: 6 comprehensive metric cards with detailed insights

### 🔧 Technical Improvements
- **FastAPI Backend**: Modern Python web framework with async support
- **Enhanced Database**: Improved schema with active pipeline tracking
- **RESTful APIs**: Comprehensive endpoints for all dashboard data
- **Error Handling**: Robust error handling with graceful fallbacks
- **Performance Optimization**: Efficient data fetching and caching

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
│                 │    │                 │    │                 │
│ • Charts        │    │ • REST APIs     │    │ • Builds        │
│ • Metrics       │    │ • WebSockets    │    │ • Pipelines     │
│ • Real-time UI  │    │ • Collectors    │    │ • Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.8+ (for backend development)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd cicd-pipeline-health-dashboard
```

### 2. Automated Database Setup (Recommended)
```bash
# Option 1: Using the Python script (cross-platform)
python3 setup_database.py

# Option 2: Using the bash script (Linux/macOS)
./setup_database.sh

# Option 3: Manual setup
docker-compose up -d postgres
cd backend
python3 seed_db.py --action init
python3 seed_db.py --action seed
cd ..
```

### 3. Start Full Application
```bash
docker-compose up -d
```

### 4. Access Dashboard
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 5. Development Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
python app.py

# Frontend
cd frontend
npm install
npm run dev
```

## 🔧 Database Management

### Automated Setup Scripts
The project includes automated setup scripts that handle:
- Database initialization and schema creation
- Automatic migration handling (including the `is_active` column fix)
- Sample data seeding
- Docker service management

### Manual Database Operations
```bash
# Initialize database schema only
python3 setup_database.py --action init

# Seed sample data only
python3 setup_database.py --action seed

# Reset all data (clear and reseed)
python3 setup_database.py --action reset

# Clear all data
python3 setup_database.py --action clear

# Skip Docker checks (if running manually)
python3 setup_database.py --skip-docker --action setup
```

### Troubleshooting Database Issues
If you encounter the "column pipelines.is_active does not exist" error:
1. **Use the automated setup scripts** - they handle migrations automatically
2. **Manual fix**: The migration is now handled automatically in `init_db()`
3. **Reset database**: Use `python3 setup_database.py --action reset` to start fresh

## 📊 Dashboard Features

### Metrics Overview
- **Success/Failure Rates**: Real-time build success metrics
- **Build Performance**: Average build times and trends
- **Pipeline Health**: Active pipeline counts and status
- **Recent Activity**: Today's builds and weekly comparisons

### Interactive Charts
- **Success/Failure Distribution**: Stacked bar charts over time
- **Build Duration Trends**: Area charts showing performance
- **Pipeline Rankings**: Horizontal bar charts for comparison
- **Time-Series Analysis**: Configurable date ranges (3-30 days)

### Real-time Monitoring
- **Live Updates**: WebSocket-powered real-time data
- **Build Status**: Current running builds and recent completions
- **Alert System**: Notifications for build failures and issues
- **Log Access**: Direct access to build logs and details

## 🔌 Supported CI/CD Providers

- **GitHub Actions**: Webhook and API integration
- **GitLab CI**: Pipeline monitoring and status tracking
- **Jenkins**: Build job monitoring and metrics
- **Extensible**: Easy to add new providers

## 🛠️ Configuration

### Environment Variables
```bash
# Database
POSTGRES_USER=cicd_user
POSTGRES_PASSWORD=supersecret
POSTGRES_HOST=postgres
POSTGRES_DB=cicd_health

# Providers
PROVIDERS=github,gitlab,jenkins

# Frontend
FRONTEND_ORIGIN=http://localhost:5173
```

### Provider Setup
See individual provider documentation in the `collectors/` directory for detailed setup instructions.

## 📱 Responsive Design

The dashboard is fully responsive and optimized for:
- **Desktop**: Full-featured experience with all charts visible
- **Tablet**: Adaptive layout with optimized chart sizing
- **Mobile**: Touch-friendly interface with mobile-optimized controls

## 🔮 Advanced Features

### Chart Controls
- **Time Range Selection**: 3, 7, 14, or 30 days
- **Chart Toggles**: Show/hide specific chart types
- **Interactive Elements**: Hover tooltips and click actions
- **Real-time Updates**: Automatic data refresh

### Data Analysis
- **Trend Analysis**: Build success patterns over time
- **Performance Metrics**: Pipeline efficiency rankings
- **Statistical Insights**: Success rates and failure analysis
- **Historical Data**: Long-term performance tracking

## 🚀 Deployment

### Production Setup
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with production config
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Configuration
- Configure production database credentials
- Set up SSL certificates for HTTPS
- Configure reverse proxy (nginx/traefik)
- Set up monitoring and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Documentation**: Check the `docs/` directory for detailed guides
- **Community**: Join discussions in GitHub Discussions

---

**Built with ❤️ for the DevOps community**



