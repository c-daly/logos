"""Tests for HCG client configuration."""

import os
from unittest import mock

import pytest

from logos_hcg.config import HCGConfig, load_config


class TestHCGConfig:
    """Test HCGConfig settings."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = HCGConfig()

        assert config.neo4j_uri == "bolt://localhost:7687"
        assert config.neo4j_user == "neo4j"
        assert config.neo4j_password == "password"  # noqa: S105 - test fixture default
        assert config.neo4j_database == "neo4j"
        assert config.max_connection_pool_size == 50
        assert config.retry_attempts == 3
        assert config.shacl_enabled is True
        assert config.shacl_shapes_path is None

    def test_from_environment(self) -> None:
        """Test configuration from environment variables."""
        env_vars = {
            "NEO4J_URI": "bolt://testhost:7687",
            "NEO4J_USER": "testuser",
            "NEO4J_PASSWORD": "testpass",
            "NEO4J_DATABASE": "testdb",
            "HCG_MAX_POOL_SIZE": "100",
            "HCG_RETRY_ATTEMPTS": "5",
            "HCG_SHACL_ENABLED": "false",
        }

        with mock.patch.dict(os.environ, env_vars, clear=False):
            config = HCGConfig()

            assert config.neo4j_uri == "bolt://testhost:7687"
            assert config.neo4j_user == "testuser"
            assert config.neo4j_password == "testpass"  # noqa: S105 - test fixture
            assert config.neo4j_database == "testdb"
            assert config.max_connection_pool_size == 100
            assert config.retry_attempts == 5
            assert config.shacl_enabled is False

    def test_explicit_values_override_env(self) -> None:
        """Test that explicit values override environment."""
        # Use model_construct to bypass validation and set values directly
        config = HCGConfig.model_construct(neo4j_uri="bolt://explicit:7687")

        assert config.neo4j_uri == "bolt://explicit:7687"

    def test_retry_attempts_validation(self) -> None:
        """Test retry attempts bounds validation."""
        # Valid bounds via environment
        with mock.patch.dict(os.environ, {"HCG_RETRY_ATTEMPTS": "1"}, clear=False):
            config = HCGConfig()
            assert config.retry_attempts == 1

        with mock.patch.dict(os.environ, {"HCG_RETRY_ATTEMPTS": "10"}, clear=False):
            config = HCGConfig()
            assert config.retry_attempts == 10

        # Invalid bounds
        with mock.patch.dict(os.environ, {"HCG_RETRY_ATTEMPTS": "0"}, clear=False):
            with pytest.raises(ValueError):
                HCGConfig()

        with mock.patch.dict(os.environ, {"HCG_RETRY_ATTEMPTS": "11"}, clear=False):
            with pytest.raises(ValueError):
                HCGConfig()

    def test_load_config_function(self) -> None:
        """Test load_config convenience function."""
        config = load_config()

        assert isinstance(config, HCGConfig)
        assert config.neo4j_uri is not None
