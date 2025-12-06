"""Tests for logos_config.ports module."""

from __future__ import annotations

import os
from unittest import mock

import pytest

from logos_config.ports import (
    APOLLO_PORTS,
    HERMES_PORTS,
    LOGOS_PORTS,
    SOPHIA_PORTS,
    TALOS_PORTS,
    BasePorts,
    RepoOffset,
    RepoPorts,
    get_repo_ports,
)


class TestBasePorts:
    """Tests for BasePorts enum."""

    def test_neo4j_defaults(self) -> None:
        """Neo4j ports match official defaults."""
        assert BasePorts.NEO4J_HTTP == 7474
        assert BasePorts.NEO4J_BOLT == 7687

    def test_milvus_defaults(self) -> None:
        """Milvus ports match official defaults."""
        assert BasePorts.MILVUS_GRPC == 19530
        assert BasePorts.MILVUS_METRICS == 9091

    def test_api_default(self) -> None:
        """API port matches FastAPI/Uvicorn default."""
        assert BasePorts.API == 8000


class TestRepoOffset:
    """Tests for RepoOffset enum."""

    def test_offsets_are_multiples_of_10000(self) -> None:
        """Each offset is a multiple of 10000."""
        for offset in RepoOffset:
            assert offset % 10000 == 0

    def test_offsets_are_unique(self) -> None:
        """Each repo has a unique offset."""
        offsets = [offset.value for offset in RepoOffset]
        assert len(offsets) == len(set(offsets))

    def test_offset_values(self) -> None:
        """Verify specific offset values."""
        assert RepoOffset.HERMES == 10000
        assert RepoOffset.APOLLO == 20000
        assert RepoOffset.LOGOS == 30000
        assert RepoOffset.SOPHIA == 40000
        assert RepoOffset.TALOS == 50000


class TestRepoPorts:
    """Tests for RepoPorts named tuple."""

    def test_is_named_tuple(self) -> None:
        """RepoPorts is a NamedTuple with correct fields."""
        ports = RepoPorts(1, 2, 3, 4, 5)
        assert ports.neo4j_http == 1
        assert ports.neo4j_bolt == 2
        assert ports.milvus_grpc == 3
        assert ports.milvus_metrics == 4
        assert ports.api == 5


