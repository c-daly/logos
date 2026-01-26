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
    RepoPorts,
    get_repo_ports,
)


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


class TestPortConsistency:
    """Tests that all ports for a repo share the same prefix."""

    @pytest.mark.parametrize(
        "ports,expected_prefix",
        [
            (HERMES_PORTS, 17),
            (APOLLO_PORTS, 27),
            (LOGOS_PORTS, 37),
            (SOPHIA_PORTS, 47),
            (TALOS_PORTS, 57),
        ],
    )
    def test_all_ports_share_prefix(
        self, ports: RepoPorts, expected_prefix: int
    ) -> None:
        """All ports for a repo should start with the same two-digit prefix."""
        for port in ports:
            prefix = port // 1000
            assert (
                prefix == expected_prefix
            ), f"Port {port} has prefix {prefix}, expected {expected_prefix}"


class TestGetRepoPorts:
    """Tests for get_repo_ports function."""

    def test_returns_hermes_ports(self) -> None:
        """get_repo_ports returns correct hermes ports."""
        for var in [
            "NEO4J_HTTP_PORT",
            "NEO4J_BOLT_PORT",
            "MILVUS_PORT",
            "MILVUS_METRICS_PORT",
            "API_PORT",
        ]:
            os.environ.pop(var, None)

        ports = get_repo_ports("hermes")
        assert ports == HERMES_PORTS

    def test_returns_apollo_ports(self) -> None:
        """get_repo_ports returns correct apollo ports."""
        for var in [
            "NEO4J_HTTP_PORT",
            "NEO4J_BOLT_PORT",
            "MILVUS_PORT",
            "MILVUS_METRICS_PORT",
            "API_PORT",
        ]:
            os.environ.pop(var, None)

        ports = get_repo_ports("apollo")
        assert ports == APOLLO_PORTS

    def test_returns_logos_ports(self) -> None:
        """get_repo_ports returns correct logos ports."""
        for var in [
            "NEO4J_HTTP_PORT",
            "NEO4J_BOLT_PORT",
            "MILVUS_PORT",
            "MILVUS_METRICS_PORT",
            "API_PORT",
        ]:
            os.environ.pop(var, None)

        ports = get_repo_ports("logos")
        assert ports == LOGOS_PORTS

    def test_returns_sophia_ports(self) -> None:
        """get_repo_ports returns correct sophia ports."""
        for var in [
            "NEO4J_HTTP_PORT",
            "NEO4J_BOLT_PORT",
            "MILVUS_PORT",
            "MILVUS_METRICS_PORT",
            "API_PORT",
        ]:
            os.environ.pop(var, None)

        ports = get_repo_ports("sophia")
        assert ports == SOPHIA_PORTS

    def test_returns_talos_ports(self) -> None:
        """get_repo_ports returns correct talos ports."""
        for var in [
            "NEO4J_HTTP_PORT",
            "NEO4J_BOLT_PORT",
            "MILVUS_PORT",
            "MILVUS_METRICS_PORT",
            "API_PORT",
        ]:
            os.environ.pop(var, None)

        ports = get_repo_ports("talos")
        assert ports == TALOS_PORTS

    def test_case_insensitive(self) -> None:
        """Repo name is case-insensitive."""
        for var in [
            "NEO4J_HTTP_PORT",
            "NEO4J_BOLT_PORT",
            "MILVUS_PORT",
            "MILVUS_METRICS_PORT",
            "API_PORT",
        ]:
            os.environ.pop(var, None)

        assert get_repo_ports("HERMES") == get_repo_ports("hermes")
        assert get_repo_ports("Apollo") == get_repo_ports("apollo")

    def test_env_var_override(self) -> None:
        """Environment variables override defaults."""
        with mock.patch.dict(os.environ, {"MILVUS_PORT": "12345"}):
            ports = get_repo_ports("hermes")
            assert ports.milvus_grpc == 12345
            # Others should still be defaults
            assert ports.neo4j_http == HERMES_PORTS.neo4j_http

    def test_env_mapping_override(self) -> None:
        """Provided env mapping overrides defaults."""
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
        """HERMES_PORTS has consistent 17xxx prefix."""
        assert HERMES_PORTS == RepoPorts(17474, 17687, 17530, 17091, 17000)

    def test_apollo_ports(self) -> None:
        """APOLLO_PORTS has consistent 27xxx prefix."""
        assert APOLLO_PORTS == RepoPorts(27474, 27687, 27530, 27091, 27000)

    def test_logos_ports(self) -> None:
        """LOGOS_PORTS has consistent 37xxx prefix."""
        assert LOGOS_PORTS == RepoPorts(37474, 37687, 37530, 37091, 37000)

    def test_sophia_ports(self) -> None:
        """SOPHIA_PORTS has consistent 47xxx prefix."""
        assert SOPHIA_PORTS == RepoPorts(47474, 47687, 47530, 47091, 47000)

    def test_talos_ports(self) -> None:
        """TALOS_PORTS has consistent 57xxx prefix."""
        assert TALOS_PORTS == RepoPorts(57474, 57687, 57530, 57091, 57000)
