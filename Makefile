.PHONY: help install install-dev run test lint format clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

run: ## Start API and dashboard locally (requires two terminals)
	@echo "Starting API and Dashboard..."
	@echo "Run in terminal 1: uvicorn branchberg.app.main:app --reload --port 8000"
	@echo "Run in terminal 2: streamlit run branchberg/dashboard/streamlit_app.py --server.port 8502"
	@echo "Or use: ./scripts/run-local.sh (Unix/Mac) or .\scripts\run-local.ps1 (Windows)"

test: ## Run tests
	PYTHONPATH=. pytest -v

test-minimal: ## Run minimal test only
	PYTHONPATH=. pytest branchbot/test_minimal.py -v

lint: ## Run ruff linting
	ruff check . --exclude '.github/workflows/ops' --exclude 'ops'

format: ## Format code with ruff
	ruff format . --exclude '.github/workflows/ops' --exclude 'ops'

format-check: ## Check code formatting
	ruff format --check . --exclude '.github/workflows/ops' --exclude 'ops'

syntax-check: ## Check Python syntax
	python -m compileall -q branchberg/ branchbot/ tests/ apps/ jobs/ gumroad/

pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

clean: ## Clean up temporary files and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.db" -delete
	rm -rf .ruff_cache 2>/dev/null || true

api: ## Start API only
	python -m uvicorn branchberg.app.main:app --reload --port 8000

dashboard: ## Start dashboard only
	streamlit run branchberg/dashboard/streamlit_app.py --server.port 8502
