# GoogleAdsAutomation-Backend

# 🤖 Google Ads Automation Backend

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

AI-powered Google Ads campaign optimization system that monitors performance, detects anomalies, and generates optimization recommendations using multi-provider AI (OpenAI, Claude, Gemini).

---

## 🎯 Overview

**AdOptimizer AI** is a comprehensive backend system that automates Google Ads campaign optimization for affiliate marketing. The system continuously monitors campaign metrics, analyzes historical trends, and generates AI-powered optimization recommendations.

### Key Features

- 🔍 **Automated Campaign Monitoring** - Tracks 20+ metrics every 6 hours
- 🤖 **Multi-Provider AI Analysis** - Supports OpenAI, Claude, and Gemini
- 📊 **Historical Trend Analysis** - 14-day performance tracking with weekend/weekday patterns
- ⚡ **Real-time Alerts** - Detects anomalies and performance issues
- 🎯 **Smart Optimization Recommendations** - Budget adjustments, bid changes, keyword management
- 🔄 **Automated Execution** - Direct Google Ads API integration for applying optimizations
- 📈 **REST API** - Complete API for frontend integration

---

## 🛠️ Tech Stack

### Core Framework & Runtime
- **Python 3.12.0** - Latest Python with performance improvements
- **FastAPI 0.104+** - High-performance async web framework
  - Automatic OpenAPI/Swagger documentation
  - Type hints and validation
  - Async/await support
- **Uvicorn** - Lightning-fast ASGI server
- **Pydantic v2** - Data validation using Python type annotations

### Database & ORM
- **PostgreSQL 15+** - Advanced open-source relational database
  - JSONB support for flexible schema
  - Full-text search capabilities
  - Advanced indexing
- **SQLAlchemy 2.x** - Modern Python SQL toolkit and ORM
  - Type-safe queries
  - Connection pooling
  - Migration support
- **psycopg2-binary** - PostgreSQL adapter for Python
- **Alembic** - Database migration tool (optional)

### Google Ads Integration
- **google-ads-api v24.1.0** - Official Google Ads API Python client
  - Direct campaign management
  - Real-time metrics fetching
  - Automated bid/budget adjustments
- **OAuth 2.0** - Secure authentication flow
- **GAQL (Google Ads Query Language)** - SQL-like query language for Google Ads
- **google-auth** - Google authentication library
- **google-auth-oauthlib** - OAuth 2.0 helpers

### AI & Machine Learning
- **OpenAI API (GPT-4 Turbo)** 
  - Model: `gpt-4-turbo-preview`
  - 128K context window
  - Advanced reasoning capabilities
- **Anthropic Claude API**
  - Model: `claude-3-5-sonnet-20241022`
  - 200K context window
  - Best for complex analysis
- **Google Gemini API**
  - Model: `gemini-1.5-flash`
  - Free tier available
  - Fast inference
- **google-generativeai** - Gemini Python SDK

### Background Processing
- **APScheduler 4.x** - Advanced Python scheduler
  - Interval-based scheduling
  - Cron-like scheduling
  - Job persistence
  - Timezone support
- **asyncio** - Async I/O framework for concurrent operations

### API & Networking
- **httpx** - Modern HTTP client with async support
- **requests** - HTTP library for synchronous requests
- **aiohttp** - Async HTTP client/server framework
- **urllib3** - HTTP client library

### Data Processing & Analysis
- **numpy** - Numerical computing library
  - Statistical calculations
  - Array operations
  - Performance optimization
- **pandas** (optional) - Data manipulation and analysis
- **datetime** - Date and time handling
- **pytz** - Timezone calculations

### Logging & Monitoring
- **loguru** - Simplified logging with colors
  - Structured logging
  - Automatic rotation
  - Exception catching
- **python-json-logger** - JSON formatted logs
- **sentry-sdk** (optional) - Error tracking

### Configuration & Environment
- **python-dotenv** - Environment variable management from .env files
- **pydantic-settings** - Settings management with Pydantic
- **configparser** - Configuration file parser

### Security
- **cryptography** - Cryptographic recipes and primitives
- **python-jose** - JWT token handling
- **passlib** - Password hashing utilities
- **bcrypt** - Modern password hashing

