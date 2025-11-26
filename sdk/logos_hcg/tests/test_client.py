"""Tests for HCG client."""

import os
from datetime import datetime
from typing import Any
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest

from logos_hcg import HCGClient, HCGConfig
from logos_hcg.exceptions import (
    HCGConnectionError,
    HCGNotFoundError,
    HCGQueryError,
    HCGValidationError,
)


class MockNeo4jNode:
    """Mock Neo4j Node that properly supports dict() conversion.

    This test helper mimics the Neo4j Node interface which uses dynamic types.
    """

    def __init__(
        self, data: dict[str, Any], labels: list[str], node_id: int = 1
    ) -> None:
        self._data = data
        self.labels = labels
        self.id = node_id

    def __iter__(self):  # noqa: ANN204
        return iter(self._data)

    def __getitem__(self, key: str) -> Any:  # noqa: ANN401
        return self._data[key]

    def keys(self):  # noqa: ANN201
        return self._data.keys()

    def get(self, key: str, default: Any = None) -> Any:  # noqa: ANN401
        return self._data.get(key, default)


class TestHCGClientInit:
    """Test HCGClient initialization."""

    def test_default_config(self) -> None:
        """Test client with default config."""
        client = HCGClient()

        assert client.config is not None
        assert client.config.neo4j_uri == "bolt://localhost:7687"
        assert client._validator is not None  # SHACL enabled by default

    def test_custom_config(self) -> None:
        """Test client with custom config."""
        with mock.patch.dict(
            os.environ,
            {"NEO4J_URI": "bolt://custom:7687", "HCG_SHACL_ENABLED": "false"},
            clear=False,
        ):
            config = HCGConfig()
            client = HCGClient(config)

            assert client.config.neo4j_uri == "bolt://custom:7687"
            assert client._validator is None  # SHACL disabled

    def test_custom_validator(self) -> None:
        """Test client with custom validator."""
        from logos_hcg.validation import SHACLValidator

        custom_validator = SHACLValidator()
        client = HCGClient(validator=custom_validator)

        assert client._validator is custom_validator


class TestHCGClientConnection:
    """Test HCGClient connection management."""

    @patch("logos_hcg.client.GraphDatabase")
    def test_connect_success(self, mock_gdb: MagicMock) -> None:
        """Test successful connection."""
        mock_driver = MagicMock()
        mock_gdb.driver.return_value = mock_driver

        client = HCGClient()
        client.connect()

        mock_gdb.driver.assert_called_once()
        mock_driver.verify_connectivity.assert_called_once()

    @patch("logos_hcg.client.GraphDatabase")
    def test_connect_failure(self, mock_gdb: MagicMock) -> None:
        """Test connection failure raises exception."""
        mock_gdb.driver.side_effect = Exception("Connection refused")

        client = HCGClient()

        with pytest.raises(HCGConnectionError):
            client.connect()

    @patch("logos_hcg.client.GraphDatabase")
    def test_context_manager(self, mock_gdb: MagicMock) -> None:
        """Test context manager connects and closes."""
        mock_driver = MagicMock()
        mock_gdb.driver.return_value = mock_driver

        with HCGClient() as client:
            assert client._driver is not None

        mock_driver.close.assert_called_once()

    @patch("logos_hcg.client.GraphDatabase")
    def test_close(self, mock_gdb: MagicMock) -> None:
        """Test close disconnects driver."""
        mock_driver = MagicMock()
        mock_gdb.driver.return_value = mock_driver

        client = HCGClient()
        client.connect()
        client.close()

        mock_driver.close.assert_called_once()
        assert client._driver is None


