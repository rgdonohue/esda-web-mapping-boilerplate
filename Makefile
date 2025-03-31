.PHONY: setup dev test lint format clean build migrate help

# Colors for help messages
BLUE=\033[0;34m
NC=\033[0m # No Color

help: ## Show this help message
	@echo 'Usage:'
	@echo '  ${BLUE}make${NC} ${BLUE}<target>${NC}'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  ${BLUE}%-15s${NC} %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Initial project setup
	@echo "Setting up development environment..."
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@python -m venv venv
	@. venv/bin/activate && pip install -r requirements.txt
	@. venv/bin/activate && pip install -r requirements-dev.txt
	@cd frontend && npm install
	@echo "Setup complete! Run 'make dev' to start the development servers"

dev: ## Start development environment
	@echo "Starting development servers..."
	@chmod +x scripts/run_backend.sh scripts/run_frontend.sh
	@./scripts/run_backend.sh & ./scripts/run_frontend.sh

test: ## Run all tests
	@echo "Running backend tests..."
	@. venv/bin/activate && pytest
	@echo "Running frontend tests..."
	@cd frontend && npm test

lint: ## Run linters
	@echo "Running Python linters..."
	@. venv/bin/activate && flake8 .
	@. venv/bin/activate && mypy .
	@echo "Running JavaScript/TypeScript linters..."
	@cd frontend && npm run lint

format: ## Format code
	@echo "Formatting Python code..."
	@. venv/bin/activate && black .
	@echo "Formatting JavaScript/TypeScript code..."
	@cd frontend && npm run format

clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	@rm -rf build dist *.egg-info
	@rm -rf frontend/build frontend/dist
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type d -name .pytest_cache -exec rm -rf {} +
	@find . -type d -name .mypy_cache -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete

build: ## Build for production
	@echo "Building backend..."
	@. venv/bin/activate && python setup.py build
	@echo "Building frontend..."
	@cd frontend && npm run build

migrate: ## Run database migrations
	@echo "Running database migrations..."
	@. venv/bin/activate && alembic upgrade head

# Make scripts executable
scripts/%.sh:
	@chmod +x $@