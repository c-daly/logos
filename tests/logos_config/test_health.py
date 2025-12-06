"""Tests for logos_config.health module."""

from __future__ import annotations

import re
from datetime import UTC, datetime

from logos_config.health import DependencyStatus, HealthResponse, _utc_now


class TestUtcNow:
    """Tests for _utc_now helper."""

    def test_returns_iso_format(self) -> None:
        """Returns ISO 8601 formatted string."""
        result = _utc_now()
        # Should match ISO 8601 with Z suffix
        assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", result)
        assert result.endswith("Z")

    def test_is_current_time(self) -> None:
        """Returns approximately current time."""
        before = datetime.now(UTC)
        result = _utc_now()
        after = datetime.now(UTC)

        # Parse the result (remove Z, add +00:00 for parsing)
        parsed = datetime.fromisoformat(result.replace("Z", "+00:00"))
        assert before <= parsed <= after


class TestDependencyStatus:
    """Tests for DependencyStatus model."""

    def test_minimal_status(self) -> None:
        """Only status is required."""
        status = DependencyStatus(status="healthy")
        assert status.status == "healthy"
        assert status.connected is None
        assert status.latency_ms is None
        assert status.details is None

    def test_full_status(self) -> None:
        """All fields can be set."""
        status = DependencyStatus(
            status="degraded",
            connected=True,
            latency_ms=5.2,
            details={"version": "5.14.0"},
        )
        assert status.status == "degraded"
        assert status.connected is True
        assert status.latency_ms == 5.2
        assert status.details == {"version": "5.14.0"}

    def test_status_values(self) -> None:
        """Status must be one of the allowed values."""
        DependencyStatus(status="healthy")
        DependencyStatus(status="degraded")
        DependencyStatus(status="unavailable")


class TestHealthResponse:
    """Tests for HealthResponse model."""

    def test_required_fields(self) -> None:
        """Status, service, and version are required."""
        response = HealthResponse(
            status="healthy",
            service="test-service",
            version="1.0.0",
        )
        assert response.status == "healthy"
        assert response.service == "test-service"
        assert response.version == "1.0.0"

    def test_timestamp_auto_generated(self) -> None:
        """Timestamp is auto-generated if not provided."""
        response = HealthResponse(
            status="healthy",
            service="test-service",
            version="1.0.0",
        )
        assert response.timestamp is not None
        assert response.timestamp.endswith("Z")

    def test_timestamp_can_be_overridden(self) -> None:
        """Timestamp can be explicitly set."""
        response = HealthResponse(
            status="healthy",
            service="test-service",
            version="1.0.0",
            timestamp="2025-01-01T00:00:00Z",
        )
        assert response.timestamp == "2025-01-01T00:00:00Z"

    def test_with_dependencies(self) -> None:
        """Dependencies can be set."""
        response = HealthResponse(
            status="healthy",
            service="test-service",
            version="1.0.0",
            dependencies={
                "neo4j": DependencyStatus(status="healthy", connected=True),
                "milvus": DependencyStatus(status="unavailable", connected=False),
            },
        )
        assert response.dependencies is not None
        assert len(response.dependencies) == 2
        assert response.dependencies["neo4j"].status == "healthy"
        assert response.dependencies["milvus"].status == "unavailable"

    def test_with_capabilities(self) -> None:
        """Capabilities can be set."""
        response = HealthResponse(
            status="healthy",
            service="test-service",
            version="1.0.0",
            capabilities={
                "embedding": "openai",
                "llm": "anthropic",
            },
        )
        assert response.capabilities == {"embedding": "openai", "llm": "anthropic"}

    def test_json_serialization(self) -> None:
        """Can be serialized to JSON."""
        response = HealthResponse(
            status="healthy",
            service="test-service",
            version="1.0.0",
            timestamp="2025-01-01T00:00:00Z",
            dependencies={
                "neo4j": DependencyStatus(status="healthy", connected=True),
            },
        )
        json_dict = response.model_dump()
        assert json_dict["status"] == "healthy"
        assert json_dict["service"] == "test-service"
        assert json_dict["dependencies"]["neo4j"]["status"] == "healthy"
