"""Shared testing utilities for LOGOS repositories.

This package centralizes environment loading, container helpers, and
Neo4j/Milvus helpers so every repo consumes the same behaviour.

Neo4j and Milvus imports are lazy to avoid requiring those dependencies
for repos that only need logging/config utilities.
"""

from .config import ServiceConfig, get_env_value, normalize_host, resolve_service_config
from .docker import is_container_running, resolve_container_name, wait_for_container_health
from .env import load_stack_env
from .health import DependencyHealth, ServiceHealth
from .logging import HumanFormatter, StructuredFormatter, setup_logging

# Lazy imports for neo4j/milvus - only load when accessed
_neo4j_names = {
    "Neo4jConfig",
    "get_neo4j_config",
    "get_neo4j_driver",
    "is_neo4j_available",
    "load_cypher_file",
    "run_cypher_query",
    "wait_for_neo4j",
}
_milvus_names = {
    "MilvusConfig",
    "get_milvus_config",
    "is_milvus_running",
    "wait_for_milvus",
}


def __getattr__(name: str):
    """Lazy import neo4j/milvus modules only when accessed."""
    if name in _neo4j_names:
        from . import neo4j as _neo4j
        return getattr(_neo4j, name)
    if name in _milvus_names:
        from . import milvus as _milvus
        return getattr(_milvus, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "DependencyHealth",
    "HumanFormatter",
    "MilvusConfig",
    "Neo4jConfig",
    "ServiceConfig",
    "ServiceHealth",
    "StructuredFormatter",
    "get_env_value",
    "get_milvus_config",
    "get_neo4j_config",
    "get_neo4j_driver",
    "is_container_running",
    "is_milvus_running",
    "is_neo4j_available",
    "load_cypher_file",
    "load_stack_env",
    "normalize_host",
    "resolve_container_name",
    "resolve_service_config",
    "run_cypher_query",
    "setup_logging",
    "wait_for_container_health",
    "wait_for_milvus",
    "wait_for_neo4j",
]