class TestHCGClientTypeConversion:
    """Test type conversion utilities."""

    def test_convert_value_none(self) -> None:
        """Test converting None."""
        client = HCGClient()
        assert client._convert_value(None) is None

    def test_convert_value_native(self) -> None:
        """Test converting Neo4j native types."""
        client = HCGClient()

        mock_value = MagicMock()
        mock_value.to_native.return_value = "native_value"

        result = client._convert_value(mock_value)
        assert result == "native_value"

    def test_convert_value_bytes(self) -> None:
        """Test converting bytes."""
        client = HCGClient()

        result = client._convert_value(b"hello")
        assert result == "hello"

    def test_convert_value_datetime_string(self) -> None:
        """Test converting ISO datetime string."""
        client = HCGClient()

        result = client._convert_value("2024-01-15T10:30:00")
        assert isinstance(result, datetime)

    def test_parse_json_field(self) -> None:
        """Test parsing JSON fields."""
        client = HCGClient()

        # Valid JSON string
        result = client._parse_json_field('{"key": "value"}')
        assert result == {"key": "value"}

        # Invalid JSON returns default
        result = client._parse_json_field("not json", default={})
        assert result == {}

        # Non-string passes through
        result = client._parse_json_field({"already": "dict"})
        assert result == {"already": "dict"}

    def test_sanitize_props(self) -> None:
        """Test sanitizing property dictionaries."""
        client = HCGClient()

        props = {
            "simple": "value",
            "nested": {"inner": "value"},
            "list": [1, 2, 3],
        }

        result = client._sanitize_props(props)

        assert result["simple"] == "value"
        assert result["nested"]["inner"] == "value"
        assert result["list"] == [1, 2, 3]


class TestHCGClientReadOperations:
    """Test read operations."""

    @patch("logos_hcg.client.GraphDatabase")
    def test_get_entities(self, mock_gdb: MagicMock) -> None:
        """Test getting entities."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        mock_node = MockNeo4jNode({"id": "entity_123", "type": "test"}, ["Entity"], 1)

        mock_result.__iter__ = lambda self: iter([{"n": mock_node}])
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__ = lambda self: mock_session
        mock_driver.session.return_value.__exit__ = lambda *args: None
        mock_gdb.driver.return_value = mock_driver

        with HCGClient() as client:
            entities = client.get_entities(entity_type="test", limit=10)

        assert len(entities) == 1
        assert entities[0].id == "entity_123"

    @patch("logos_hcg.client.GraphDatabase")
    def test_get_entity_by_id_found(self, mock_gdb: MagicMock) -> None:
        """Test getting entity by ID when found."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        mock_node = MockNeo4jNode({"id": "entity_123", "type": "test"}, ["Entity"], 1)

        mock_result.single.return_value = {"n": mock_node}
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__ = lambda self: mock_session
        mock_driver.session.return_value.__exit__ = lambda *args: None
        mock_gdb.driver.return_value = mock_driver

        with HCGClient() as client:
            entity = client.get_entity_by_id("entity_123")

        assert entity is not None
        assert entity.id == "entity_123"

    @patch("logos_hcg.client.GraphDatabase")
    def test_get_entity_by_id_not_found(self, mock_gdb: MagicMock) -> None:
        """Test getting entity by ID when not found."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        mock_result.single.return_value = None
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__ = lambda self: mock_session
        mock_driver.session.return_value.__exit__ = lambda *args: None
        mock_gdb.driver.return_value = mock_driver

        with HCGClient() as client:
            entity = client.get_entity_by_id("nonexistent")

        assert entity is None

    @patch("logos_hcg.client.GraphDatabase")
    def test_health_check_success(self, mock_gdb: MagicMock) -> None:
        """Test successful health check."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        mock_result.single.return_value = {"health": 1}
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__ = lambda self: mock_session
        mock_driver.session.return_value.__exit__ = lambda *args: None
        mock_gdb.driver.return_value = mock_driver

        with HCGClient() as client:
            healthy = client.health_check()

        assert healthy is True

    @patch("logos_hcg.client.GraphDatabase")
    def test_health_check_failure(self, mock_gdb: MagicMock) -> None:
        """Test failed health check."""
        mock_driver = MagicMock()
        mock_session = MagicMock()

        mock_session.run.side_effect = Exception("Connection lost")
        mock_driver.session.return_value.__enter__ = lambda self: mock_session
        mock_driver.session.return_value.__exit__ = lambda *args: None
        mock_gdb.driver.return_value = mock_driver

        with HCGClient() as client:
            healthy = client.health_check()

        assert healthy is False


