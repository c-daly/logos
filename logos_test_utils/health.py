"""Health schema helpers for LOGOS services."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class DependencyHealth(BaseModel):
    name: str
    status: Literal["connected", "disconnected", "unknown"]
    critical: bool = True
    host: str | None = None
    port: int | None = None
    latency_ms: float | None = None


class ServiceHealth(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    service: str
    timestamp: str
    dependencies: list[DependencyHealth] = Field(default_factory=list)

    @classmethod
    def compute_status(
        cls,
        deps: list[DependencyHealth],
    ) -> Literal["healthy", "degraded", "unhealthy"]:
        """Derive status from dependency states."""

        critical_down = any(d.status != "connected" and d.critical for d in deps)
        non_critical_down = any(d.status != "connected" and not d.critical for d in deps)
        if critical_down:
            return "unhealthy"
        if non_critical_down:
            return "degraded"
        return "healthy"
