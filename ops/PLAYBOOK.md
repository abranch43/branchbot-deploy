# Operations Playbook
*BranchBot Deploy - Daily Operations Guide*

## 🚀 Quick Start Commands

```bash
# Complete environment setup
make bootstrap

# Daily development workflow
make lint          # Check code quality
make test          # Run test suite  
make dev           # Start development server
make dashboard     # Start Streamlit dashboard

# Health and maintenance
make health        # System health check
make clean         # Clean temporary files
make verify        # Run all quality checks
```

## 📋 Daily Operations

### Morning Routine (5 minutes)
```bash
# Pull latest changes
git pull origin main

# Health check
make health

# Run tests to ensure everything works
make test

# Start development environment
make dev
```

### Before Committing Changes
```bash
# Format and lint code
make format
make lint

# Run tests
make test

# Type check (if using type hints)
make type-check

# Verify everything passes
make verify
```

### Deployment Preparation
```bash
# Final verification
make verify

# Check environment variables
cat .env.example  # Ensure all vars documented

# Test with production-like settings
SAFE_MODE=false make test  # Only if you have test credentials
```

## 🔧 Development Server Management

### FastAPI Backend
```bash
# Start API server (auto-reload)
make dev

# Alternative: Direct uvicorn
uvicorn branchberg.app.main:app --reload --host 0.0.0.0 --port 8000

# Check API health
curl http://localhost:8000/health
```

### Streamlit Dashboard
```bash
# Start dashboard
make dashboard

# Alternative: Direct streamlit
streamlit run branchberg/dashboard/streamlit_app.py

# Access dashboard
open http://localhost:8501
```

### Both Services
```bash
# Terminal 1: API
make dev

# Terminal 2: Dashboard  
make dashboard

# Now both services running simultaneously
```

## 🧪 Testing Operations

### Run Different Test Suites
```bash
# All tests
make test

# Specific test file
pytest tests/test_environment.py -v

# Tests with coverage report
pytest tests/ -v --cov=branchberg --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Test Environment Variables
```bash
# Test with safe mode (default)
SAFE_MODE=true make test

# Test with actual APIs (careful!)
SAFE_MODE=false make test  # Only with test credentials
```

## 🔍 Troubleshooting Guide

### Common Issues

**Import Errors:**
```bash
# Fix Python path
export PYTHONPATH=.
# OR
echo "PYTHONPATH=." >> .env
```

**Port Already in Use:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn branchberg.app.main:app --port 8001
```

**Missing Dependencies:**
```bash
# Reinstall everything
pip install -r requirements_final.txt

# Reinstall dev tools
make bootstrap
```

**Tests Failing:**
```bash
# Check environment
make health

# Clear cache and retry
make clean
make test

# Run single test for debugging
pytest tests/test_environment.py::TestEnvironment::test_basic_imports -v
```

### Environment Issues

**Virtual Environment Problems:**
```bash
# Recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# OR .venv\Scripts\activate  # Windows

# Reinstall dependencies
make bootstrap
```

**Environment Variables Not Loading:**
```bash
# Check .env file exists
ls -la .env

# Check format (no spaces around =)
cat .env

# Test loading
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('SAFE_MODE'))"
```

## 🛠️ Maintenance Tasks

### Weekly (10 minutes)
```bash
# Update dependencies (check for security updates)
pip list --outdated

# Clean up temporary files
make clean

# Review logs for any issues
# Check Railway logs if deployed
```

### Monthly (30 minutes)
```bash
# Dependency audit
pip audit  # Install with: pip install pip-audit

# Update development tools
pip install --upgrade ruff pytest mypy pre-commit

# Review and update documentation
# Check SECURITY.md for any needed updates
```

### Quarterly (1 hour)
```bash
# Rotate API keys (see SECURITY.md)
# Update secrets in Railway environment
# Test with new credentials
# Update .env.example if new variables added
```

## 📊 Monitoring & Logs

### Local Development
```bash
# Watch API logs
make dev  # Logs appear in terminal

# Watch test coverage
pytest tests/ --cov=branchberg --cov-report=term-missing
```

### Production (Railway)
```bash
# View Railway logs
railway logs

# Check service status
railway status

# Monitor resource usage
railway stats
```

## 🚨 Emergency Procedures

### Service Down
1. **Check Railway status**: railway status
2. **Review logs**: railway logs 
3. **Check environment variables**: Ensure all required vars set
4. **Restart service**: railway restart
5. **Health check**: curl https://your-domain/health

### Security Incident
1. **Follow SECURITY.md incident response**
2. **Revoke compromised credentials immediately**
3. **Update environment variables**
4. **Deploy with new secrets**
5. **Monitor for suspicious activity**

### Database Issues
1. **Check Railway database status**
2. **Verify DATABASE_URL environment variable**
3. **Test connection**: python -c "import os; print(os.getenv('DATABASE_URL'))"
4. **Contact Railway support if persistent**

## 🎯 Performance Optimization

### API Performance
```bash
# Profile API endpoints
pip install httpx pytest-benchmark

# Load testing (be careful!)
pip install locust
# Create locustfile.py for load testing
```

### Dashboard Performance
```bash
# Streamlit performance profiling
streamlit run branchberg/dashboard/streamlit_app.py --profiler

# Memory usage monitoring
pip install memory-profiler
```

## 📚 Reference Links

- **Railway Docs**: https://docs.railway.app/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Streamlit Docs**: https://docs.streamlit.io/
- **pytest Docs**: https://docs.pytest.org/
- **ruff Docs**: https://docs.astral.sh/ruff/

## 🤖 Automation Shortcuts

**VS Code Tasks** (Ctrl+Shift+P → "Tasks: Run Task"):
- 🚀 Bootstrap Environment
- 🧪 Run Tests  
- 🔍 Lint Code
- 🎨 Format Code
- 🚀 Start Development Server
- 📊 Start Dashboard
- ✅ Verify Setup

**Make Targets** (just type `make <target>`):
- `bootstrap`, `test`, `lint`, `format`, `dev`, `dashboard`, `health`, `clean`, `verify`

---
*"Automate the routine, focus on the creative."*  
Keep this playbook updated as the project evolves!