### Development & Testing
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Code coverage reporting
- **black** - Code formatter
- **flake8** - Code linter
- **mypy** - Static type checker
- **pre-commit** - Git hook scripts

### Deployment & DevOps
- **Docker** - Containerization
- **docker-compose** - Multi-container orchestration
- **gunicorn** - WSGI HTTP server for production
- **supervisor** - Process control system
- **systemd** - System and service manager (Linux)

### Cloud & Infrastructure (Supported)
- **Supabase** - PostgreSQL cloud hosting
- **Render.com** - Application hosting
- **Railway.app** - Platform-as-a-Service
- **Fly.io** - Application hosting
- **Google Cloud Run** - Serverless container platform
- **DigitalOcean** - VPS hosting

### Monitoring & Analytics (Optional)
- **Prometheus** - Metrics collection
- **Grafana** - Metrics visualization
- **Sentry** - Error tracking
- **New Relic** - Application performance monitoring

---

## 📦 Complete Dependencies

### Core Requirements (requirements.txt)

```txt
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1

# Google Ads API
google-ads==24.1.0
google-auth==2.25.2
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0

# AI Providers
openai==1.6.1
anthropic==0.8.1
google-generativeai==0.3.2

# Background Processing
apscheduler==4.0.0a4

# HTTP & Networking
httpx==0.25.2
requests==2.31.0
aiohttp==3.9.1

# Data Processing
numpy==1.26.2
pandas==2.1.4
python-dateutil==2.8.2
pytz==2023.3

# Logging
loguru==0.7.2
python-json-logger==2.0.7

# Configuration
python-dotenv==1.0.0

# Security
cryptography==41.0.7
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

### Development Requirements (requirements-dev.txt)

```txt
# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0

# Code Quality
black==23.12.1
flake8==6.1.0
mypy==1.7.1
pylint==3.0.3
isort==5.13.2

# Pre-commit hooks
pre-commit==3.6.0
```

### Production Requirements (requirements-prod.txt)

```txt
# Production Server
gunicorn==21.2.0

# Monitoring
sentry-sdk[fastapi]==1.39.1
prometheus-client==0.19.0

# Performance
redis==5.0.1
celery==5.3.4
```

### Installation Commands

```bash
# Development setup
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Production setup
pip install -r requirements.txt
pip install -r requirements-prod.txt

# All at once
pip install -r requirements.txt -r requirements-dev.txt -r requirements-prod.txt
```

---

## 📁 Project Structure

```
backend/
├── agents/                      # AI Agents
│   ├── analyzer.py             # Campaign analysis with AI (multi-provider)
│   ├── executor.py             # Action execution via Google Ads API
│   └── monitor.py              # Metrics monitoring and alert generation
│
├── api/                         # FastAPI Application
│   ├── main.py                 # API entry point
│   └── routes/
│       ├── campaigns.py        # Campaign endpoints
│       ├── stats.py            # Statistics endpoints
│       ├── optimizations.py    # Optimization endpoints
│       ├── actions.py          # Action execution endpoints
│       └── alerts.py           # Alert management endpoints
│
├── database/                    # Database Layer
│   ├── database.py             # Database connection and session management
│   ├── models.py               # SQLAlchemy models
│   └── schema.sql              # Database schema
│
├── config/                      # Configuration
│   └── settings.py             # Application settings (Pydantic)
│
├── utils/                       # Utilities
│   └── logger.py               # Logging configuration
│
├── scheduler.py                 # Background scheduler (APScheduler)
├── requirements.txt             # Python dependencies
├── .env.example                # Environment variables template
└── README.md                   # This file
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Google Ads API credentials
- AI Provider API key (OpenAI, Claude, or Gemini)

### 1. Clone Repository

```bash
git clone https://github.com/YOUR-USERNAME/GoogleAdsAutomation-Backend.git
cd GoogleAdsAutomation-Backend
```

### 2. Create Virtual Environment

```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
nano .env
```

Required variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/google_ads_automation

# Google Ads API
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_CUSTOMER_ID=1234567890
GOOGLE_ADS_LOGIN_CUSTOMER_ID=9876543210

