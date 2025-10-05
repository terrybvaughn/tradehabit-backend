# Setup and Deployment Guide

## Overview

This guide covers setup for both TradeHabit systems:
1. **Core Analytics Backend** - Main Flask API (below)
2. **TradeHabit Mentor** - AI coaching system (see [Mentor Setup](#tradehabit-mentor-setup))

---

## Core Analytics Backend Setup

### Development Environment Setup

### **Prerequisites**
- **Python 3.10+**: Required for modern type hints and dataclass features
- **pip**: Python package manager
- **Virtual Environment**: Recommended for dependency isolation
- **Git**: Version control (optional but recommended)

### **Local Development Setup**

#### **1. Clone the Repository**
```bash
git clone https://github.com/terrybvaughn/tradehabit-backend.git
cd tradehabit-backend
```

#### **2. Create Virtual Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### **3. Install Dependencies**
```bash
# Install production dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

#### **4. Environment Configuration**
```bash
# Create environment file (optional)
echo "FLASK_DEBUG=1" > .env
echo "FLASK_RUN_HOST=127.0.0.1" >> .env
echo "FLASK_RUN_PORT=5000" >> .env
```

#### **5. Start Development Server**
```bash
# Method 1: Direct execution
python app.py

# Method 2: Flask CLI
flask run

# Method 3: With custom settings
FLASK_DEBUG=1 python app.py
```

#### **6. Verify Installation**
```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Expected response:
# {"Status": "Nuh worry yuhself, mi bredda. Everyting crisp."}
```

### **Development Configuration**

#### **Flask Configuration**
```python
# Development settings (app.py)
if __name__ == "__main__":
    host = os.environ.get("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_RUN_PORT", os.environ.get("PORT", 5000)))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    
    app.run(host=host, port=port, debug=debug)
```

#### **CORS Configuration**
```python
# Development CORS settings
ALLOWED_ORIGINS = [
    "http://127.0.0.1:5173",    # Vite dev server
    "http://localhost:5173",    # Alternative localhost
    # Add your frontend development URL here
]
```

## Testing Setup

### **Install Testing Dependencies**
```bash
# Install testing packages
pip install pytest pytest-cov pytest-flask pytest-mock

# Or create requirements-dev.txt
cat > requirements-dev.txt << EOF
pytest>=7.0
pytest-cov>=4.0
pytest-flask>=1.2
pytest-mock>=3.10
black>=23.0
mypy>=1.0
EOF

pip install -r requirements-dev.txt
```

### **Run Tests**
```bash
# Run existing tests
python -m parsing data/test_data.csv --verbose

# Run pytest (when implemented)
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

## Production Deployment

### **Deployment Platforms**

#### **1. Replit Deployment (Current)**
```bash
# Replit configuration
# File: .replit
run = "python app.py"

[env]
FLASK_RUN_HOST = "0.0.0.0"
FLASK_RUN_PORT = "5000"

[nix]
channel = "stable-22_11"

[deployment]
run = ["python", "app.py"]
```

#### **2. Heroku Deployment**
```bash
# Install Heroku CLI
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Create runtime.txt
echo "python-3.11.0" > runtime.txt

# Deploy to Heroku
heroku create your-app-name
git push heroku main
```

#### **3. Railway Deployment**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy to Railway
railway login
railway init
railway up
```

#### **4. Docker Deployment**
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

```bash
# Build and run Docker container
docker build -t tradehabit-backend .
docker run -p 5000:5000 tradehabit-backend
```

### **Production Configuration**

#### **Environment Variables**
```bash
# Production environment variables
export FLASK_DEBUG=0
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=5000
export GUNICORN_WORKERS=4
export GUNICORN_TIMEOUT=30
```

#### **Gunicorn Configuration**
```python
# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
```

#### **Production Deployment Script**
```bash
#!/bin/bash
# deploy.sh

set -e

echo "Starting deployment..."

# Install dependencies
pip install --no-cache-dir -r requirements.txt

# Run basic health check
python -c "from app import app; app.test_client().get('/api/health')"

# Start application with Gunicorn
exec gunicorn --config gunicorn.conf.py app:app
```

## Cloud Platform Setup

### **AWS Deployment**

#### **1. AWS Elastic Beanstalk**
```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init tradehabit-backend

# Create environment
eb create production

# Deploy
eb deploy
```

#### **2. AWS Lambda (Serverless)**
```python
# serverless.py
import json
from app import app

def lambda_handler(event, context):
    # Convert API Gateway event to WSGI environ
    # This requires additional setup with framework like Zappa
    pass
```

### **Google Cloud Platform**

#### **1. Google App Engine**
```yaml
# app.yaml
runtime: python311

env_variables:
  FLASK_DEBUG: "0"
  
automatic_scaling:
  min_instances: 1
  max_instances: 10
```

```bash
# Deploy to GAE
gcloud app deploy
```

### **Azure Deployment**

#### **1. Azure App Service**
```bash
# Install Azure CLI
az login

# Create resource group
az group create --name tradehabit-rg --location eastus

# Create app service
az webapp create --resource-group tradehabit-rg --plan tradehabit-plan --name tradehabit-backend --runtime "PYTHON|3.11"

# Deploy
az webapp deployment source config --name tradehabit-backend --resource-group tradehabit-rg --repo-url https://github.com/yourusername/tradehabit-backend --branch main
```

## Database Setup (Future Enhancement)

### **PostgreSQL Setup**
```bash
# Install PostgreSQL
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Create database
sudo -u postgres createdb tradehabit

# Create user
sudo -u postgres createuser --interactive tradehabit_user
```

### **Database Configuration**
```python
# config.py (future enhancement)
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://tradehabit_user:password@localhost/tradehabit'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

## Frontend Integration

### **Frontend Setup**
```bash
# Clone frontend repository
git clone https://github.com/terrybvaughn/tradehabit-frontend.git

# Install dependencies
cd tradehabit-frontend
npm install

# Configure backend URL
echo "VITE_API_URL=http://localhost:5000" > .env.local

# Start development server
npm run dev
```

### **Production Frontend Integration**
```javascript
// Frontend configuration
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-backend-url.com'
  : 'http://localhost:5000';
```

## Monitoring and Logging

### **Basic Logging Setup**
```python
# logging_config.py
import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
```

### **Health Check Endpoint**
```python
# Enhanced health check
@app.route('/api/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'environment': os.environ.get('ENVIRONMENT', 'development')
    }
```

## Security Configuration

### **Production Security Settings**
```python
# security.py
from flask_talisman import Talisman

def configure_security(app):
    # HTTPS enforcement
    Talisman(app, force_https=True)
    
    # Security headers
    @app.after_request
    def after_request(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
```

### **Environment-Specific CORS**
```python
# Production CORS configuration
def configure_cors(app):
    if app.config['ENV'] == 'production':
        CORS(app, origins=['https://app.tradehab.it'])
    else:
        CORS(app, origins=['http://localhost:5173', 'http://127.0.0.1:5173'])
```

## Troubleshooting

### **Common Issues**

#### **1. Port Already in Use**
```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Use different port
FLASK_RUN_PORT=5001 python app.py
```

#### **2. Module Import Errors**
```bash
# Verify Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

#### **3. CORS Issues**
```python
# Add your frontend URL to ALLOWED_ORIGINS
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://localhost:5173",  # Vite dev server
    "https://your-frontend-url.com"
]
```

#### **4. Memory Issues**
```bash
# Check memory usage
free -h

