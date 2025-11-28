"""Pytest fixtures that can be reused across LOGOS repos."""

from __future__ import annotations

from pathlib import Path

import pytest

from .env import load_stack_env
from .neo4j import (
    Neo4jConfig,
    get_neo4j_config,
    get_neo4j_driver,
    load_cypher_file,
    wait_for_neo4j,
)


@pytest.fixture(scope="session")
def stack_env() -> dict[str, str]:
    """Expose the parsed stack environment for other fixtures."""

    return load_stack_env()


@pytest.fixture(scope="session")
def neo4j_config(stack_env: dict[str, str]) -> Neo4jConfig:
    """Return the resolved Neo4j configuration."""

    return get_neo4j_config(stack_env)


@pytest.fixture(scope="session")
def neo4j_driver(neo4j_config: Neo4jConfig):
    """Provide a shared Neo4j driver for tests that need one."""

    wait_for_neo4j(neo4j_config)
    driver = get_neo4j_driver(neo4j_config)
    yield driver
    driver.close()


@pytest.fixture(scope="session")
def load_cypher(neo4j_config: Neo4jConfig):
    """Helper fixture that loads arbitrary Cypher files into Neo4j."""

    def _loader(path: str | Path, timeout: int = 60):
        return load_cypher_file(path, config=neo4j_config, timeout=timeout)

    return _loader
