"""Port of Services/MonitoringService.cs (IMonitoringService)."""

from __future__ import annotations

from typing import Awaitable, Callable

from healthchecks.common import HealthCheckResult, HealthStatus


class MonitoringService:
    """Aggregates the registered health checks.

    In .NET this wraps HealthCheckService; here we accept a dict of
    {name: async_check_callable} and assemble the same {name: status} map.
    """

    def __init__(self, checks: dict[str, Callable[[], Awaitable[HealthCheckResult]]]):
        self._checks = checks

    async def get_health(self) -> dict[str, str]:
        status: dict[str, str] = {}
        overall = HealthStatus.HEALTHY
        for name, check in self._checks.items():
            try:
                result = await check()
            except Exception as exc:
                result = HealthCheckResult.unhealthy(str(exc))
            status[name] = result.status.value
            if result.status == HealthStatus.UNHEALTHY:
                overall = HealthStatus.UNHEALTHY
            elif result.status == HealthStatus.DEGRADED and overall != HealthStatus.UNHEALTHY:
                overall = HealthStatus.DEGRADED
        status["overall"] = overall.value
        return status