# Increase swap space (Linux)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### **Debug Mode**
```bash
# Enable debug mode
export FLASK_DEBUG=1
python app.py

# Or inline
FLASK_DEBUG=1 python app.py
```

### **Performance Debugging**
```python
# Add timing middleware
import time

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    print(f"Request took {duration:.2f} seconds")
    return response
```

## Maintenance and Updates

### **Dependency Updates**
```bash
# Check outdated packages
pip list --outdated

# Update specific package
pip install --upgrade flask

# Update all packages
pip install --upgrade -r requirements.txt
```

### **Backup and Recovery**
```bash
# Backup application
tar -czf tradehabit-backup-$(date +%Y%m%d).tar.gz .

# Database backup (future)
pg_dump tradehabit > backup.sql
```

### **Version Management**
```bash
# Tag releases
git tag v1.0.0
git push origin v1.0.0

# Semantic versioning
# MAJOR.MINOR.PATCH
# 1.0.0 -> 1.0.1 (patch)
# 1.0.1 -> 1.1.0 (minor)
# 1.1.0 -> 2.0.0 (major)
```

---

## TradeHabit Mentor Setup

**Status**: Development prototype - separate from main backend

### Prerequisites

- **Node.js 20+**: Required for Next.js frontend
- **Python 3.9+**: Required for tool runner
- **OpenAI API Key**: Required for AI functionality
- **npm**: Node package manager

### Local Development Setup

#### **1. Tool Runner (Backend) Setup**

```bash
# Navigate to tool runner directory
cd mentor/tool_runner

# Install Flask and Flask-CORS (if not already installed)
pip install flask flask-cors

# Start tool runner
python tool_runner.py

# Should start on http://localhost:5000
```

**Verify Tool Runner**:
```bash
# Test health endpoint
curl http://localhost:5000/health

# Expected response:
# {"status": "OK"}

# Test endpoint listing
curl http://localhost:5000/list_endpoints

# Should return available fixture keys
```

