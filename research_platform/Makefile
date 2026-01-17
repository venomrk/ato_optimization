.PHONY: help install run test clean docker-build docker-up docker-down check-agents example

help:
	@echo "Multi-Agent Research Analysis Platform - Make Commands"
	@echo ""
	@echo "install          Install Python dependencies"
	@echo "run              Run the API server locally"
	@echo "test             Run tests"
	@echo "clean            Clean generated files"
	@echo "docker-build     Build Docker image"
	@echo "docker-up        Start Docker Compose stack"
	@echo "docker-down      Stop Docker Compose stack"
	@echo "check-agents     Check available agents"
	@echo "example          Run example query"
	@echo "cli-search       Search papers via CLI (use QUERY='your query')"
	@echo "cli-analyze      Analyze papers via CLI (use QUERY='query' QUESTION='question')"

install:
	pip install -r requirements.txt
	python -m spacy download en_core_web_sm

run:
	python main.py

test:
	pytest tests/ -v --cov=. --cov-report=html

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf *.egg-info
	rm -rf build dist

docker-build:
	docker build -t research-platform:latest .

docker-up:
	docker-compose up -d
	@echo "Waiting for services to start..."
	@sleep 5
	@echo "API available at http://localhost:8000"
	@echo "API docs at http://localhost:8000/docs"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api

check-agents:
	python scripts/check_agents.py

example:
	python scripts/example_query.py

cli-search:
	python cli.py search "$(QUERY)" --max-results=10

cli-analyze:
	python cli.py analyze "$(QUERY)" "$(QUESTION)" --max-papers=10

format:
	black .
	isort .

lint:
	flake8 . --max-line-length=120
	mypy . --ignore-missing-imports

setup-dev:
	pip install -r requirements.txt
	pip install black isort flake8 mypy pytest pytest-asyncio pytest-cov
	python -m spacy download en_core_web_sm
	cp .env.example .env
	@echo "Development environment ready!"
	@echo "Edit .env with your API keys"

# Quick start
quickstart: install
	@echo "Quick Start Setup"
	@echo "================="
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file - please edit with your API keys"; \
	else \
		echo ".env file exists"; \
	fi
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env with your API keys"
	@echo "2. Run 'make docker-up' to start the platform"
	@echo "3. Visit http://localhost:8000/docs for API documentation"
