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


def wait_for_milvus(config: MilvusConfig | None = None, timeout: int = 90) -> None:
    cfg = config or get_milvus_config()
    wait_for_container_health(cfg.container, timeout=timeout)