#### **2. Chat UI (Frontend) Setup**

```bash
# Navigate to chat UI directory
cd mentor/chat-ui

# Install dependencies
npm install

# Create environment file
cat > .env.local << EOF
OPENAI_API_KEY=sk-...your-key-here...
ASSISTANT_ID=asst_...your-assistant-id...
TOOL_RUNNER_BASE_URL=http://localhost:5000
EOF

# Start development server
npm run dev

# Should start on http://localhost:3000
```

**Verify Chat UI**:
- Open browser to http://localhost:3000
- Should see "Mentor Tester" interface
- Try asking: "What is TradeHabit?"

#### **3. JSON Fixtures Setup**

```bash
# Ensure fixtures exist in tool_runner/static/
cd mentor/tool_runner/static

# Required fixtures (9 files):
ls -la *.json

# Should show:
# - summary.json
# - trades.json
# - losses.json
# - insights.json
# - revenge.json
# - excessive-risk.json
# - risk-sizing.json
# - stop-loss.json
# - winrate-payoff.json
```

### OpenAI Assistant Configuration

#### **1. Create OpenAI Assistant**

```bash
# Using OpenAI CLI or Dashboard
# 1. Go to https://platform.openai.com/assistants
# 2. Create new Assistant
# 3. Set model to GPT-4 (or gpt-4-1106-preview)
# 4. Add system instructions (from mentor/prompts/assistant/system_instructions/)
# 5. Add function tools (4 functions from mentor/prompts/assistant/functions/)
```

#### **2. Function Tool Configuration**

Add these 4 function tools to your assistant:

1. **get_summary_data** (from `mentor/prompts/assistant/functions/get_summary_data.json`)
2. **get_endpoint_data** (from `mentor/prompts/assistant/functions/get_endpoint_data.json`)
3. **filter_trades** (from `mentor/prompts/assistant/functions/filter_trades.json`)
4. **filter_losses** (from `mentor/prompts/assistant/functions/filter_losses.json`)

Copy the JSON schema from each file into the OpenAI Assistant function configuration.

#### **3. Get Assistant ID**

```bash
# From OpenAI Dashboard
# Copy the Assistant ID (starts with "asst_")
# Add to .env.local file
```

### Environment Configuration

#### **Chat UI Environment Variables**

```bash
# .env.local (in mentor/chat-ui/)
OPENAI_API_KEY=sk-...                  # OpenAI API key
ASSISTANT_ID=asst_...                  # OpenAI Assistant ID
TOOL_RUNNER_BASE_URL=http://localhost:5000  # Tool runner URL
```

#### **Tool Runner Configuration**

```python
# mentor/tool_runner/tool_runner.py
# CORS configuration (development)
CORS(app, resources={r"/*": {"origins": "*"}})

# For production, restrict origins:
CORS(app, resources={r"/*": {"origins": ["https://your-chat-ui-url.com"]}})
```

### Testing the Setup

#### **Complete Flow Test**

```bash
# Terminal 1: Start tool runner
cd mentor/tool_runner
python tool_runner.py

# Terminal 2: Start chat UI
cd mentor/chat-ui
npm run dev

# Browser: http://localhost:3000
# Test questions:
# - "What is my win rate?"
# - "How many trades do I have?"
# - "Explain how you detect revenge trading"
```

#### **Tool Runner Tests**

```bash
# Test summary endpoint
curl -X POST http://localhost:5000/get_summary_data

# Test endpoint data
curl -X POST http://localhost:5000/get_endpoint_data \
  -H "Content-Type: application/json" \
  -d '{"name": "insights", "keys_only": true}'

# Test trade filtering
curl -X POST http://localhost:5000/filter_trades \
  -H "Content-Type: application/json" \
  -d '{"max_results": 5, "include_total": true}'
```

### Production Deployment Considerations

⚠️ **WARNING**: Mentor is a development prototype. Do not deploy to production without addressing security concerns (see `docs/security-considerations.md`).

#### **Pre-Production Checklist**

- [ ] Implement authentication for Chat UI
- [ ] Implement authentication for Tool Runner
- [ ] Restrict Tool Runner CORS to specific origins
- [ ] Move OpenAI API key to secure secret management
- [ ] Implement rate limiting and cost controls
- [ ] Replace JSON fixtures with live database queries
- [ ] Implement per-user data isolation
- [ ] Add audit logging for AI interactions
- [ ] Set up monitoring and alerting
- [ ] Test prompt injection safeguards

#### **Deployment Architecture Options**

##### **Option 1: Separate Services (Current)**
```
Chat UI → Vercel/Netlify (Next.js)
Tool Runner → Heroku/Railway (Flask)
OpenAI API → Third-party
```

