"""Shared result type for health checks — mirrors .NET HealthCheckResult."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class HealthStatus(str, Enum):
    HEALTHY = "Healthy"
    DEGRADED = "Degraded"
    UNHEALTHY = "Unhealthy"


class HealthCheckResult(BaseModel):
    status: HealthStatus
    description: str | None = None
    duration_ms: float = 0.0
    tags: list[str] = []

    @classmethod
    def healthy(cls, description: str | None = None) -> "HealthCheckResult":
        return cls(status=HealthStatus.HEALTHY, description=description)

    @classmethod
    def degraded(cls, description: str | None = None) -> "HealthCheckResult":
        return cls(status=HealthStatus.DEGRADED, description=description)

    @classmethod
    def unhealthy(cls, description: str | None = None) -> "HealthCheckResult":
        return cls(status=HealthStatus.UNHEALTHY, description=description)
