"""Port of HealthChecks/AirflowHealthCheck.cs."""

from __future__ import annotations

import httpx

from config.airflow_options import AirflowOptions

from .common import HealthCheckResult


class AirflowHealthCheck:
    def __init__(self, options: AirflowOptions):
        self._options = options

    async def check(self, timeout: float = 5.0) -> HealthCheckResult:
        if not self._options.base_url:
            return HealthCheckResult.unhealthy("AIRFLOW_BASE_URL not set")

        url = self._options.base_url.rstrip("/") + "/health"
        auth = None
        if self._options.username and self._options.password:
            auth = (self._options.username, self._options.password)
        try:
            async with httpx.AsyncClient(timeout=timeout, auth=auth) as client:
                r = await client.get(url)
                if not r.is_success:
                    return HealthCheckResult.degraded(f"Airflow responded with {r.status_code}")

                try:
                    body = r.json()
                    meta = body.get("metadatabase", {}).get("status", "").lower()
                    sched = body.get("scheduler", {}).get("status", "").lower()
                    web = body.get("webserver", {}).get("status", "").lower()
                    all_ok = meta == "healthy" and sched == "healthy" and web == "healthy"
                    if all_ok:
                        return HealthCheckResult.healthy()
                    return HealthCheckResult.degraded(
                        f"Airflow status: meta={meta}, scheduler={sched}, webserver={web}"
                    )
                except Exception:
                    return HealthCheckResult.healthy("Airflow responded 200")
        except Exception as exc:
            return HealthCheckResult.unhealthy(f"Airflow health check failed: {exc}")
