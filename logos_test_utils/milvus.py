"""Milvus helpers for integration tests."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from logos_config import get_repo_ports

from .config import ServiceConfig, get_env_value, resolve_service_config
from .docker import (
    is_container_running,
    resolve_container_name,
    wait_for_container_health,
)


@dataclass(frozen=True)
class MilvusConfig:
    host: str
    port: int
    metrics_port: int
    healthcheck: str
    container: str


def get_milvus_config(
    env: Mapping[str, str] | None = None,
    repo: str = "logos",
) -> MilvusConfig:
    values = env or {}
    ports = get_repo_ports(repo, values)
    defaults = ServiceConfig(
        host="localhost",
        port=ports.milvus_grpc,
        url=f"http://localhost:{ports.milvus_grpc}",
    )
    service = resolve_service_config("MILVUS_HOST", "MILVUS_PORT", defaults, values)
    metrics_port = int(
        get_env_value("MILVUS_METRICS_PORT", values, str(ports.milvus_metrics))
        or ports.milvus_metrics
    )
    healthcheck = (
        get_env_value(
            "MILVUS_HEALTHCHECK",
            values,
            f"http://{service.host}:{metrics_port}/healthz",
        )
        or f"http://{service.host}:{metrics_port}/healthz"
    )
    container = resolve_container_name(
        "MILVUS_CONTAINER",
        "logos-phase2-test-milvus",
        values,
    )
    return MilvusConfig(
        host=service.host,
        port=service.port,
        metrics_port=metrics_port,
        healthcheck=healthcheck,
        container=container,
    )


def is_milvus_running(config: MilvusConfig | None = None) -> bool:
    cfg = config or get_milvus_config()
    return is_container_running(cfg.container)


def is_milvus_available(
    config: MilvusConfig | None = None, timeout: float = 2.0
) -> bool:
    """Quick connectivity probe for Milvus.

    Unlike :func:`is_milvus_running`, which introspects a local Docker
    container by name, this opens a real gRPC connection. Tests should gate on
    *reachability* of the service (which works in CI compose, the shared test
    stack, or a remote Milvus) rather than on a specific local container name.
    """

    cfg = config or get_milvus_config()
    try:
        from pymilvus import connections
    except ImportError:
        return False

    alias = "logos_test_utils_probe"
    try:
        # Bounded so an unreachable/black-holed Milvus fails the probe fast
        # instead of blocking test collection for pymilvus's ~20-30s default.
        connections.connect(
            alias=alias, host=cfg.host, port=str(cfg.port), timeout=timeout
        )
    except Exception:
        return False
    else:
        return True
    finally:
        try:
            connections.disconnect(alias)
        except Exception:
            pass


def wait_for_milvus(config: MilvusConfig | None = None, timeout: int = 90) -> None:
    cfg = config or get_milvus_config()
    wait_for_container_health(cfg.container, timeout=timeout)
