"""
Tests for HCG write operations and SHACL validation.

These tests verify the write operations added to HCGClient
as part of Phase 1 enhancement (logos#350).

Note: These are unit tests that mock Neo4j interactions.
Integration tests require a running Neo4j instance.
"""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch
from uuid import uuid4

import pytest

from logos_hcg.client import HCGClient
from logos_hcg.shacl_validator import HCGValidationError, SHACLValidator


class TestSHACLValidator:
    """Test suite for SHACLValidator class."""

    def test_validator_initialization(self):
        """Test that validator initializes with shapes graph."""
        validator = SHACLValidator()
        assert validator._shapes is not None
        assert len(validator._shapes) > 0  # Has default shapes

    def test_validate_node_valid(self):
        """Test validation of a valid node."""
        validator = SHACLValidator()

        valid_node = {
            "id": str(uuid4()),
            "type": "Entity",
        }

        # Should not raise
        is_valid, errors = validator.validate_node(valid_node)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_node_missing_id(self):
        """Test validation fails for node without id."""
        validator = SHACLValidator()

        invalid_node = {
            "type": "Entity",
        }

        is_valid, errors = validator.validate_node(invalid_node)
        assert is_valid is False
        assert len(errors) > 0
        assert "id" in str(errors).lower()

    def test_validate_node_missing_type(self):
        """Test validation fails for node without type."""
        validator = SHACLValidator()

        invalid_node = {
            "id": str(uuid4()),
        }

        is_valid, errors = validator.validate_node(invalid_node)
        assert is_valid is False
        assert len(errors) > 0
        assert "type" in str(errors).lower()

    def test_validate_edge_valid(self):
        """Test validation of a valid edge."""
        validator = SHACLValidator()

        valid_edge = {
            "id": str(uuid4()),
            "source": str(uuid4()),
            "target": str(uuid4()),
            "relation": "RELATES_TO",
        }

        is_valid, errors = validator.validate_edge(valid_edge)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_edge_missing_source(self):
        """Test validation fails for edge without source."""
        validator = SHACLValidator()

        invalid_edge = {
            "id": str(uuid4()),
            "target": str(uuid4()),
            "relation": "RELATES_TO",
        }

        is_valid, errors = validator.validate_edge(invalid_edge)
        assert is_valid is False
        assert "source" in str(errors).lower()

    def test_validate_edge_missing_target(self):
        """Test validation fails for edge without target."""
        validator = SHACLValidator()

        invalid_edge = {
            "id": str(uuid4()),
            "source": str(uuid4()),
            "relation": "RELATES_TO",
        }

        is_valid, errors = validator.validate_edge(invalid_edge)
        assert is_valid is False
        assert "target" in str(errors).lower()

    def test_validate_edge_missing_relation(self):
        """Test validation fails for edge without relation."""
        validator = SHACLValidator()

        invalid_edge = {
            "id": str(uuid4()),
            "source": str(uuid4()),
            "target": str(uuid4()),
        }

        is_valid, errors = validator.validate_edge(invalid_edge)
        assert is_valid is False
        assert "relation" in str(errors).lower()

    def test_validate_mutation_valid_add_node(self):
        """Test validation of add_node mutation."""
        validator = SHACLValidator()

        node_data = {
            "id": str(uuid4()),
            "type": "Entity",
        }

        is_valid, errors = validator.validate_mutation("add_node", node_data)
        assert is_valid is True

    def test_validate_mutation_valid_add_edge(self):
        """Test validation of add_edge mutation."""
        validator = SHACLValidator()

        edge_data = {
            "id": str(uuid4()),
            "source": str(uuid4()),
            "target": str(uuid4()),
            "relation": "CAUSES",
        }

        is_valid, errors = validator.validate_mutation("add_edge", edge_data)
        assert is_valid is True

    def test_validate_node_with_properties(self):
        """Test validation of node with additional properties."""
        validator = SHACLValidator()

        node_data = {
            "id": str(uuid4()),
            "type": "Entity",
            "properties": {
                "label": "TestEntity",
                "description": "A test entity",
                "created_at": datetime.now().isoformat(),
            },
        }

        is_valid, errors = validator.validate_node(node_data)
        assert is_valid is True


