"""Shared testing utilities for LOGOS repositories.

This package centralizes environment loading, container helpers, and
Neo4j/Milvus helpers so every repo consumes the same behaviour.
"""

from .config import ServiceConfig, get_env_value, normalize_host, resolve_service_config
from .docker import is_container_running, resolve_container_name, wait_for_container_health
from .env import load_stack_env
from .health import DependencyHealth, ServiceHealth
from .logging import HumanFormatter, StructuredFormatter, setup_logging
from .milvus import MilvusConfig, get_milvus_config, is_milvus_running, wait_for_milvus
from .neo4j import (
    Neo4jConfig,
    get_neo4j_config,
    get_neo4j_driver,
    is_neo4j_available,
    load_cypher_file,
    run_cypher_query,
    wait_for_neo4j,
)

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
