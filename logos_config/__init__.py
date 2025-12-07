"""logos_config - Shared configuration utilities for LOGOS repos.

This package provides centralized configuration helpers used across
all LOGOS repositories (apollo, hermes, logos, sophia, talos).

Modules:
    env: Environment variable resolution and .env file loading
    ports: Centralized port allocation with consistent offsets
    settings: Pydantic configuration models for common services
    health: Unified health response schema
"""

from logos_config.env import get_env_value, get_repo_root, load_env_file
from logos_config.ports import (
    APOLLO_PORTS,
    HERMES_PORTS,
    LOGOS_PORTS,
    SOPHIA_PORTS,
    TALOS_PORTS,
    RepoPorts,
    get_repo_ports,
)
from logos_config.settings import MilvusConfig, Neo4jConfig, ServiceConfig

__all__ = [
    # env
    "get_env_value",
    "get_repo_root",
    "load_env_file",
    # ports
    "RepoPorts",
    "get_repo_ports",
    "HERMES_PORTS",
    "APOLLO_PORTS",
    "LOGOS_PORTS",
    "SOPHIA_PORTS",
    "TALOS_PORTS",
    # settings
    "Neo4jConfig",
    "MilvusConfig",
    "ServiceConfig",
]

__version__ = "0.1.0"