class TestHCGClientWriteOperations:
    """Test suite for HCGClient write operations."""

    @pytest.fixture
    def mock_client(self):
        """Create HCGClient with mocked internal methods."""
        with patch("logos_hcg.client.GraphDatabase") as mock_gdb:
            mock_driver = MagicMock()
            mock_gdb.driver.return_value = mock_driver
            mock_driver.verify_connectivity.return_value = None

            client = HCGClient(
                uri="bolt://localhost:7687",
                user="neo4j",
                password="test",
            )
            return client

    def test_add_node_without_validation(self, mock_client):
        """Test adding a node without SHACL validation."""
        # Mock the internal _execute_read method
        mock_client._execute_read = Mock(return_value=[{"id": "test-id"}])

        node_data = {
            "id": "test-id",
            "type": "Entity",
            "properties": {"label": "Test", "name": "TestEntity"},
        }

        node_id = mock_client.add_node(node_data, validate=False)

        assert node_id == "test-id"
        mock_client._execute_read.assert_called_once()

    def test_add_node_with_validation(self, mock_client):
        """Test adding a node with SHACL validation."""
        mock_client._execute_read = Mock(return_value=[{"id": "test-id"}])

        node_data = {
            "id": "test-id",
            "type": "Entity",
            "properties": {"label": "Test"},
        }

        node_id = mock_client.add_node(node_data, validate=True)

        assert node_id == "test-id"

    def test_add_node_validation_failure(self, mock_client):
        """Test that validation failure prevents node creation."""
        # Node missing required 'type' field
        invalid_node = {
            "id": "test-id",
            # Missing 'type' field
        }

        with pytest.raises(HCGValidationError):
            mock_client.add_node(invalid_node, validate=True)

    def test_add_edge_without_validation(self, mock_client):
        """Test adding an edge without SHACL validation."""
        mock_client._execute_read = Mock(return_value=[{"id": "edge-1"}])

        edge_data = {
            "id": "edge-1",
            "source": "node-1",
            "target": "node-2",
            "relation": "RELATES_TO",
            "properties": {"weight": 1.0},
        }

        edge_id = mock_client.add_edge(edge_data, validate=False)

        assert edge_id == "edge-1"
        mock_client._execute_read.assert_called_once()

    def test_add_edge_with_validation(self, mock_client):
        """Test adding an edge with SHACL validation."""
        mock_client._execute_read = Mock(return_value=[{"id": "edge-1"}])

        edge_data = {
            "id": "edge-1",
            "source": "node-1",
            "target": "node-2",
            "relation": "CAUSES",
        }

        edge_id = mock_client.add_edge(edge_data, validate=True)

        assert edge_id == "edge-1"

    def test_add_edge_validation_failure(self, mock_client):
        """Test that validation failure prevents edge creation."""
        # Edge missing required 'relation' field
        invalid_edge = {
            "id": "edge-1",
            "source": "node-1",
            "target": "node-2",
            # Missing 'relation' field
        }

        with pytest.raises(HCGValidationError):
            mock_client.add_edge(invalid_edge, validate=True)

    def test_update_node(self, mock_client):
        """Test updating a node's properties."""
        mock_client._execute_read = Mock(return_value=[{"updated": 1}])

        result = mock_client.update_node(
            node_id="test-id",
            properties={"name": "UpdatedName", "status": "active"},
        )

        assert result is True
        mock_client._execute_read.assert_called_once()

    def test_delete_node(self, mock_client):
        """Test deleting a node."""
        mock_client._execute_read = Mock(return_value=[{"deleted": 1}])

        success = mock_client.delete_node(node_id="test-id")

        assert success is True
        mock_client._execute_read.assert_called_once()

    def test_delete_edge(self, mock_client):
        """Test deleting an edge."""
        mock_client._execute_read = Mock(return_value=[{"deleted": 1}])

        success = mock_client.delete_edge(edge_id="edge-1")

        assert success is True
        mock_client._execute_read.assert_called_once()

    def test_clear_all(self, mock_client):
        """Test clearing all nodes and edges."""
        mock_client._execute_query = Mock(return_value=None)

        # Should not raise with confirm=True
        mock_client.clear_all(confirm=True)

        mock_client._execute_query.assert_called_once()

    def test_clear_all_without_confirm(self, mock_client):
        """Test that clear_all requires confirm=True."""
        with pytest.raises(ValueError, match="Must pass confirm=True"):
            mock_client.clear_all(confirm=False)


