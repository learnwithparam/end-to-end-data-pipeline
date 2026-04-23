"""Port of HealthChecks/MinioHealthCheck.cs."""

from __future__ import annotations

import asyncio
from urllib.parse import urlparse

from config.minio_options import MinioOptions

from .common import HealthCheckResult


def _parse_endpoint(endpoint: str) -> tuple[str, bool]:
    parsed = urlparse(endpoint if "://" in endpoint else f"http://{endpoint}")
    host = parsed.netloc or parsed.path
    secure = parsed.scheme == "https"
    return host, secure


class MinioHealthCheck:
    def __init__(self, options: MinioOptions):
        self._options = options

    async def check(self, timeout: float = 3.0) -> HealthCheckResult:
        if not self._options.endpoint or not self._options.access_key:
            return HealthCheckResult.unhealthy("MinIO not configured")

        host, secure = _parse_endpoint(self._options.endpoint)
        ak, sk = self._options.access_key, self._options.secret_key
        raw, proc = self._options.bucket_raw, self._options.bucket_processed

        def _probe() -> HealthCheckResult:
            from minio import Minio  # type: ignore

            client = Minio(host, access_key=ak, secret_key=sk, secure=secure)
            buckets = [b.name for b in client.list_buckets()]
            if raw in buckets or proc in buckets:
                return HealthCheckResult.healthy(f"buckets: {buckets}")
            return HealthCheckResult.degraded("MinIO reachable but pipeline buckets missing")

        try:
            return await asyncio.wait_for(asyncio.to_thread(_probe), timeout=timeout)
        except Exception as exc:
            return HealthCheckResult.unhealthy(f"MinIO unreachable: {exc}")
