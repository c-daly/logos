"""Helpers for interacting with Neo4j test instances."""

from __future__ import annotations

import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

from .docker import resolve_container_name, wait_for_container_health
from .env import get_env_value, load_stack_env


@dataclass(frozen=True)
class Neo4jConfig:
    uri: str
    user: str
    password: str
    container: str


def get_neo4j_config(env: Mapping[str, str] | None = None) -> Neo4jConfig:
    """Build a ``Neo4jConfig`` from environment sources."""

    values = env or load_stack_env()
    uri = (
        get_env_value("NEO4J_URI", values, "bolt://localhost:7687")
        or "bolt://localhost:7687"
    )
    user = get_env_value("NEO4J_USER", values, "neo4j") or "neo4j"
    password = get_env_value("NEO4J_PASSWORD", values, "neo4jtest") or "neo4jtest"
    container = resolve_container_name(
        "NEO4J_CONTAINER",
        "logos-phase2-test-neo4j",
        values,
    )
    return Neo4jConfig(uri=uri, user=user, password=password, container=container)


def get_neo4j_driver(config: Neo4jConfig | None = None):
    """Create a Neo4j driver for the configured instance."""

    cfg = config or get_neo4j_config()
    return GraphDatabase.driver(cfg.uri, auth=(cfg.user, cfg.password))


def is_neo4j_available(config: Neo4jConfig | None = None) -> bool:
    """Quick connectivity probe for Neo4j."""

    cfg = config or get_neo4j_config()
    try:
        driver = get_neo4j_driver(cfg)
        with driver.session() as session:
            session.run("RETURN 1 AS test").single()
        driver.close()
        return True
    except (ServiceUnavailable, OSError):
        return False


def _cypher_shell_command(config: Neo4jConfig) -> list[str]:
    return [
        "docker",
        "exec",
        "-i",
        config.container,
        "cypher-shell",
        "-u",
        config.user,
        "-p",
        config.password,
    ]


def run_cypher_query(
    query: str,
    config: Neo4jConfig | None = None,
    timeout: int = 30,
) -> subprocess.CompletedProcess[str]:
    """Execute a Cypher query via ``cypher-shell`` inside the container."""

    cfg = config or get_neo4j_config()
    return subprocess.run(  # noqa: S603,S607 (trusted input for test infra)
        _cypher_shell_command(cfg) + [query],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def load_cypher_file(
    file_path: str | Path,
    config: Neo4jConfig | None = None,
    timeout: int = 60,
) -> subprocess.CompletedProcess[str]:
    """Pipe the contents of a Cypher file into ``cypher-shell``."""

    cfg = config or get_neo4j_config()
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as cypher_file:
        return subprocess.run(  # noqa: S603,S607
            _cypher_shell_command(cfg),
            stdin=cypher_file,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )


def wait_for_neo4j(config: Neo4jConfig | None = None, timeout: int = 90) -> None:
    """Wait for the Neo4j container to report healthy and accept connections."""

    cfg = config or get_neo4j_config()
    wait_for_container_health(cfg.container, timeout=timeout)
    if not is_neo4j_available(cfg):
        raise RuntimeError(
            "Neo4j container reported healthy but Bolt endpoint is unreachable"
        )
