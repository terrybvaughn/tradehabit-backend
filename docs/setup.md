# Setup and Deployment Guide

## Development Environment Setup

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