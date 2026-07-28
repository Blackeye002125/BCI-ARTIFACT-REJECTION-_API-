# ============================================
# INSTALLATION
# ============================================
install:
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt
	pre-commit install

# ============================================
# TESTING
# ============================================
test:
	pytest tests/ -v --cov=src --cov=api --cov-report=html

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-performance:
	pytest tests/performance/ -v

# ============================================
# DEVELOPMENT
# ============================================
run:
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

run-prod:
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

# ============================================
# DOCKER
# ============================================
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v
	docker system prune -f

# ============================================
# CODE QUALITY
# ============================================
format:
	black src/ api/ tests/
	isort src/ api/ tests/

lint:
	flake8 src/ api/ tests/
	mypy src/ api/

check: format lint

# ============================================
# DATA & MODELS
# ============================================
download-data:
	python scripts/download_sample_data.py

train-models:
	python scripts/train_models.py

benchmark:
	python scripts/benchmark.py

# ============================================
# CLEANUP
# ============================================
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -rf build/ dist/ *.egg-info/
	rm -f .coverage

clean-all: clean docker-clean
	rm -rf data/raw/* data/processed/* data/augmented/*
	rm -rf models/*

# ============================================
# HELP
# ============================================
help:
	@echo "Available commands:"
	@echo "  make install          - Install production dependencies"
	@echo "  make dev              - Install development dependencies"
	@echo "  make test             - Run all tests"
	@echo "  make run              - Run development server"
	@echo "  make run-prod         - Run production server"
	@echo "  make docker-up        - Start Docker services"
	@echo "  make docker-down      - Stop Docker services"
	@echo "  make format           - Format code"
	@echo "  make lint             - Lint code"
	@echo "  make download-data    - Download sample EEG data"
	@echo "  make train-models     - Train ML models"
	@echo "  make clean            - Clean build artifacts"
