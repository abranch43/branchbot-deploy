# Development Environment Setup
*BranchBot Deploy - Environment Configuration*

## 🚀 Quick Start

**One-command bootstrap:**
```bash
make bootstrap
```

## 📋 Prerequisites

- **Python 3.12+** (tested with 3.12.3)
- **pip** (package manager)
- **git** (version control)

## 🛠️ Manual Setup Steps

### 1. Clone Repository
```bash
git clone https://github.com/abranch43/branchbot-deploy.git
cd branchbot-deploy
```

### 2. Python Environment
```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# OR .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements_final.txt

# Install development tools
pip install ruff pytest mypy pre-commit
```

### 3. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your actual values:
# STRIPE_WEBHOOK_SECRET=whsec_...
# GUMROAD_WEBHOOK_SECRET=your_secret
# OPENAI_API_KEY=sk-...
# etc.
```

### 4. Development Tools Setup
```bash
# Install pre-commit hooks
pre-commit install

# Verify setup
make test
make lint
```

## 🏃‍♂️ Common Development Commands

| Command | Purpose |
|---------|---------|
| `make bootstrap` | Complete environment setup |
| `make test` | Run full test suite |
| `make lint` | Check code style & formatting |
| `make run` | Start local development server |
| `make format` | Auto-format code |
| `make type-check` | Run mypy type checking |
| `make clean` | Clean temporary files |

## 🔧 VS Code Setup

Install recommended extensions:
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.ruff",
    "ms-python.mypy-type-checker",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

Use Ctrl+Shift+P → "Tasks: Run Task" for:
- Bootstrap environment
- Run tests
- Lint code
- Start development server

## 🐍 Python Dependencies

### Runtime Dependencies
```
fastapi==0.110.0        # Web framework
stripe==7.10.0          # Payment processing
streamlit==1.37.0       # Dashboard framework
requests==2.31.0        # HTTP client
uvicorn==0.30.0         # ASGI server
python-dotenv==1.0.1    # Environment variables
openai==1.37.0          # AI integration
```

### Development Dependencies
```
ruff                    # Linting & formatting
pytest                  # Testing framework
pytest-cov            # Coverage reporting
mypy                   # Type checking
pre-commit             # Git hooks
```

## 🌍 Environment Variables

**Required for Development:**
```bash
# Webhook secrets (get from respective services)
STRIPE_WEBHOOK_SECRET=whsec_...
GUMROAD_WEBHOOK_SECRET=your_shared_secret

# Optional integrations
OPENAI_API_KEY=sk-...
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
NOTION_TOKEN=secret_...
NOTION_DATABASE_ID=...

# Safety switch
SAFE_MODE=true  # Disables external integrations in dev
```

**Railway Deployment Variables:**
```bash
DATABASE_URL=postgresql://...  # Auto-provisioned by Railway
PORT=8000                      # Auto-set by Railway
```

## 🔍 Troubleshooting

### Import Errors
```bash
# Set Python path for local development
export PYTHONPATH=.
# OR add to .env:
echo "PYTHONPATH=." >> .env
```

### Port Conflicts
```bash
# Check what's running on port 8000
lsof -i :8000
# Kill process if needed
kill -9 <PID>
```

### Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_final.txt
```

### Dependencies Not Found
```bash
# Upgrade pip
pip install --upgrade pip

# Clear pip cache
pip cache purge

# Reinstall requirements
pip install -r requirements_final.txt --force-reinstall
```

## 🏗️ Project Structure

```
branchbot-deploy/
├── branchberg/
│   ├── app/main.py          # FastAPI backend
│   └── dashboard/           # Streamlit dashboard
├── tests/                   # Test suite
├── ops/                     # Operations documentation
├── ops_out/                 # Generated reports
├── .env.example             # Environment template
├── Makefile                 # Development commands
├── pyproject.toml           # Python project config
└── requirements_final.txt   # Pinned dependencies
```

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] `python --version` shows 3.12+
- [ ] `make test` passes all tests
- [ ] `make lint` shows no errors
- [ ] `make run` starts the server
- [ ] VS Code shows no import errors
- [ ] Pre-commit hooks are active

---
*Need help? Check the [Operations Playbook](./PLAYBOOK.md) or update this guide!*