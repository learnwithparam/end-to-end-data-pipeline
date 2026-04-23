"""Port of HealthChecks/MLflowHealthCheck.cs."""

from __future__ import annotations

import httpx

from config.mlflow_options import MLflowOptions

from .common import HealthCheckResult


class MLflowHealthCheck:
    def __init__(self, options: MLflowOptions):
        self._options = options

    async def check(self, timeout: float = 5.0) -> HealthCheckResult:
        if not self._options.tracking_uri:
            return HealthCheckResult.unhealthy("MLFLOW_TRACKING_URI not set")

        url = self._options.tracking_uri.rstrip("/") + "/api/2.0/mlflow/experiments/list?max_results=1"
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                r = await client.get(url)
                if r.is_success:
                    return HealthCheckResult.healthy()
                return HealthCheckResult.degraded(f"MLflow responded with {r.status_code}")
        except Exception as exc:
            return HealthCheckResult.unhealthy(f"MLflow unreachable: {exc}")
