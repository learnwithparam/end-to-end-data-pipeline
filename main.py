"""FastAPI application entry point. 1:1 Python port of sample_dotnet_backend/Program.cs.

Wires options, services, health checks, middleware, CORS, and routes — mirroring the
.NET DI container and WebApplication pipeline.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import (
    AirflowOptions,
    AtlasOptions,
    DatabaseOptions,
    GEOptions,
    GitHubOptions,
    KafkaOptions,
    MinioOptions,
    MLflowOptions,
)
from healthchecks import (
    AirflowHealthCheck,
    KafkaHealthCheck,
    MinioHealthCheck,
    MLflowHealthCheck,
    MySqlHealthCheck,
    PostgresHealthCheck,
)
from router import router
from services import (
    AtlasService,
    BatchService,
    CIService,
    DbService,
    GEValidationService,
    KafkaService,
    MinioService,
    MLflowService,
    MonitoringService,
    StreamingService,
)

logging.basicConfig(level=logging.INFO)
log = structlog.get_logger()


@dataclass
class ServiceContainer:
    db: DbService
    storage: MinioService
    kafka: KafkaService
    ge: GEValidationService
    batch: BatchService
    streaming: StreamingService
    atlas: AtlasService
    mlflow: MLflowService
    ci: CIService
    monitoring: MonitoringService


def build_container() -> ServiceContainer:
    """Mirror of builder.Services.AddSingleton<...> registrations in Program.cs."""
    db_opts = DatabaseOptions()
    airflow_opts = AirflowOptions()
    minio_opts = MinioOptions()
    kafka_opts = KafkaOptions()
    ge_opts = GEOptions()
    atlas_opts = AtlasOptions()
    mlflow_opts = MLflowOptions()
    github_opts = GitHubOptions()

    # Health checks registered as named callables (mirrors .AddCheck<T>("name") chain)
    mysql_hc = MySqlHealthCheck(db_opts)
    postgres_hc = PostgresHealthCheck(db_opts)
    minio_hc = MinioHealthCheck(minio_opts)
    kafka_hc = KafkaHealthCheck(kafka_opts)
    airflow_hc = AirflowHealthCheck(airflow_opts)
    mlflow_hc = MLflowHealthCheck(mlflow_opts)

    monitoring = MonitoringService(
        {
            "mysql": mysql_hc.check,
            "postgres": postgres_hc.check,
            "minio": minio_hc.check,
            "kafka": kafka_hc.check,
            "airflow": airflow_hc.check,
            "mlflow": mlflow_hc.check,
        }
    )

    return ServiceContainer(
        db=DbService(db_opts),
        storage=MinioService(minio_opts),
        kafka=KafkaService(kafka_opts),
        ge=GEValidationService(ge_opts),
        batch=BatchService(airflow_opts),
        streaming=StreamingService(airflow_opts),
        atlas=AtlasService(atlas_opts),
        mlflow=MLflowService(mlflow_opts),
        ci=CIService(github_opts),
        monitoring=monitoring,
    )


app = FastAPI(
    title="E2E Data Pipeline API",
    description=(
        "Enterprise-grade API for orchestrating batch ingestion, streaming, data governance, "
        "ML pipelines, and warehouse operations. Python port of the .NET 8 reference. "
        "learnwithparam.com workshop."
    ),
    version="2.0.0",
    contact={"name": "learnwithparam.com", "url": "https://www.learnwithparam.com"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.container = build_container()
log.info("app.init.done")

app.include_router(router)


# ============================================================
# Health endpoints (port of app.MapHealthChecks in Program.cs)
# ============================================================


@app.get("/health")
async def health() -> JSONResponse:
    container: ServiceContainer = app.state.container
    status = await container.monitoring.get_health()
    overall = status.get("overall", "Healthy")
    return JSONResponse(
        status_code=200,
        content={
            "status": overall,
            "checks": {k: v for k, v in status.items() if k != "overall"},
        },
    )


@app.get("/health/ready")
async def health_ready() -> JSONResponse:
    # Mirrors Predicate: check => check.Tags.Contains("critical")
    container: ServiceContainer = app.state.container
    status = await container.monitoring.get_health()
    critical = ["mysql", "postgres", "minio", "kafka"]
    any_unhealthy = any(status.get(c) == "Unhealthy" for c in critical)
    overall = "Unhealthy" if any_unhealthy else "Healthy"
    return JSONResponse(status_code=200, content={"status": overall})


@app.get("/health/live")
async def health_live() -> JSONResponse:
    return JSONResponse(status_code=200, content={"status": "Healthy"})


@app.get("/")
async def root() -> dict:
    return {
        "service": "end-to-end-data-pipeline",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
    }
