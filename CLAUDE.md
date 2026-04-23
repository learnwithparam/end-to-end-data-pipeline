# CLAUDE.md

Guidance for Claude Code when working in this repo.

## What this is

Production-grade end-to-end data pipeline for [learnwithparam.com](https://www.learnwithparam.com). Twenty-service Docker Compose stack: Airflow + Kafka + Spark + Postgres + MySQL + MongoDB + Redis + InfluxDB + MinIO + Elasticsearch + MLflow + Prometheus + Grafana + (optional Snowflake) + a **Python FastAPI backend** that is a 1:1 port of the original .NET 8 reference (see the port map in `README.md`). Kubernetes/Terraform/Helm manifests are included for cluster deploys.

See `README.md` for the full walkthrough and `ARCHITECTURE.md` for diagrams.

## Quick start

### Just the FastAPI (no compose)

```bash
uv sync
cp .env.example .env
make run            # /docs on http://localhost:8000/docs
```

### Full stack

```bash
make setup
make up             # 20 services, ~18 GB RAM
make urls           # print all the service UI URLs
make trigger-batch  # run the batch DAG
make down
```

Use `make up-lite` for an ~8 GB footprint (drops Elasticsearch / InfluxDB / MLflow / Kafka producer).

## Smoke test

Covered by the shared sweep in `../smoke_test_all.sh`:

```bash
bash ../smoke_test_all.sh end-to-end-data-pipeline
```

The FastAPI `/health` returns 200 with graceful per-check degradation when the compose stack isn't up. `/api/batch` and the other ported controller endpoints stub upstream calls (Airflow / MinIO / Kafka) when they're unreachable, so the smoke test doesn't require the full stack.

## .NET → Python port map

The original `sample_dotnet_backend/` directory was removed and replaced with a 1:1 Python port. Files at a glance:

| .NET original | Python target |
|---|---|
| `Program.cs` | `main.py` |
| `Models/BatchRequest.cs`, `StreamingRequest.cs` | `models.py` |
| `Options/*.cs` (8 classes) | `config/*.py` |
| `HealthChecks/*.cs` (6 classes) | `healthchecks/*.py` |
| `Services/*.cs` + `Services/I*.cs` (10 pairs) | `services/*.py` |
| `Controllers/*.cs` (7 controllers) | `router.py` |
| `Dockerfile` (dotnet) | `Dockerfile` (python:3.11-slim + uv) |
| `appsettings.json` | `.env.example` |

HTTP routes and response shapes are preserved.

## Push workflow

Before every push:

1. Run the smoke test above. It must pass.
2. `.gitignore` covers `.env`, `__pycache__/`, `.venv/`, `airflow/logs/`, `mlruns/`, `terraform/.terraform/`, `*.tfstate*`.
3. `git status` — no secrets or generated infra state.
4. Commit with a descriptive message.
5. `git push origin main` — remote is `git@github.com:learnwithparam/end-to-end-data-pipeline.git`.

Never force-push. Never commit `.env`. The repo is ~4 MB after cleanup (no data, no logs).