class TestHCGClientWriteOperations:
    """Test write operations."""

    @patch("logos_hcg.client.GraphDatabase")
    def test_create_entity_success(self, mock_gdb: MagicMock) -> None:
        """Test successful entity creation."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        mock_result.single.return_value = {"id": "entity_abc123"}
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__ = lambda self: mock_session
        mock_driver.session.return_value.__exit__ = lambda *args: None
        mock_gdb.driver.return_value = mock_driver

        config = HCGConfig(shacl_enabled=False)
        with HCGClient(config) as client:
            entity_id = client.create_entity(
                entity_type="manipulator",
                properties={"name": "gripper"},
            )

        assert "entity" in entity_id or entity_id == "entity_abc123"
        mock_session.run.assert_called_once()

    @patch("logos_hcg.client.GraphDatabase")
    def test_create_entity_with_validation(self, mock_gdb: MagicMock) -> None:
        """Test entity creation with SHACL validation."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        mock_result.single.return_value = {"id": "entity_abc123"}
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__ = lambda self: mock_session
        mock_driver.session.return_value.__exit__ = lambda *args: None
        mock_gdb.driver.return_value = mock_driver

        # SHACL enabled by default
        with HCGClient() as client:
            entity_id = client.create_entity(
                entity_type="manipulator",
                properties={"name": "gripper"},
            )

        assert entity_id is not None

    @patch("logos_hcg.client.GraphDatabase")
    def test_update_entity(self, mock_gdb: MagicMock) -> None:
        """Test entity update."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        mock_result.single.return_value = {"updated": 1}
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__ = lambda self: mock_session
        mock_driver.session.return_value.__exit__ = lambda *args: None
        mock_gdb.driver.return_value = mock_driver

        config = HCGConfig(shacl_enabled=False)
        with HCGClient(config) as client:
            updated = client.update_entity(
                entity_id="entity_123",
                properties={"status": "active"},
            )

        assert updated is True

    @patch("logos_hcg.client.GraphDatabase")
    def test_delete_entity(self, mock_gdb: MagicMock) -> None:
        """Test entity deletion."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        mock_result.single.return_value = {"deleted": 1}
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__ = lambda self: mock_session
        mock_driver.session.return_value.__exit__ = lambda *args: None
        mock_gdb.driver.return_value = mock_driver

        config = HCGConfig(shacl_enabled=False)
        with HCGClient(config) as client:
            deleted = client.delete_entity("entity_123")

        assert deleted is True

    @patch("logos_hcg.client.GraphDatabase")
    def test_add_relationship_success(self, mock_gdb: MagicMock) -> None:
        """Test successful relationship creation."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        mock_result.single.return_value = {"id": "edge_abc123"}
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__ = lambda self: mock_session
        mock_driver.session.return_value.__exit__ = lambda *args: None
        mock_gdb.driver.return_value = mock_driver

        config = HCGConfig(shacl_enabled=False)
        with HCGClient(config) as client:
            edge_id = client.add_relationship(
                source_id="entity_a",
                target_id="entity_b",
                relation_type="HAS_STATE",
            )

        assert edge_id is not None

    @patch("logos_hcg.client.GraphDatabase")
    def test_add_relationship_not_found(self, mock_gdb: MagicMock) -> None:
        """Test relationship creation when entities not found."""
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()

        mock_result.single.return_value = None  # No match found
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__ = lambda self: mock_session
        mock_driver.session.return_value.__exit__ = lambda *args: None
        mock_gdb.driver.return_value = mock_driver

        config = HCGConfig(shacl_enabled=False)
        with HCGClient(config) as client:
            with pytest.raises(HCGNotFoundError):
                client.add_relationship(
                    source_id="nonexistent_a",
                    target_id="nonexistent_b",
                    relation_type="HAS_STATE",
                )


class TestHCGClientExceptions:
    """Test exception handling."""

    def test_exceptions_hierarchy(self) -> None:
        """Test exception class hierarchy."""
        from logos_hcg.exceptions import HCGError

        assert issubclass(HCGConnectionError, HCGError)
        assert issubclass(HCGValidationError, HCGError)
        assert issubclass(HCGQueryError, HCGError)
        assert issubclass(HCGNotFoundError, HCGError)

    def test_validation_error_with_errors_list(self) -> None:
        """Test HCGValidationError contains error list."""
        errors = ["Field 'id' is required", "Field 'type' is required"]
        exc = HCGValidationError("Validation failed", errors=errors)

        assert exc.errors == errors
        assert str(exc) == "Validation failed"
