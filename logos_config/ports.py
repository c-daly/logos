"""Centralized port allocation for all LOGOS repos.

Convention: Each repo has an offset added to default service ports.
This allows CI jobs to run in parallel without port conflicts.

Priority (highest to lowest):
1. Environment variables (OS env or .env file)
2. Repo-specific offset defaults (computed from this module)
3. Base port defaults (raw service ports)

Port Offset Table:
| Repo   | Offset | Neo4j HTTP | Neo4j Bolt | Milvus gRPC | Milvus Metrics | API   |
|--------|--------|------------|------------|-------------|----------------|-------|
| hermes | +10000 | 17474      | 17687      | 29530       | 19091          | 18000 |
| apollo | +20000 | 27474      | 27687      | 39530       | 29091          | 28000 |
| logos  | +30000 | 37474      | 37687      | 49530       | 39091          | 38000 |
| sophia | +40000 | 47474      | 47687      | 59530       | 49091          | 48000 |
| talos  | +50000 | 57474      | 57687      | 69530       | 59091          | 58000 |
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from enum import IntEnum
from typing import NamedTuple


class RepoOffset(IntEnum):
    """Port offsets by repo (alphabetical order × 10000, hermes first)."""

    HERMES = 10000
    APOLLO = 20000
    LOGOS = 30000
    SOPHIA = 40000
    TALOS = 50000


class BasePorts(IntEnum):
    """Default service ports (no offset)."""

    NEO4J_HTTP = 7474
    NEO4J_BOLT = 7687
    MILVUS_GRPC = 19530
    MILVUS_METRICS = 9091
    API = 8000


class RepoPorts(NamedTuple):
    """Port configuration for a repo."""

    neo4j_http: int
    neo4j_bolt: int
    milvus_grpc: int
    milvus_metrics: int
    api: int


def get_repo_ports(
    repo: str,
    env: Mapping[str, str] | None = None,
) -> RepoPorts:
    """Get port configuration for a specific repo.

    Environment variables override computed defaults:
    - NEO4J_HTTP_PORT, NEO4J_BOLT_PORT
    - MILVUS_PORT, MILVUS_METRICS_PORT
    - API_PORT

    Args:
        repo: Repository name (hermes, apollo, logos, sophia, talos)
        env: Optional env dict (e.g., from .env file). OS env takes priority.

    Returns:
        RepoPorts with resolved port values
    """
    offset = RepoOffset[repo.upper()]

    def get_port(env_var: str, default: int) -> int:
        # Check OS env first, then provided mapping, then default
        if env_var in os.environ:
            return int(os.environ[env_var])
        if env and env_var in env:
            return int(env[env_var])
        return default

    return RepoPorts(
        neo4j_http=get_port("NEO4J_HTTP_PORT", BasePorts.NEO4J_HTTP + offset),
        neo4j_bolt=get_port("NEO4J_BOLT_PORT", BasePorts.NEO4J_BOLT + offset),
        milvus_grpc=get_port("MILVUS_PORT", BasePorts.MILVUS_GRPC + offset),
        milvus_metrics=get_port("MILVUS_METRICS_PORT", BasePorts.MILVUS_METRICS + offset),
        api=get_port("API_PORT", BasePorts.API + offset),
    )


# Pre-computed defaults (without env overrides) for reference/docs
# In actual usage, call get_repo_ports() to respect env vars
HERMES_PORTS = RepoPorts(17474, 17687, 29530, 19091, 18000)
APOLLO_PORTS = RepoPorts(27474, 27687, 39530, 29091, 28000)
LOGOS_PORTS = RepoPorts(37474, 37687, 49530, 39091, 38000)
SOPHIA_PORTS = RepoPorts(47474, 47687, 59530, 49091, 48000)
TALOS_PORTS = RepoPorts(57474, 57687, 69530, 59091, 58000)
