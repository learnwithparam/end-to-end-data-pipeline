.PHONY: help setup install dev run smoke build up up-lite down restart clean clean-all status health logs rebuild test lint format format-check validate \
	kafka-topics spark-batch spark-stream trigger-batch trigger-warehouse list-dags \
	airflow-ui grafana-ui minio-ui mlflow-ui spark-ui api-ui urls \
	deploy-local deploy-lite deploy-k8s deploy-aws deploy-gcp deploy-azure deploy-onprem deploy-status deploy-teardown

.DEFAULT_GOAL := help

COMPOSE = docker compose
UV = uv

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

# ===========================
# Python (FastAPI control plane)
# ===========================
setup: ## Initial setup (create .env, install uv, uv sync)
	@if [ ! -f .env ]; then cp .env.example .env && echo "OK: .env created"; else echo ".env already exists"; fi
	@if ! command -v uv >/dev/null 2>&1; then curl -LsSf https://astral.sh/uv/install.sh | sh; fi
	@$(UV) sync

install: ## uv sync
	@$(UV) sync

run: ## Run FastAPI locally on :8000
	@$(UV) run uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev: setup run ## Setup + run

smoke: ## Shared smoke test (server on :8111, /health + /api/batch)
	@bash ../smoke_test_all.sh end-to-end-data-pipeline

# ===========================
# Docker Lifecycle (full pipeline stack)
# ===========================
build: ## Build all Docker images
	$(COMPOSE) build

up: ## Start all services (full stack, ~18GB RAM)
	$(COMPOSE) up -d

up-lite: ## Start core services only (~8GB RAM, disables ES/InfluxDB/MLflow)
	$(COMPOSE) -f docker-compose.yaml -f docker-compose.lite.yaml up -d

down: ## Stop all services
	$(COMPOSE) down

restart: ## Restart all services
	$(COMPOSE) down && $(COMPOSE) up -d

clean: ## Clean local Python venv + caches
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@$(UV) cache clean

clean-all: ## Stop services and remove all volumes
	$(COMPOSE) down -v --remove-orphans
	rm -rf .venv

rebuild: ## Rebuild and restart all services from scratch
	$(COMPOSE) down && $(COMPOSE) build --no-cache && $(COMPOSE) up -d

# ===========================
# Observability
# ===========================
status: ## Show status of all services
	$(COMPOSE) ps

health: ## Check health of all services
	@echo "=== Service Health ===" && $(COMPOSE) ps --format "table {{.Name}}\t{{.Status}}"

logs: ## Tail logs for all services
	$(COMPOSE) logs -f

logs-%: ## Tail logs for a specific service (e.g. make logs-kafka)
	$(COMPOSE) logs -f $*

shell-%: ## Open a shell in a container (e.g. make shell-airflow-webserver)
	$(COMPOSE) exec $* /bin/bash 2>/dev/null || $(COMPOSE) exec $* /bin/sh

# ===========================
# Testing & Quality (Python-only)
# ===========================
test: ## Run pytest
	$(UV) run pytest tests/ -v --tb=short

lint: ## Ruff
	$(UV) run ruff check .

format: ## Black + isort
	$(UV) run black --line-length 120 .
	$(UV) run isort --profile black --line-length 120 .

format-check: ## Check formatting
	$(UV) run black --check --line-length 120 .
	$(UV) run isort --check-only --profile black --line-length 120 .

validate: ## Validate docker-compose config
	$(COMPOSE) config --quiet && echo "docker-compose.yaml: VALID"

# ===========================
# Pipeline Operations
# ===========================
kafka-topics: ## List Kafka topics
	$(COMPOSE) exec kafka kafka-topics --bootstrap-server localhost:29092 --list

spark-batch: ## Run Spark batch ETL job
	$(COMPOSE) exec spark-master spark-submit --master spark://spark-master:7077 /opt/spark_jobs/spark_batch_job.py

spark-stream: ## Run Spark streaming job
	$(COMPOSE) exec spark-master spark-submit --master spark://spark-master:7077 /opt/spark_jobs/spark_streaming_job.py

trigger-batch: ## Trigger batch ingestion DAG in Airflow
	$(COMPOSE) exec airflow-webserver airflow dags trigger batch_ingestion_dag

trigger-warehouse: ## Trigger warehouse transform DAG in Airflow
	$(COMPOSE) exec airflow-webserver airflow dags trigger warehouse_transform_dag

list-dags: ## List all Airflow DAGs
	$(COMPOSE) exec airflow-webserver airflow dags list

# ===========================
# Service UIs
# ===========================
airflow-ui: ## Show Airflow UI URL
	@echo "Airflow UI:    http://localhost:8080"

grafana-ui: ## Show Grafana UI URL
	@echo "Grafana UI:    http://localhost:3000"

minio-ui: ## Show MinIO Console URL
	@echo "MinIO Console: http://localhost:9001"

mlflow-ui: ## Show MLflow UI URL
	@echo "MLflow UI:     http://localhost:5001"

spark-ui: ## Show Spark Master UI URL
	@echo "Spark UI:      http://localhost:8081"

api-ui: ## Show FastAPI /docs URL
	@echo "API /docs:     http://localhost:5000/docs"

urls: ## Show all service URLs
	@echo "=== Service URLs ==="
	@echo "Airflow UI:    http://localhost:8080"
	@echo "Grafana UI:    http://localhost:3000"
	@echo "MinIO Console: http://localhost:9001"
	@echo "MLflow UI:     http://localhost:5001"
	@echo "Spark UI:      http://localhost:8081"
	@echo "API /docs:     http://localhost:5000/docs"
	@echo "Prometheus:    http://localhost:9090"
	@echo "Elasticsearch: http://localhost:9200"
	@echo "Kafka:         localhost:9092"

# ===========================
# Deployment (Multi-Provider)
# ===========================
deploy-local: ## Deploy with Docker Compose (full stack)
	./scripts/deploy.sh local

deploy-lite: ## Deploy with Docker Compose (lite, ~8GB RAM)
	./scripts/deploy.sh local-lite

deploy-k8s: ## Deploy to any Kubernetes cluster via Helm
	./scripts/deploy.sh k8s

deploy-aws: ## Deploy to AWS EKS (Terraform + Helm)
	./scripts/deploy.sh aws

deploy-gcp: ## Deploy to GCP GKE via Helm
	./scripts/deploy.sh gcp

deploy-azure: ## Deploy to Azure AKS via Helm
	./scripts/deploy.sh azure

deploy-onprem: ## Deploy to on-prem Kubernetes (k3s, kubeadm, etc.)
	./scripts/deploy.sh k8s helm/e2e-pipeline/values-onprem.yaml

deploy-status: ## Show deployment status
	./scripts/deploy.sh status

deploy-teardown: ## Remove deployment
	./scripts/deploy.sh teardown
