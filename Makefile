.PHONY: help install dev lint test clean docker docker-run docker-stop

help:
	@echo "PlutoClips Worker - Development Commands"
	@echo ""
	@echo "  make install       Install dependencies"
	@echo "  make dev           Run development server"
	@echo "  make lint          Run code linting"
	@echo "  make test          Run test suite"
	@echo "  make clean         Clean temporary files"
	@echo "  make docker        Build Docker image"
	@echo "  make docker-run    Run Docker container"
	@echo "  make docker-stop   Stop Docker container"
	@echo ""

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

format:
	black app/ main.py

lint:
	flake8 app/ main.py
	mypy app/ main.py

test:
	pytest tests/ -v --cov=app

test-watch:
	pytest tests/ -v --watch

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf dist build

docker:
	docker build -t plutoclips-worker:latest .

docker-run:
	docker run -d \
		-p 8000:8000 \
		-e OPENAI_API_KEY=$${OPENAI_API_KEY} \
		-e ANTHROPIC_API_KEY=$${ANTHROPIC_API_KEY} \
		-v $$(pwd)/uploads:/app/uploads \
		-v $$(pwd)/outputs:/app/outputs \
		--name plutoclips-worker \
		plutoclips-worker:latest

docker-stop:
	docker stop plutoclips-worker || true
	docker rm plutoclips-worker || true

docker-logs:
	docker logs -f plutoclips-worker

docker-exec:
	docker exec -it plutoclips-worker /bin/bash
