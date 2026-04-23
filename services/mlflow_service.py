"""Port of Services/MLflowService.cs (IMLflowService)."""

from __future__ import annotations

import httpx

from config.mlflow_options import MLflowOptions


class MLflowService:
    def __init__(self, options: MLflowOptions):
        self._options = options

    async def create_run(self, experiment_id: str, run_name: str) -> str:
        if not self._options.tracking_uri:
            raise RuntimeError("MLFLOW_TRACKING_URI not configured")
        async with httpx.AsyncClient(
            base_url=self._options.tracking_uri,
            timeout=self._options.request_timeout_seconds,
        ) as http:
            r = await http.post(
                "/api/2.0/mlflow/runs/create",
                json={"experiment_id": experiment_id, "run_name": run_name},
            )
            r.raise_for_status()
            return r.text
