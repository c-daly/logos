"""Helpers for resolving container names used in integration tests."""

from __future__ import annotations

from collections.abc import Iterable
import os
import subprocess

DEFAULT_NEO4J_CANDIDATES: tuple[str, ...] = (
    "logos-phase2-test-neo4j",
    "logos-hcg-neo4j",
)
DEFAULT_MILVUS_CANDIDATES: tuple[str, ...] = (
    "logos-phase2-test-milvus",
    "logos-hcg-milvus",
)


def _docker_container_exists(name: str) -> bool:
    """Return True when ``docker ps`` reports a container with ``name``."""

    try:
        result = subprocess.run(  # noqa: S603,S607 - trusted test helper
            [
                "docker",
                "ps",
                "-a",
                "--filter",
                f"name=^{name}$",
                "--format",
                "{{.Names}}",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return False

    containers = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    return name in containers


def _resolve_container_name(
    env_var: str,
    candidates: Iterable[str],
) -> str:
    """Resolve a container name via environment override or discovery."""

    env_value = os.getenv(env_var)
    if env_value:
        return env_value

    check_candidates = tuple(candidates)
    for candidate in check_candidates:
        if _docker_container_exists(candidate):
            return candidate

    return check_candidates[0]


def resolve_neo4j_container() -> str:
    """Resolve the Neo4j container name for the local test stack."""

    return _resolve_container_name(
        env_var="NEO4J_CONTAINER",
        candidates=DEFAULT_NEO4J_CANDIDATES,
    )


def resolve_milvus_container() -> str:
    """Resolve the Milvus container name for the local test stack."""

    return _resolve_container_name(
        env_var="MILVUS_CONTAINER",
        candidates=DEFAULT_MILVUS_CANDIDATES,
    )
