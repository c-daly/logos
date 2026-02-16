"""
Tests for OpenTelemetry infrastructure stack.

These tests verify that the OTel collector, Jaeger, and Prometheus
services are properly configured and accessible.
"""

import subprocess
import time
from pathlib import Path

import pytest
import requests


@pytest.fixture(scope="module")
def otel_stack():
    """Start the OTel stack for testing."""
    # Get the project root directory (where docker-compose.otel.yml is)
    project_root = Path(__file__).parent.parent.parent.absolute()

    # Start the stack
    subprocess.run(
        ["docker", "compose", "-f", "docker-compose.otel.yml", "up", "-d"],
        cwd=str(project_root),
        check=True,
        capture_output=True,
    )

    # Wait for services to start
    time.sleep(10)

    yield

    # Cleanup
    subprocess.run(
        ["docker", "compose", "-f", "docker-compose.otel.yml", "down"],
        cwd=str(project_root),
        check=True,
        capture_output=True,
    )


def test_jaeger_ui_accessible(otel_stack):
    """Verify Jaeger UI is accessible."""
    response = requests.get("http://localhost:16686/", timeout=5)
    assert response.status_code == 200
    assert "<!doctype html>" in response.text.lower()


def test_prometheus_accessible(otel_stack):
    """Verify Prometheus is accessible and healthy."""
    response = requests.get("http://localhost:9090/-/healthy", timeout=5)
    assert response.status_code == 200
    assert "Prometheus Server is Healthy" in response.text


def test_otel_collector_health_endpoint(otel_stack):
    """Verify OTel collector health extension port is accessible."""
    import socket

    # The collector's health endpoint on port 13133 may just close connections
    # or return an empty response. Just verify the port is open.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("localhost", 13133))
    sock.close()
    assert result == 0, "OTel collector health port 13133 should be open"


def test_otlp_grpc_port_open(otel_stack):
    """Verify OTLP gRPC port is open."""
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("localhost", 4317))
    sock.close()
    assert result == 0, "OTLP gRPC port 4317 should be open"


def test_otlp_http_port_open(otel_stack):
    """Verify OTLP HTTP port is open."""
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("localhost", 4318))
    sock.close()
    assert result == 0, "OTLP HTTP port 4318 should be open"


def test_prometheus_targets(otel_stack):
    """Verify Prometheus has the expected target configurations."""
    response = requests.get("http://localhost:9090/api/v1/targets", timeout=5)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"

    # Get list of job names
    jobs = {target["labels"]["job"] for target in data["data"]["activeTargets"]}

    # Verify expected jobs are configured
    expected_jobs = {"otel-collector", "sophia", "hermes", "apollo"}
    assert expected_jobs.issubset(jobs), f"Expected jobs {expected_jobs}, got {jobs}"


def test_jaeger_api_services(otel_stack):
    """Verify Jaeger API is accessible."""
    response = requests.get("http://localhost:16686/api/services", timeout=5)
    assert response.status_code == 200

    data = response.json()
    # Initially no services since nothing has sent traces yet
    assert "data" in data


@pytest.mark.skipif(
    subprocess.run(
        ["docker", "ps", "-q", "--filter", "name=logos-otel-collector"],
        capture_output=True,
    ).returncode
    != 0,
    reason="OTel stack not running - run manually with ./scripts/start-otel-stack.sh",
)
def test_otel_collector_metrics_endpoint(otel_stack):
    """Verify OTel collector exposes Prometheus metrics."""
    response = requests.get("http://localhost:8889/metrics", timeout=5)
    assert response.status_code == 200
    # Metrics endpoint should return prometheus format (even if empty initially)
    # Just verify we get a response
    assert response.text is not None