##### **Option 2: Unified Backend (Future)**
```
Frontend → Main Backend → Mentor Service → OpenAI API
                       → Database
```

### Troubleshooting Mentor Setup

#### **Common Issues**

##### **1. OpenAI API Errors**
```bash
# Error: Invalid API key
# Solution: Verify OPENAI_API_KEY in .env.local

# Error: Assistant not found
# Solution: Verify ASSISTANT_ID matches your OpenAI assistant

# Error: Rate limit exceeded
# Solution: Check your OpenAI account usage limits
```

##### **2. Tool Runner Connection Issues**
```bash
# Error: Tool runner not responding
# Solution: Ensure tool runner is running on port 5000

# Error: CORS policy blocked
# Solution: Check CORS configuration in tool_runner.py

# Test connection:
curl http://localhost:5000/health
```

##### **3. Chat UI Build Issues**
```bash
# Error: Module not found
# Solution: Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Error: Port 3000 already in use
# Solution: Kill process or use different port
lsof -i :3000
kill -9 <PID>
# Or:
npm run dev -- -p 3001
```

##### **4. Missing Fixtures**
```bash
# Error: fixture not found
# Solution: Ensure all 9 JSON files exist in mentor/tool_runner/static/

# List fixtures:
ls -la mentor/tool_runner/static/*.json

# Verify fixture format:
cat mentor/tool_runner/static/summary.json | jq
```

##### **5. Function Tool Errors**
```bash
# Error: Unknown function
# Solution: Verify all 4 function tools are added to OpenAI Assistant

# Check function schemas match:
cat mentor/prompts/assistant/functions/get_summary_data.json
# Compare to OpenAI Dashboard function configuration
```

### Development Workflow

#### **Typical Development Session**

```bash
# 1. Start tool runner
cd mentor/tool_runner && python tool_runner.py

# 2. In new terminal, start chat UI
cd mentor/chat-ui && npm run dev

# 3. Make changes to:
# - Chat UI: mentor/chat-ui/src/ (auto-reloads)
# - Tool Runner: mentor/tool_runner/ (restart required)
# - Prompts: mentor/prompts/ (reload assistant)

# 4. Test changes in browser (http://localhost:3000)
```

#### **Updating Fixtures**

```bash
# Update test data
cd mentor/tool_runner/static

# Edit fixture
nano trades.json

# Refresh tool runner cache
curl -X POST http://localhost:5000/refresh_cache

# Or restart tool runner
```

#### **Updating Prompts**

```bash
# Edit prompt files
cd mentor/prompts

# Edit system instructions
nano assistant/system_instructions/system_instructions.md

# Update assistant in OpenAI Dashboard
# - Copy new content
# - Paste into assistant configuration
# - Save

# Test changes in chat UI
```

### Performance Tuning

#### **Tool Runner Performance**

```python
# Increase cache size (in tool_runner.py)
# Current: In-memory cache with no size limit

# Add cache size limit:
from cachetools import LRUCache
CACHE = LRUCache(maxsize=100)  # Limit cache to 100 entries
```

#### **Chat UI Performance**

```typescript
// Add request debouncing
import { debounce } from 'lodash';

const debouncedSend = debounce(send, 300);
```

#### **OpenAI API Optimization**

```typescript
// Reduce token usage
// - Use field projection in filter_trades
// - Set max_results appropriately
// - Use keys_only when full data not needed

const filters = {
  max_results: 10,  // Don't over-fetch
  fields: ['id', 'entryTime', 'pnl'],  // Project only needed fields
  include_total: false  // Skip total count if not needed
};
```

### Monitoring and Debugging

#### **Tool Runner Logging**

```python
# Add logging to tool_runner.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.before_request
def log_request():
    logger.info(f"{request.method} {request.path}")
```

#### **Chat UI Debugging**

```typescript
// Enable verbose logging in runAssistant.ts
console.log('Calling tool runner:', toolCall);
console.log('Tool response:', result);
```

#### **OpenAI Assistant Debugging**

```typescript
// Log OpenAI run details
console.log('Run status:', run.status);
console.log('Tool calls:', run.required_action?.submit_tool_outputs?.tool_calls);
console.log('Usage:', run.usage);
```

---

## Performance Optimization

### **Production Optimizations**
```python
# Disable debug mode
app.config['DEBUG'] = False

# Enable gzip compression
from flask_compress import Compress
Compress(app)

# Add caching headers
@app.after_request
def after_request(response):
    response.headers['Cache-Control'] = 'public, max-age=300'
    return response
```

### **Database Connection Pooling (Future)**
```python
# SQLAlchemy configuration
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

This comprehensive setup guide provides everything needed to deploy and maintain the TradeHabit backend application across different environments and platforms.