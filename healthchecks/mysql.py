"""Port of HealthChecks/MySqlHealthCheck.cs."""

from __future__ import annotations

import asyncio
from urllib.parse import urlparse

from config.database_options import DatabaseOptions

from .common import HealthCheckResult


class MySqlHealthCheck:
    """Pings MySQL by opening a connection and closing it, mirroring the .NET check."""

    def __init__(self, options: DatabaseOptions):
        self._options = options

    async def check(self, timeout: float = 3.0) -> HealthCheckResult:
        if not self._options.mysql:
            return HealthCheckResult.unhealthy("MySQL connection string not configured")

        try:
            import aiomysql  # type: ignore

            dsn = self._options.mysql
            parsed = urlparse(dsn)
            conn = await asyncio.wait_for(
                aiomysql.connect(
                    host=parsed.hostname or "localhost",
                    port=parsed.port or 3306,
                    user=parsed.username or "",
                    password=parsed.password or "",
                    db=(parsed.path or "/").lstrip("/") or None,
                ),
                timeout=timeout,
            )
            try:
                return HealthCheckResult.healthy()
            finally:
                conn.close()
        except Exception as exc:
            return HealthCheckResult.unhealthy(f"MySQL connection failed: {exc}")
