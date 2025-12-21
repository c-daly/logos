"""Tests for logos_test_utils health helpers."""

from __future__ import annotations

from logos_test_utils.health import DependencyHealth, ServiceHealth


def test_compute_status_healthy() -> None:
    deps = [
        DependencyHealth(name="neo4j", status="connected"),
        DependencyHealth(name="milvus", status="connected"),
    ]
    assert ServiceHealth.compute_status(deps) == "healthy"


def test_compute_status_degraded_for_non_critical() -> None:
    deps = [
        DependencyHealth(name="neo4j", status="connected"),
        DependencyHealth(name="milvus", status="disconnected", critical=False),
    ]
    assert ServiceHealth.compute_status(deps) == "degraded"


def test_compute_status_unhealthy_for_critical() -> None:
    deps = [
        DependencyHealth(name="neo4j", status="unknown", critical=True),
        DependencyHealth(name="milvus", status="connected"),
    ]
    assert ServiceHealth.compute_status(deps) == "unhealthy"
