"""Port of Services/StreamingService.cs (IStreamingService)."""

from __future__ import annotations

from datetime import datetime, timezone

import httpx

from config.airflow_options import AirflowOptions


class StreamingService:
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

    async def trigger_streaming(self) -> str:
        run_id = f"stream_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        async with self._client() as http:
            resp = await http.post(
                f"/api/v1/dags/{self._options.streaming_dag_id}/dagRuns",
                json={"dag_run_id": run_id},
            )
            resp.raise_for_status()
        return run_id

    async def get_streaming_status(self, run_id: str) -> str:
        async with self._client() as http:
            r = await http.get(f"/api/v1/dags/{self._options.streaming_dag_id}/dagRuns/{run_id}")
            r.raise_for_status()
            return r.text
