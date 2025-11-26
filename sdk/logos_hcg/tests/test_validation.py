"""Tests for SHACL validator."""

import pytest

from logos_hcg.validation import SHACLValidator


class TestSHACLValidator:
    """Test SHACL validator."""

    @pytest.fixture
    def validator(self) -> SHACLValidator:
        """Create default validator."""
        return SHACLValidator()

    def test_validate_valid_node(self, validator: SHACLValidator) -> None:
        """Test validation of a valid node."""
        node_data = {
            "id": "entity_123",
            "type": "manipulator",
            "properties": {"name": "gripper"},
        }

        is_valid, errors = validator.validate_node(node_data)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_node_missing_id(self, validator: SHACLValidator) -> None:
        """Test validation fails without ID."""
        node_data = {
            "type": "manipulator",
        }

        is_valid, errors = validator.validate_node(node_data)

        assert is_valid is False
        assert any("id" in error.lower() for error in errors)

    def test_validate_node_missing_type(self, validator: SHACLValidator) -> None:
        """Test validation fails without type."""
        node_data = {
            "id": "entity_123",
        }

        is_valid, errors = validator.validate_node(node_data)

        assert is_valid is False
        assert any("type" in error.lower() for error in errors)

    def test_validate_valid_edge(self, validator: SHACLValidator) -> None:
        """Test validation of a valid edge."""
        edge_data = {
            "id": "edge_123",
            "source": "entity_a",
            "target": "entity_b",
            "relation": "HAS_STATE",
        }

        is_valid, errors = validator.validate_edge(edge_data)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_edge_missing_fields(self, validator: SHACLValidator) -> None:
        """Test validation fails for edge missing required fields."""
        # Missing source
        edge_data = {
            "id": "edge_123",
            "target": "entity_b",
            "relation": "HAS_STATE",
        }

        is_valid, errors = validator.validate_edge(edge_data)
        assert is_valid is False
        assert any("source" in error.lower() for error in errors)

        # Missing target
        edge_data = {
            "id": "edge_123",
            "source": "entity_a",
            "relation": "HAS_STATE",
        }

        is_valid, errors = validator.validate_edge(edge_data)
        assert is_valid is False
        assert any("target" in error.lower() for error in errors)

        # Missing relation
        edge_data = {
            "id": "edge_123",
            "source": "entity_a",
            "target": "entity_b",
        }

        is_valid, errors = validator.validate_edge(edge_data)
        assert is_valid is False
        assert any("relation" in error.lower() for error in errors)

    def test_custom_shapes(self) -> None:
        """Test validator with custom SHACL shapes."""
        custom_shapes = """
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        @prefix ex: <http://example.org/hcg/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        ex:CustomNodeShape a sh:NodeShape ;
            sh:targetClass ex:CustomNode ;
            sh:property [
                sh:path ex:customField ;
                sh:minCount 1 ;
            ] .
        """

        validator = SHACLValidator(shapes_graph=custom_shapes)

        # Should still pass basic validation
        node_data = {"id": "test_123", "type": "test"}
        is_valid, errors = validator.validate_node(node_data)

        # Basic validation should pass
        assert is_valid is True


class TestSHACLValidatorEdgeCases:
    """Test edge cases for SHACL validator."""

    def test_empty_node_data(self) -> None:
        """Test validation with empty node data."""
        validator = SHACLValidator()

        is_valid, errors = validator.validate_node({})

        assert is_valid is False
        assert len(errors) >= 2  # Missing both id and type

    def test_empty_edge_data(self) -> None:
        """Test validation with empty edge data."""
        validator = SHACLValidator()

        is_valid, errors = validator.validate_edge({})

        assert is_valid is False
        assert len(errors) >= 4  # Missing id, source, target, relation

    def test_node_with_extra_properties(self) -> None:
        """Test that extra properties don't cause validation failure."""
        validator = SHACLValidator()

        node_data = {
            "id": "entity_123",
            "type": "test",
            "properties": {
                "custom_field": "value",
                "nested": {"key": "value"},
            },
            "extra_field": "should be ignored",
        }

        is_valid, errors = validator.validate_node(node_data)

        assert is_valid is True
