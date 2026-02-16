"""Centralized port allocation for all LOGOS repos.

Infrastructure services (Neo4j, Milvus) run on standard ports and are
shared across repos. Each repo gets a unique API port.

Port Table:
Infrastructure ports (Neo4j, Milvus) use standard defaults — all repos
share a single set of infrastructure services.  Only API ports are
repo-specific.

| Repo   | Neo4j HTTP | Neo4j Bolt | Milvus gRPC | Milvus Metrics | API   |
|--------|------------|------------|-------------|----------------|-------|
| hermes | 7474       | 7687       | 19530       | 9091           | 17000 |
| apollo | 7474       | 7687       | 19530       | 9091           | 27000 |
| logos  | 7474       | 7687       | 19530       | 9091           | 37000 |
| sophia | 7474       | 7687       | 19530       | 9091           | 47000 |
| talos  | 7474       | 7687       | 19530       | 9091           | 57000 |
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import NamedTuple


class RepoPorts(NamedTuple):
    """Port configuration for a repo."""

    neo4j_http: int
    neo4j_bolt: int
    milvus_grpc: int
    milvus_metrics: int
    api: int


# Shared infra ports + repo-specific API ports
HERMES_PORTS = RepoPorts(7474, 7687, 19530, 9091, 17000)
APOLLO_PORTS = RepoPorts(7474, 7687, 19530, 9091, 27000)
LOGOS_PORTS = RepoPorts(7474, 7687, 19530, 9091, 37000)
SOPHIA_PORTS = RepoPorts(7474, 7687, 19530, 9091, 47000)
TALOS_PORTS = RepoPorts(7474, 7687, 19530, 9091, 57000)

_REPO_PORTS = {
    "hermes": HERMES_PORTS,
    "apollo": APOLLO_PORTS,
    "logos": LOGOS_PORTS,
    "sophia": SOPHIA_PORTS,
    "talos": TALOS_PORTS,
}


def get_repo_ports(
    repo: str,
    env: Mapping[str, str] | None = None,
) -> RepoPorts:
    """Get port configuration for a specific repo.

    Environment variables override defaults:
    - NEO4J_HTTP_PORT, NEO4J_BOLT_PORT
    - MILVUS_PORT, MILVUS_METRICS_PORT
    - API_PORT

    Args:
        repo: Repository name (hermes, apollo, logos, sophia, talos)
        env: Optional env dict (e.g., from .env file). OS env takes priority.

    Returns:
        RepoPorts with resolved port values
    """
    defaults = _REPO_PORTS[repo.lower()]

    def get_port(env_var: str, default: int) -> int:
        if env_var in os.environ:
            return int(os.environ[env_var])
        if env and env_var in env:
            return int(env[env_var])
        return default

    return RepoPorts(
        neo4j_http=get_port("NEO4J_HTTP_PORT", defaults.neo4j_http),
        neo4j_bolt=get_port("NEO4J_BOLT_PORT", defaults.neo4j_bolt),
        milvus_grpc=get_port("MILVUS_PORT", defaults.milvus_grpc),
        milvus_metrics=get_port("MILVUS_METRICS_PORT", defaults.milvus_metrics),
        api=get_port("API_PORT", defaults.api),
    )
