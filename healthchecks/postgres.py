"""Port of HealthChecks/PostgresHealthCheck.cs."""

from __future__ import annotations

import asyncio

from config.database_options import DatabaseOptions

from .common import HealthCheckResult


def _asyncpg_dsn(dsn: str) -> str:
    if "+psycopg2" in dsn:
        dsn = dsn.replace("+psycopg2", "")
    return dsn


class PostgresHealthCheck:
    def __init__(self, options: DatabaseOptions):
        self._options = options

    async def check(self, timeout: float = 3.0) -> HealthCheckResult:
        if not self._options.postgres:
            return HealthCheckResult.unhealthy("PostgreSQL connection string not configured")
        try:
            import asyncpg  # type: ignore

            conn = await asyncio.wait_for(
                asyncpg.connect(_asyncpg_dsn(self._options.postgres)),
                timeout=timeout,
            )
            try:
                await conn.execute("SELECT 1")
                return HealthCheckResult.healthy()
            finally:
                await conn.close()
        except Exception as exc:
            return HealthCheckResult.unhealthy(f"PostgreSQL connection failed: {exc}")
