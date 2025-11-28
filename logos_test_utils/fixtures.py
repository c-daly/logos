"""Pytest fixtures that can be reused across LOGOS repos.

This module provides ready-to-use pytest fixtures for downstream repos
(apollo, hermes, sophia, talos) to consume when they adopt the standardized
test infrastructure.

Usage in downstream repos:
    1. Add logos_test_utils to dev dependencies in pyproject.toml:
       ```toml
       [tool.poetry.group.dev.dependencies]
       logos-test-utils = {path = "../logos", develop = true}
       ```

    2. Import fixtures in conftest.py:
       ```python
       from logos_test_utils.fixtures import (
           stack_env,
           neo4j_config,
           neo4j_driver,
           load_cypher,
       )
       ```

    3. Use fixtures in tests:
       ```python
       def test_something(neo4j_driver):
           with neo4j_driver.session() as session:
               result = session.run("RETURN 1 AS test")
               assert result.single()["test"] == 1
       ```

Note: The logos repo itself typically imports helper functions directly
(e.g., `get_neo4j_config()`) rather than using these fixtures, since its
tests pre-date fixture standardization. New tests should consider using
fixtures for consistency with downstream repos.

Available fixtures:
- stack_env: Parsed environment from .env.test
- neo4j_config: Neo4j connection configuration
- neo4j_driver: Connected Neo4j driver (session-scoped, auto-cleanup)
- load_cypher: Helper function to load .cypher files
"""

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