# AI Provider (choose one)
AI_PROVIDER=openai  # or 'claude' or 'gemini'

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Google Gemini (FREE)
GEMINI_API_KEY=AI...
GEMINI_MODEL=gemini-1.5-flash

# Targets
TARGET_ROAS_MIN=1.5
TARGET_CTR_MIN=1.5
TARGET_CPC_MAX=0.70
```

### 5. Setup Database

```bash
# Create database
createdb google_ads_automation

# Run migrations
psql google_ads_automation < database/schema.sql
```

### 6. Generate Google Ads Refresh Token

```bash
python generate_refresh_token.py
```

Follow the OAuth flow in your browser and save the refresh token to `.env`.

### 7. Start the Application

**Development Mode:**
```bash
# Start API server
uvicorn api.main:app --reload --port 8000

# Start scheduler (in another terminal)
python scheduler.py
```

**Production Mode:**
```bash
# Start both with process manager
pm2 start ecosystem.config.js
```

---

## 📡 API Endpoints

### Campaigns
- `GET /api/campaigns` - Get all campaigns with optional filters
- `GET /api/campaigns/available-fields` - Get available metric fields

### Statistics
- `GET /api/stats/dashboard` - Get dashboard statistics with period comparison

### Optimizations
- `GET /api/optimizations` - List all optimization recommendations
- `GET /api/optimizations/count` - Count optimizations by status
- `POST /api/optimizations/{id}/apply` - Apply an optimization
- `POST /api/optimizations/{id}/dismiss` - Dismiss an optimization
- `GET /api/optimizations/{id}` - Get optimization details

### Actions
- `GET /api/actions/pending` - Get pending actions
- `POST /api/actions/{id}/approve` - Approve an action
- `POST /api/actions/execute` - Execute approved actions

### Alerts
- `GET /api/alerts/active` - Get active alerts
- `POST /api/alerts/{id}/resolve` - Resolve an alert

### Health
- `GET /api/health` - Health check
- `GET /api/health/summary` - System summary

**API Documentation:** `http://localhost:8000/docs`

---

## 🤖 AI Agents

### 1. Monitor Agent (`agents/monitor.py`)

**Purpose:** Continuous campaign monitoring and alert generation

**Features:**
- Fetches campaign metrics from Google Ads API
- Calculates 20+ performance indicators
- Stores historical data in PostgreSQL
- Generates alerts for anomalies (low ROAS, high CPC, etc.)
- Runs every 6 hours via scheduler

**Metrics Tracked:**
- Cost, Conversions, ROAS, CTR, CPC
- Impressions, Clicks, Conversion Value
- Budget, Status, Optimization Score
- Quality Score, Bid Strategy

### 2. Analyzer Agent (`agents/analyzer.py`)

**Purpose:** AI-powered campaign analysis and recommendation generation

**Features:**
- Multi-provider AI support (OpenAI, Claude, Gemini)
- Analyzes 14-day historical trends
- Weekend vs weekday pattern detection
- Temporal context awareness (day of week, time)
- Generates 3-7 actionable recommendations per campaign

**AI Prompt Engineering:**
- Provides complete historical context (not just current snapshot)
- Includes statistical analysis (averages, trends, best/worst periods)
- Considers seasonal patterns and anomalies
- Specifies exact action formats (budget changes, bid adjustments, etc.)

**Action Types:**
- `INCREASE_BUDGET` / `DECREASE_BUDGET` - Budget adjustments
- `INCREASE_BID` / `REDUCE_BID` - Bid modifications
- `PAUSE_KEYWORD` / `PAUSE_AD` - Pause underperforming elements
- `ADD_NEGATIVE_KEYWORD` - Negative keyword additions

### 3. Executor Agent (`agents/executor.py`)

**Purpose:** Execute approved optimizations via Google Ads API

**Features:**
- Direct Google Ads API integration
- Campaign budget modifications
- Bid adjustments
- Status changes (pause/enable)
- Comprehensive error handling and logging
- Action result tracking in database

---

## 📅 Background Scheduler

The `scheduler.py` runs background tasks using APScheduler:

