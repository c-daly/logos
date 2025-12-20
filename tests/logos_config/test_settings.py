"""Tests for logos_config.settings module."""

from __future__ import annotations

import os
from unittest import mock

import pytest
from pydantic import ValidationError

from logos_config.settings import MilvusConfig, Neo4jConfig, ServiceConfig


class TestNeo4jConfig:
    """Tests for Neo4jConfig."""

    def test_default_values(self) -> None:
        """Default values are set correctly."""
        # Clear env vars that might interfere
        for var in [
            "NEO4J_HOST",
            "NEO4J_HTTP_PORT",
            "NEO4J_BOLT_PORT",
            "NEO4J_USER",
            "NEO4J_PASSWORD",
        ]:
            os.environ.pop(var, None)

        config = Neo4jConfig(password="secret")
        assert config.host == "localhost"
        assert config.http_port == 7474
        assert config.bolt_port == 7687
        assert config.user == "neo4j"
        assert config.password == "secret"

    def test_uri_property(self) -> None:
        """URI property returns correct bolt:// connection string."""
        for var in ["NEO4J_HOST", "NEO4J_BOLT_PORT"]:
            os.environ.pop(var, None)

        config = Neo4jConfig(password="secret")
        assert config.uri == "bolt://localhost:7687"

        config = Neo4jConfig(host="neo4j-server", bolt_port=7688, password="secret")
        assert config.uri == "bolt://neo4j-server:7688"

    def test_http_url_property(self) -> None:
        """HTTP URL property returns correct http:// URL."""
        for var in ["NEO4J_HOST", "NEO4J_HTTP_PORT"]:
            os.environ.pop(var, None)

        config = Neo4jConfig(password="secret")
        assert config.http_url == "http://localhost:7474"

    def test_password_required(self) -> None:
        """Password is required - no default."""
        for var in [
            "NEO4J_HOST",
            "NEO4J_HTTP_PORT",
            "NEO4J_BOLT_PORT",
            "NEO4J_USER",
            "NEO4J_PASSWORD",
        ]:
            os.environ.pop(var, None)

        with pytest.raises(ValidationError):
            Neo4jConfig()  # type: ignore[call-arg]

    def test_env_var_override(self) -> None:
        """Environment variables override defaults."""
        with mock.patch.dict(
            os.environ,
            {
                "NEO4J_HOST": "custom-host",
                "NEO4J_BOLT_PORT": "7777",
                "NEO4J_PASSWORD": "env-password",
            },
        ):
            config = Neo4jConfig()  # type: ignore[call-arg]
            assert config.host == "custom-host"
            assert config.bolt_port == 7777
            assert config.password == "env-password"


class TestMilvusConfig:
    """Tests for MilvusConfig."""

    def test_default_values(self) -> None:
        """Default values are set correctly."""
        for var in ["MILVUS_HOST", "MILVUS_PORT", "MILVUS_COLLECTION_NAME"]:
            os.environ.pop(var, None)

        config = MilvusConfig()
        assert config.host == "localhost"
        assert config.port == 19530
        assert config.collection_name == "embeddings"

    def test_env_var_override(self) -> None:
        """Environment variables override defaults."""
        with mock.patch.dict(
            os.environ,
            {
                "MILVUS_HOST": "milvus-server",
                "MILVUS_PORT": "37530",
                "MILVUS_COLLECTION_NAME": "my_embeddings",
            },
        ):
            config = MilvusConfig()
            assert config.host == "milvus-server"
            assert config.port == 37530
            assert config.collection_name == "my_embeddings"


class TestServiceConfig:
    """Tests for ServiceConfig."""

    def test_port_required(self) -> None:
        """Port is required - no default."""
        for var in ["SERVICE_HOST", "SERVICE_PORT", "SERVICE_API_KEY"]:
            os.environ.pop(var, None)

        with pytest.raises(ValidationError):
            ServiceConfig()  # type: ignore[call-arg]

    def test_with_port(self) -> None:
        """Works when port is provided."""
        for var in ["SERVICE_HOST", "SERVICE_PORT", "SERVICE_API_KEY"]:
            os.environ.pop(var, None)

        config = ServiceConfig(port=8080)
        assert config.host == "localhost"
        assert config.port == 8080
        assert config.api_key is None

    def test_api_key_optional(self) -> None:
        """API key is optional."""
        for var in ["SERVICE_HOST", "SERVICE_PORT", "SERVICE_API_KEY"]:
            os.environ.pop(var, None)

        config = ServiceConfig(port=8080, api_key="my-key")
        assert config.api_key == "my-key"

    def test_env_var_override(self) -> None:
        """Environment variables override defaults."""
        with mock.patch.dict(
            os.environ,
            {
                "SERVICE_HOST": "custom-host",
                "SERVICE_PORT": "9000",
                "SERVICE_API_KEY": "secret-key",
            },
        ):
            config = ServiceConfig()  # type: ignore[call-arg]
            assert config.host == "custom-host"
            assert config.port == 9000
            assert config.api_key == "secret-key"