class TestGetRepoPorts:
    """Tests for get_repo_ports function."""

    def test_computes_hermes_offset(self) -> None:
        """Hermes ports have +10000 offset."""
        # Clear any env vars that might interfere
        for var in ["NEO4J_HTTP_PORT", "NEO4J_BOLT_PORT", "MILVUS_PORT", "MILVUS_METRICS_PORT", "API_PORT"]:
            os.environ.pop(var, None)

        ports = get_repo_ports("hermes")
        assert ports.neo4j_http == 17474
        assert ports.neo4j_bolt == 17687
        assert ports.milvus_grpc == 29530
        assert ports.milvus_metrics == 19091
        assert ports.api == 18000

    def test_computes_apollo_offset(self) -> None:
        """Apollo ports have +20000 offset."""
        for var in ["NEO4J_HTTP_PORT", "NEO4J_BOLT_PORT", "MILVUS_PORT", "MILVUS_METRICS_PORT", "API_PORT"]:
            os.environ.pop(var, None)

        ports = get_repo_ports("apollo")
        assert ports.neo4j_http == 27474
        assert ports.neo4j_bolt == 27687
        assert ports.milvus_grpc == 39530
        assert ports.milvus_metrics == 29091
        assert ports.api == 28000

    def test_computes_logos_offset(self) -> None:
        """Logos ports have +30000 offset."""
        for var in ["NEO4J_HTTP_PORT", "NEO4J_BOLT_PORT", "MILVUS_PORT", "MILVUS_METRICS_PORT", "API_PORT"]:
            os.environ.pop(var, None)

        ports = get_repo_ports("logos")
        assert ports.neo4j_http == 37474
        assert ports.neo4j_bolt == 37687
        assert ports.milvus_grpc == 49530
        assert ports.milvus_metrics == 39091
        assert ports.api == 38000

    def test_computes_sophia_offset(self) -> None:
        """Sophia ports have +40000 offset."""
        for var in ["NEO4J_HTTP_PORT", "NEO4J_BOLT_PORT", "MILVUS_PORT", "MILVUS_METRICS_PORT", "API_PORT"]:
            os.environ.pop(var, None)

        ports = get_repo_ports("sophia")
        assert ports.neo4j_http == 47474
        assert ports.neo4j_bolt == 47687
        assert ports.milvus_grpc == 59530
        assert ports.milvus_metrics == 49091
        assert ports.api == 48000

    def test_computes_talos_offset(self) -> None:
        """Talos ports have +50000 offset."""
        for var in ["NEO4J_HTTP_PORT", "NEO4J_BOLT_PORT", "MILVUS_PORT", "MILVUS_METRICS_PORT", "API_PORT"]:
            os.environ.pop(var, None)

        ports = get_repo_ports("talos")
        assert ports.neo4j_http == 57474
        assert ports.neo4j_bolt == 57687
        assert ports.milvus_grpc == 69530
        assert ports.milvus_metrics == 59091
        assert ports.api == 58000

    def test_case_insensitive(self) -> None:
        """Repo name is case-insensitive."""
        for var in ["NEO4J_HTTP_PORT", "NEO4J_BOLT_PORT", "MILVUS_PORT", "MILVUS_METRICS_PORT", "API_PORT"]:
            os.environ.pop(var, None)

        assert get_repo_ports("HERMES") == get_repo_ports("hermes")
        assert get_repo_ports("Apollo") == get_repo_ports("apollo")

    def test_env_var_override(self) -> None:
        """Environment variables override computed defaults."""
        with mock.patch.dict(os.environ, {"MILVUS_PORT": "12345"}):
            ports = get_repo_ports("hermes")
            assert ports.milvus_grpc == 12345
            # Others should still be computed
            assert ports.neo4j_http == 17474

    def test_env_mapping_override(self) -> None:
        """Provided env mapping overrides computed defaults."""
        # Clear OS env
        os.environ.pop("NEO4J_HTTP_PORT", None)

        ports = get_repo_ports("hermes", env={"NEO4J_HTTP_PORT": "9999"})
        assert ports.neo4j_http == 9999

    def test_os_env_takes_priority_over_mapping(self) -> None:
        """OS env takes priority over provided mapping."""
        with mock.patch.dict(os.environ, {"MILVUS_PORT": "11111"}):
            ports = get_repo_ports("hermes", env={"MILVUS_PORT": "22222"})
            # OS env should win
            assert ports.milvus_grpc == 11111

    def test_invalid_repo_raises(self) -> None:
        """Invalid repo name raises KeyError."""
        with pytest.raises(KeyError):
            get_repo_ports("invalid_repo")


class TestPrecomputedPorts:
    """Tests for pre-computed port constants."""

    def test_hermes_ports(self) -> None:
        """HERMES_PORTS matches expected values."""
        assert HERMES_PORTS == RepoPorts(17474, 17687, 29530, 19091, 18000)

    def test_apollo_ports(self) -> None:
        """APOLLO_PORTS matches expected values."""
        assert APOLLO_PORTS == RepoPorts(27474, 27687, 39530, 29091, 28000)

    def test_logos_ports(self) -> None:
        """LOGOS_PORTS matches expected values."""
        assert LOGOS_PORTS == RepoPorts(37474, 37687, 49530, 39091, 38000)

    def test_sophia_ports(self) -> None:
        """SOPHIA_PORTS matches expected values."""
        assert SOPHIA_PORTS == RepoPorts(47474, 47687, 59530, 49091, 48000)

    def test_talos_ports(self) -> None:
        """TALOS_PORTS matches expected values."""
        assert TALOS_PORTS == RepoPorts(57474, 57687, 69530, 59091, 58000)