```python
# Runs every 6 hours
- Monitor campaigns (fetch metrics, generate alerts)
- Analyze campaigns (AI-powered recommendations)

# Configurable intervals
schedule.every(6).hours.do(run_monitor)
schedule.every(6).hours.do(run_analyzer)
```

---

## 🗄️ Database Schema

### Core Tables

**campaign_metrics**
- Historical performance data
- 20+ metric columns
- Indexed by campaign_id and timestamp

**alerts**
- Active and resolved alerts
- Severity levels (LOW, MEDIUM, HIGH, CRITICAL)
- Alert types (LOW_ROAS, HIGH_CPC, etc.)

**proposed_actions**
- AI-generated optimization recommendations
- Status tracking (PENDING, APPLIED, DISMISSED, FAILED)
- Priority levels (HIGH, MEDIUM, LOW)
- Current/proposed values for comparison

**action_logs**
- Execution history
- API responses
- Success/failure tracking

---

## 🔒 Security Best Practices

- ✅ Environment variables for all secrets
- ✅ OAuth 2.0 for Google Ads API
- ✅ Refresh token rotation
- ✅ API key validation
- ✅ Database connection pooling
- ✅ SQL injection prevention (SQLAlchemy ORM)

---

## 🌐 Deployment

### Option 1: Render.com (Free)

```bash
# 1. Prepare deployment
bash setup_render_deploy.sh

# 2. Push to GitHub
git push origin main

# 3. Deploy on Render.com
# - Go to render.com
# - New Web Service
# - Connect GitHub repository
# - Auto-detect and deploy
```

### Option 2: Docker

```bash
# Build image
docker build -t ads-optimizer-backend .

# Run container
docker run -p 8000:8000 --env-file .env ads-optimizer-backend
```

### Option 3: VPS (DigitalOcean, Hetzner)

```bash
# Install dependencies
apt update && apt install python3.12 postgresql-client

# Clone and setup
git clone https://github.com/YOUR-USERNAME/GoogleAdsAutomation-Backend.git
cd GoogleAdsAutomation-Backend
pip install -r requirements.txt

# Setup systemd service
sudo systemctl enable ads-optimizer
sudo systemctl start ads-optimizer
```

---

## 📊 Monitoring & Logs

### Application Logs

```bash
# View logs
tail -f app.log

# Error logs
tail -f errors.log
```

### Database Queries

```sql
-- Recent optimizations
SELECT * FROM proposed_actions 
WHERE status = 'PENDING' 
ORDER BY created_at DESC 
LIMIT 10;

-- Campaign health
SELECT campaign_name, roas, ctr, status 
FROM campaign_metrics 
WHERE timestamp > NOW() - INTERVAL '24 hours';

-- Active alerts
SELECT * FROM alerts 
WHERE resolved = false 
ORDER BY severity DESC;
```

---

## 🧪 Testing

```bash
# Run tests
pytest

# Test specific module
pytest tests/test_analyzer.py

# Coverage report
pytest --cov=agents --cov-report=html
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Moussa**
- Affiliate Marketing Expert
- AI/ML Engineer
- Full-stack Developer

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Google Ads API](https://developers.google.com/google-ads/api) - Campaign management
- [OpenAI](https://openai.com/) - GPT-4 AI analysis
- [Anthropic](https://anthropic.com/) - Claude AI
- [Google Gemini](https://deepmind.google/technologies/gemini/) - Free AI tier

---

## 📞 Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

## 🗺️ Roadmap

- [ ] Machine Learning models for predictive optimization
- [ ] Multi-account management
- [ ] A/B testing automation
- [ ] Custom reporting dashboard
- [ ] Webhook integrations
- [ ] Multi-language support
- [ ] White-label SaaS version

---

## 💰 Commercial Use

This backend is designed to power a commercial SaaS product:

**Target Markets:**
- Affiliate marketers managing multiple campaigns
- Digital agencies optimizing client accounts
- E-commerce businesses running Google Ads
- Performance marketing teams

**Pricing Model (Future):**
- Free tier: 1 account, 10 campaigns
- Pro: €49/month - 5 accounts, unlimited campaigns
- Agency: €149/month - 20 accounts, white-label
- Enterprise: Custom pricing

---

**⭐ Star this repo if you find it useful!**

Built with ❤️ by Moussa
