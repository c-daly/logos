"""Unified health response schema for LOGOS services.

All LOGOS HTTP services should use these models for their /health endpoints
to ensure consistent responses across the ecosystem.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


def _utc_now() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class DependencyStatus(BaseModel):
    """Status of an individual dependency (database, service, etc.)."""

    status: Literal["healthy", "degraded", "unavailable"]
    connected: bool | None = None
    latency_ms: float | None = None
    details: dict[str, Any] | None = None


class HealthResponse(BaseModel):
    """Unified health response for all LOGOS services.

    Example response:
        {
            "status": "healthy",
            "service": "hermes",
            "version": "0.2.0",
            "timestamp": "2025-12-06T15:30:00Z",
            "dependencies": {
                "neo4j": {"status": "healthy", "connected": true, "latency_ms": 5.2},
                "milvus": {"status": "healthy", "connected": true}
            },
            "capabilities": {
                "embedding": "openai",
                "llm": "anthropic"
            }
        }

    Usage:
        @app.get("/health", response_model=HealthResponse)
        async def health():
            neo4j_ok = await check_neo4j()
            return HealthResponse(
                status="healthy" if neo4j_ok else "degraded",
                service="my-service",
                version=__version__,
                dependencies={
                    "neo4j": DependencyStatus(
                        status="healthy" if neo4j_ok else "unavailable",
                        connected=neo4j_ok
                    )
                }
            )
    """

    # Core fields (REQUIRED)
    status: Literal["healthy", "degraded", "unavailable"]
    service: str
    version: str
    timestamp: str = Field(default_factory=_utc_now)

    # Dependencies (OPTIONAL - for database/service connectivity)
    dependencies: dict[str, DependencyStatus] | None = None

    # Capabilities (OPTIONAL - for service-specific features like LLM provider)
    capabilities: dict[str, str] | None = None
