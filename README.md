# End-to-End Data Pipeline

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Airflow](https://img.shields.io/badge/Airflow-2.7.3-017CEE?logo=apacheairflow&logoColor=white)](https://airflow.apache.org/)
[![Spark](https://img.shields.io/badge/Spark-3.5.3-E25A1C?logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Kafka](https://img.shields.io/badge/Kafka-7.5.0-231F20?logo=apachekafka&logoColor=white)](https://kafka.apache.org/)
[![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?logo=snowflake&logoColor=white)](https://www.snowflake.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![MinIO](https://img.shields.io/badge/MinIO-C72E49?logo=minio&logoColor=white)](https://min.io/)
[![InfluxDB](https://img.shields.io/badge/InfluxDB-2.7-22ADF6?logo=influxdb&logoColor=white)](https://www.influxdata.com/)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.11-005571?logo=elasticsearch&logoColor=white)](https://www.elastic.co/)
[![MLflow](https://img.shields.io/badge/MLflow-2.9.2-0194E2?logo=mlflow&logoColor=white)](https://mlflow.org/)
[![Prometheus](https://img.shields.io/badge/Prometheus-2.48-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-10.2-F46800?logo=grafana&logoColor=white)](https://grafana.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Terraform](https://img.shields.io/badge/Terraform-7B42BC?logo=terraform&logoColor=white)](https://www.terraform.io/)
[![Helm](https://img.shields.io/badge/Helm-0F1689?logo=helm&logoColor=white)](https://helm.sh/)
[![learnwithparam](https://img.shields.io/badge/learnwithparam.com-0a0a0a?logo=readthedocs&logoColor=white)](https://www.learnwithparam.com)

A **production-grade, fully containerized data platform** with batch ingestion, real-time streaming, a star-schema data warehouse, ML experiment tracking, a **Python FastAPI backend** (ported 1:1 from a .NET 8 reference), and full observability — all orchestrated through **20 Docker services** managed by a single `docker compose` stack.

This is the top tier of the [learnwithparam.com](https://www.learnwithparam.com) data engineering track. It follows:

- **[`data-engineering-medallion`](../data-engineering-medallion)** — beginner, notebook-first, DuckDB + Pandas medallion pattern.
- **[`data-engineering-pipeline`](../data-engineering-pipeline)** — intermediate, trimmed Airflow + Spark + Postgres + MinIO + FastAPI stack.
- **`end-to-end-data-pipeline`** (this repo) — the full production platform with Kafka, Snowflake, MLflow, Prometheus, Grafana, Kubernetes, Terraform, and Helm.

## Table of Contents

- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Service URLs](#service-urls)
- [API Documentation (Python FastAPI)](#api-documentation-python-fastapi)
- [.NET → Python Port Map](#net--python-port-map)
- [Data Warehouse Schema](#data-warehouse-schema)
- [Airflow DAGs](#airflow-dags)
- [Testing](#testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Project Structure](#project-structure)
- [Credits](#credits)
- [License](#license)

## Architecture

```mermaid
graph TB
    subgraph Sources
        MYSQL[(MySQL 8.0<br/>Source DB)]
        KP[Kafka Producer<br/>Sensor Data]
    end

    subgraph Orchestration
        AF[Airflow 2.7.3<br/>3 DAGs]
    end

    subgraph Streaming
        ZK[Zookeeper] --> KAFKA[Kafka 7.5.0]
        KP --> KAFKA
    end

    subgraph Processing
        GE[Great Expectations<br/>Validation]
        SM[Spark Master] --> SW[Spark Worker]
    end

    subgraph Storage
        MINIO[MinIO<br/>S3-Compatible]
        PG[(PostgreSQL 15<br/>Warehouse + Processed)]
        MONGO[(MongoDB 6.0)]
        REDIS[(Redis 7)]
        INFLUX[(InfluxDB 2.7)]
    end

    subgraph Serving
        API[Python FastAPI<br/>Swagger /docs]
        MLFLOW[MLflow v2.9.2]
    end

    subgraph Observability
        PROM[Prometheus] --> GRAF[Grafana 10.2]
        ES[(Elasticsearch 8.11)]
    end

    MYSQL --> AF
    AF --> GE --> MINIO
    AF --> SM
    SM --> PG
    KAFKA --> SM
    PG --> API
    PG --> MLFLOW
    PROM --> API
    PROM --> AF
    PROM --> KAFKA
```

Detailed mermaid diagrams live in `ARCHITECTURE.md`.

## Technology Stack

- **Python 3.11** + **uv** — one language, one toolchain, across the whole platform (including the API that replaced the .NET reference backend)
- **Apache Airflow 2.7.3** — orchestration, 3 DAGs (`batch_ingestion_dag`, `streaming_monitoring_dag`, `warehouse_transform_dag`)
- **Apache Kafka 7.5.0** + Zookeeper — streaming ingest
- **Apache Spark 3.5.3** (master + workers) — batch + streaming ETL
- **PostgreSQL 15** — warehouse (star schema) + processed DB
- **MySQL 8.0** — source OLTP
- **MongoDB 6.0**, **Redis 7**, **InfluxDB 2.7** — mixed-workload datastores
- **MinIO** — S3-compatible raw/processed lake
- **Great Expectations** — data quality
- **MLflow 2.9.2** — experiment tracking
- **Elasticsearch 8.11** — log search
- **Prometheus 2.48** + **Grafana 10.2** — metrics & dashboards
- **FastAPI** + **pydantic-settings** + **structlog** — the API and its typed config
- **Docker Compose** + **Kubernetes** + **Terraform** + **Helm** — local through cloud deploys

## Prerequisites

- Docker Desktop (or Docker Engine + Compose) with ~18 GB RAM available, or ~8 GB for the lite profile
- `make`, `curl`, `git`
- Python 3.11 + [`uv`](https://astral.sh/uv) for local-only FastAPI runs
- (Optional) `kubectl`, `terraform`, `helm` for cluster deploys

## Quick Start

### Just the FastAPI (no compose, no Docker)

```bash
uv sync
cp .env.example .env
make run            # /docs on http://localhost:8000/docs
```

### Full stack

```bash
make setup
make up             # 20 services, ~18 GB RAM
make urls           # list service URLs
make trigger-batch  # trigger the batch DAG
make down
```

### Lite stack (~8 GB)

```bash
make up-lite
```

### Smoke test

```bash
bash ../smoke_test_all.sh end-to-end-data-pipeline
```

The FastAPI is designed for graceful degradation — every health check and controller endpoint returns a sane response when the upstream service isn't running, so the smoke test exercises the whole API surface without needing the full compose stack.

## Service URLs

| Service       | URL                               |
|---------------|-----------------------------------|
| Airflow UI    | http://localhost:8080             |
| FastAPI /docs | http://localhost:5000/docs        |
| MinIO Console | http://localhost:9001             |
| Grafana       | http://localhost:3000             |
| MLflow        | http://localhost:5001             |
| Spark Master  | http://localhost:8081             |
| Prometheus    | http://localhost:9090             |
| Elasticsearch | http://localhost:9200             |
| Kafka         | localhost:9092                    |

## API Documentation (Python FastAPI)

All endpoints live under `/api/*` plus the three standard `/health` probes. Auto-generated Swagger is at `http://localhost:5000/docs` (when running under compose) or `http://localhost:8000/docs` (when running locally with `make run`).

Endpoint map (preserved from the original .NET controllers):

| Controller | Route | Method | Purpose |
|---|---|---|---|
| BatchController | `/api/batch/ingest`, `/api/batch` | POST | Ingest from MySQL, upload to MinIO, optionally validate with GE + trigger Airflow |
| StreamingController | `/api/stream/produce` | POST | Produce a Kafka message |
| StreamingController | `/api/stream/run` | POST | Trigger the streaming DAG |
| WarehouseController | `/api/warehouse/transform` | POST | Trigger warehouse transform DAG |
| WarehouseController | `/api/warehouse/aggregations/daily-orders` | GET | Describe the daily-orders mart |
| WarehouseController | `/api/warehouse/pipeline-runs` | GET | Describe the pipeline-runs fact |
| WarehouseController | `/api/warehouse/health` | GET | Warehouse-specific health |
| WarehouseController | `/api/warehouse/snowflake/status` | GET | Snowflake config status |
| MLController | `/api/ml/run?expId=...&name=...` | POST | Create an MLflow run |
| MonitoringController | `/api/monitor/health` | GET | Aggregate health map |
| GovernanceController | `/api/governance/lineage` | POST | Register lineage with Apache Atlas |
| CIController | `/api/ci/trigger?wf=...&branch=...` | POST | Trigger a GitHub Actions workflow |
| Health | `/health`, `/health/ready`, `/health/live` | GET | k8s-style probes |

## .NET → Python Port Map

The original `sample_dotnet_backend/` directory has been replaced with a 1:1 Python port. Routes, response shapes, and status codes are preserved so downstream consumers (notebooks, dashboards, BI tools) continue to work.

| .NET original | Python target | Notes |
|---|---|---|
| `Program.cs` | `main.py` | FastAPI app + CORS + middleware + health endpoints + DI container |
| `Models/BatchRequest.cs`, `StreamingRequest.cs` | `models.py` | pydantic BaseModel |
| `Options/AirflowOptions.cs` | `config/airflow_options.py` | pydantic-settings `BaseSettings` |
| `Options/AtlasOptions.cs` | `config/atlas_options.py` | same |
| `Options/DatabaseOptions.cs` | `config/database_options.py` | same |
| `Options/GEOptions.cs` | `config/ge_options.py` | same |
| `Options/GitHubOptions.cs` | `config/github_options.py` | same |
| `Options/KafkaOptions.cs` | `config/kafka_options.py` | same |
| `Options/MinioOptions.cs` | `config/minio_options.py` | same |
| `Options/MLflowOptions.cs` | `config/mlflow_options.py` | same |
| `HealthChecks/AirflowHealthCheck.cs` | `healthchecks/airflow.py` | httpx |
| `HealthChecks/KafkaHealthCheck.cs` | `healthchecks/kafka.py` | confluent-kafka AdminClient |
| `HealthChecks/MinioHealthCheck.cs` | `healthchecks/minio.py` | `minio` SDK |
| `HealthChecks/MLflowHealthCheck.cs` | `healthchecks/mlflow.py` | httpx |
| `HealthChecks/MySqlHealthCheck.cs` | `healthchecks/mysql.py` | aiomysql |
| `HealthChecks/PostgresHealthCheck.cs` | `healthchecks/postgres.py` | asyncpg |
| `Services/DbService.cs` | `services/db_service.py` | aiomysql + asyncpg |
| `Services/MinioService.cs` | `services/minio_service.py` | `minio` SDK |
| `Services/KafkaService.cs` | `services/kafka_service.py` | confluent-kafka Producer |
| `Services/GEValidationService.cs` | `services/ge_validation_service.py` | `asyncio.create_subprocess_exec` |
| `Services/BatchService.cs` | `services/batch_service.py` | httpx + basic auth |
| `Services/StreamingService.cs` | `services/streaming_service.py` | httpx + basic auth |
| `Services/AtlasService.cs` | `services/atlas_service.py` | httpx + basic auth |
| `Services/MLflowService.cs` | `services/mlflow_service.py` | httpx |
| `Services/CIService.cs` | `services/ci_service.py` | httpx + bearer auth |
| `Services/MonitoringService.cs` | `services/monitoring_service.py` | aggregates the health-check callables |
| `Controllers/*.cs` (7 files) | `router.py` | one APIRouter, paths preserved |

## Data Warehouse Schema

Star schema lives in `scripts/init_warehouse.sql`. See `ARCHITECTURE.md` for ER diagrams and `snowflake/` for the Snowflake mirror.

## Airflow DAGs

- `batch_ingestion_dag` — MySQL → GE → MinIO (raw) → Spark batch → Postgres warehouse
- `streaming_monitoring_dag` — Kafka → Spark streaming → Elasticsearch + InfluxDB
- `warehouse_transform_dag` — Postgres → Snowflake (or Postgres marts)

Trigger them:

```bash
make trigger-batch
make trigger-warehouse
make list-dags
```

## Testing

```bash
make test           # pytest
make lint           # ruff
make format         # black + isort
```

## CI/CD Pipeline

See `.github/workflows/` for GitHub Actions workflows, `terraform/` for IaC, and `helm/e2e-pipeline/` for the Helm chart. Multi-provider deploys are scripted behind `make deploy-*`:

```bash
make deploy-local     # Docker Compose
make deploy-lite      # Docker Compose (~8 GB)
make deploy-k8s       # Helm on any cluster
make deploy-aws       # EKS via Terraform + Helm
make deploy-gcp       # GKE via Helm
make deploy-azure     # AKS via Helm
make deploy-onprem    # k3s / kubeadm via Helm
```

## Project Structure

```
end-to-end-data-pipeline/
├── main.py                  FastAPI app (Program.cs)
├── router.py                Routes (Controllers/*.cs)
├── models.py                Pydantic models (Models/*.cs)
├── config/                  Options/*.cs ports
├── healthchecks/            HealthChecks/*.cs ports
├── services/                Services/*.cs ports
├── airflow/                 DAGs + Airflow Dockerfile + plugins
├── spark/                   Batch + streaming jobs + Spark Dockerfile
├── kafka/                   Producer + Dockerfile
├── storage/                 Mongo / Redis / Influx / Elastic integration scripts
├── snowflake/               Snowflake schema + optional deploy
├── governance/              Atlas lineage config
├── great_expectations/      Expectations + checkpoints
├── ml/                      MLflow pipelines
├── monitoring/              Prometheus + Grafana config
├── bi_dashboards/           Static BI dashboards
├── kubernetes/              K8s manifests
├── helm/                    Helm chart (e2e-pipeline)
├── terraform/               AWS / GCP / Azure IaC
├── scripts/                 deploy.sh, init_db.sql, init_warehouse.sql
├── tests/                   pytest suite
├── docker-compose.yaml      20-service stack
├── docker-compose.lite.yaml lite profile
├── pyproject.toml           uv-managed deps
├── uv.lock
├── Makefile                 60+ targets
├── Dockerfile               python:3.11-slim + uv (API)
├── CLAUDE.md                guidance for Claude Code
└── README.md
```

## Credits

This project is a learnwithparam.com workshop fork of the open-source [End-to-End Data Pipeline](https://github.com/hoangsonww/End-to-End-Data-Pipeline) reference architecture by **Son Nguyen** (MIT). The original .NET 8 sample backend has been fully ported to Python/FastAPI for this fork. All original MIT copyright is preserved in `LICENSE`.

## License

MIT. See `LICENSE`.