class TestHCGClientNeighborQueries:
    """Test suite for HCGClient neighbor query operations."""

    @pytest.fixture
    def mock_client(self):
        """Create HCGClient with mocked internal methods."""
        with patch("logos_hcg.client.GraphDatabase") as mock_gdb:
            mock_driver = MagicMock()
            mock_gdb.driver.return_value = mock_driver
            mock_driver.verify_connectivity.return_value = None

            client = HCGClient(
                uri="bolt://localhost:7687",
                user="neo4j",
                password="test",
            )
            return client

    def test_query_neighbors(self, mock_client):
        """Test querying neighbors of a node."""
        mock_client._execute_read = Mock(
            return_value=[
                {"id": "n1", "type": "Entity", "props": {}},
                {"id": "n2", "type": "Concept", "props": {}},
            ]
        )

        neighbors = mock_client.query_neighbors(node_id="test-id")

        assert len(neighbors) == 2
        mock_client._execute_read.assert_called_once()

    def test_query_edges_from(self, mock_client):
        """Test querying edges from a node."""
        mock_client._execute_read = Mock(
            return_value=[
                {
                    "id": "e1",
                    "source": "test-id",
                    "target": "t1",
                    "relation": "CAUSES",
                    "props": {},
                },
                {
                    "id": "e2",
                    "source": "test-id",
                    "target": "t2",
                    "relation": "RELATES_TO",
                    "props": {},
                },
            ]
        )

        edges = mock_client.query_edges_from(node_id="test-id")

        assert len(edges) == 2
        mock_client._execute_read.assert_called_once()


class TestSHACLValidatorCustomShapes:
    """Test suite for custom SHACL shapes loading."""

    def test_load_shapes_from_string(self):
        """Test initializing validator with custom SHACL shapes."""
        custom_shapes = """
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        @prefix ex: <http://example.org/hcg/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        ex:CustomNodeShape a sh:NodeShape ;
            sh:targetClass ex:CustomNode ;
            sh:property [
                sh:path ex:customProperty ;
                sh:datatype xsd:string ;
                sh:minCount 1 ;
            ] .
        """

        # Should not raise
        validator = SHACLValidator(shapes_graph=custom_shapes)
        assert validator._shapes is not None
        assert len(validator._shapes) > 0

    def test_load_shapes_from_file_not_found(self):
        """Test loading shapes from non-existent file raises error."""
        validator = SHACLValidator()

        with pytest.raises((FileNotFoundError, Exception)):
            validator.load_shapes_from_file("/nonexistent/path/shapes.ttl")


class TestValidationIntegration:
    """Integration tests for validation with client operations."""

    @pytest.fixture
    def mock_client(self):
        """Create HCGClient with mocked internal methods."""
        with patch("logos_hcg.client.GraphDatabase") as mock_gdb:
            mock_driver = MagicMock()
            mock_gdb.driver.return_value = mock_driver
            mock_driver.verify_connectivity.return_value = None

            client = HCGClient(
                uri="bolt://localhost:7687",
                user="neo4j",
                password="test",
            )
            return client

    def test_validated_workflow(self, mock_client):
        """Test a complete workflow with validation."""
        mock_client._execute_read = Mock(return_value=[{"id": "entity-1"}])

        # Create an entity node
        entity_data = {
            "id": "entity-1",
            "type": "Entity",
            "properties": {"label": "TestEntity"},
        }
        entity_id = mock_client.add_node(entity_data, validate=True)

        # Create a concept node
        mock_client._execute_read = Mock(return_value=[{"id": "concept-1"}])
        concept_data = {
            "id": "concept-1",
            "type": "Concept",
            "properties": {"label": "TestConcept"},
        }
        concept_id = mock_client.add_node(concept_data, validate=True)

        # Create an edge between them
        mock_client._execute_read = Mock(return_value=[{"id": "edge-1"}])
        edge_data = {
            "id": "edge-1",
            "source": entity_id,
            "target": concept_id,
            "relation": "RELATES_TO",
        }
        edge_id = mock_client.add_edge(edge_data, validate=True)

        assert entity_id == "entity-1"
        assert concept_id == "concept-1"
        assert edge_id == "edge-1"


class TestExportedSymbols:
    """Test that all symbols are properly exported."""

    def test_import_from_package(self):
        """Test importing from logos_hcg package."""
        from logos_hcg import (
            HCGClient,
            HCGConnectionError,
            HCGQueryError,
            HCGValidationError,
            SHACLValidator,
        )

        assert HCGClient is not None
        assert HCGConnectionError is not None
        assert HCGQueryError is not None
        assert HCGValidationError is not None
        assert SHACLValidator is not None

    def test_validator_in_all(self):
        """Test that SHACLValidator is in __all__."""
        import logos_hcg

        assert "SHACLValidator" in logos_hcg.__all__
        assert "HCGValidationError" in logos_hcg.__all__
