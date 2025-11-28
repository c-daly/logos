"""Milvus helpers for integration tests."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .docker import (
    is_container_running,
    resolve_container_name,
    wait_for_container_health,
)
from .env import get_env_value, load_stack_env


@dataclass(frozen=True)
class MilvusConfig:
    host: str
    port: str
    container: str


def get_milvus_config(env: Mapping[str, str] | None = None) -> MilvusConfig:
    values = env or load_stack_env()
    host = get_env_value("MILVUS_HOST", values, "milvus")
    port = get_env_value("MILVUS_PORT", values, "19530")
    container = resolve_container_name(
        "MILVUS_CONTAINER",
        "logos-phase2-test-milvus",
        values,
    )
    return MilvusConfig(host=host, port=port, container=container)


def is_milvus_running(config: MilvusConfig | None = None) -> bool:
    cfg = config or get_milvus_config()
    return is_container_running(cfg.container)


def wait_for_milvus(config: MilvusConfig | None = None, timeout: int = 90) -> None:
    cfg = config or get_milvus_config()
    wait_for_container_health(cfg.container, timeout=timeout)
