"""Port of Services/BatchService.cs (IBatchService)."""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from config.airflow_options import AirflowOptions


class BatchService:
    def __init__(self, options: AirflowOptions):
        self._options = options

    def _client(self) -> httpx.AsyncClient:
        auth = None
        if self._options.username and self._options.password:
            auth = (self._options.username, self._options.password)
        return httpx.AsyncClient(
            base_url=self._options.base_url or "http://localhost:8080",
            timeout=self._options.request_timeout_seconds,
            headers={"User-Agent": "DataPipelineApi/2.0"},
            auth=auth,
        )

    async def trigger_batch(self) -> str:
        run_id = f"batch_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        async with self._client() as http:
            resp = await http.post(
                f"/api/v1/dags/{self._options.batch_dag_id}/dagRuns",
                json={"dag_run_id": run_id},
            )
            resp.raise_for_status()
        return run_id

    async def get_batch_status(self, run_id: str) -> str:
        async with self._client() as http:
            r = await http.get(f"/api/v1/dags/{self._options.batch_dag_id}/dagRuns/{run_id}")
            r.raise_for_status()
            return r.text
