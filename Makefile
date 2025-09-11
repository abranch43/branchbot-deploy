# BranchBot Deploy - Development Makefile
# Cross-platform development automation

.PHONY: help bootstrap install test lint format type-check run clean dev health

# Default target
help:
	@echo "🤖 BranchBot Deploy - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  bootstrap     Complete development environment setup"
	@echo "  install       Install dependencies only"
	@echo ""
	@echo "Development:"
	@echo "  test          Run test suite with coverage"
	@echo "  lint          Check code style and quality"
	@echo "  format        Auto-format code with ruff"
	@echo "  type-check    Run mypy type checking"
	@echo "  run           Start local development server"
	@echo "  dev           Start development server with auto-reload"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean         Remove temporary files and caches"
	@echo "  health        Check system health and dependencies"
	@echo ""

# Bootstrap complete development environment
bootstrap: install
	@echo "🚀 Setting up development environment..."
	@pip install ruff pytest pytest-cov mypy pre-commit
	@pre-commit install
	@echo "✅ Development environment ready!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Copy .env.example to .env and add your secrets"
	@echo "  2. Run 'make test' to verify setup"
	@echo "  3. Run 'make run' to start development server"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	@pip install -r requirements_final.txt

# Run test suite
test:
	@echo "🧪 Running test suite..."
	@python -m pytest tests/ -v --cov=branchberg --cov=branchbot --cov-report=term-missing
	@echo "✅ Tests complete!"

# Lint code
lint:
	@echo "🔍 Checking code quality..."
	@ruff check .
	@echo "✅ Linting complete!"

# Format code
format:
	@echo "🎨 Formatting code..."
	@ruff format .
	@echo "✅ Formatting complete!"

# Type checking
type-check:
	@echo "🔍 Running type checks..."
	@mypy branchberg/ branchbot/ --ignore-missing-imports
	@echo "✅ Type checking complete!"

# Start development server
run:
	@echo "🚀 Starting development server..."
	@export PYTHONPATH=. && python -c "import importlib, uvicorn; importlib.import_module('branchberg.app.main') and uvicorn.run('branchberg.app.main:app', host='0.0.0.0', port=8000)"

# Start development server with auto-reload
dev:
	@echo "🚀 Starting development server with auto-reload..."
	@export PYTHONPATH=. && uvicorn branchberg.app.main:app --reload --host 0.0.0.0 --port 8000

# Start dashboard
dashboard:
	@echo "📊 Starting Streamlit dashboard..."
	@streamlit run branchberg/dashboard/streamlit_app.py

# Health check
health:
	@echo "🏥 System health check..."
	@echo "Python version: $$(python --version)"
	@echo "Pip version: $$(pip --version)"
	@echo "Working directory: $$(pwd)"
	@echo ""
	@echo "Key dependencies:"
	@pip show fastapi streamlit ruff pytest mypy 2>/dev/null || echo "❌ Development tools not installed (run 'make bootstrap')"
	@echo ""
	@echo "Environment file:"
	@test -f .env && echo "✅ .env exists" || echo "❌ .env missing (copy from .env.example)"

# Clean temporary files
clean:
	@echo "🧹 Cleaning temporary files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf htmlcov/ .coverage
	@echo "✅ Cleanup complete!"

# Quick setup verification
verify: test lint type-check
	@echo "✅ All checks passed! Environment is ready."

# Installation check
check-deps:
	@echo "📋 Checking required dependencies..."
	@python -c "import fastapi, streamlit, requests, uvicorn; print('✅ Runtime dependencies OK')"
	@python -c "import ruff, pytest, mypy; print('✅ Development dependencies OK')" 2>/dev/null || echo "❌ Run 'make bootstrap' to install dev tools"