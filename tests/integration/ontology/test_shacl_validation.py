#!/usr/bin/env python3
"""
M2 Verification: SHACL Validation Catches Errors

Tests that SHACL validation rules successfully catch malformed graph updates
and enforce data quality for the flexible ontology.

FLEXIBLE ONTOLOGY:
All nodes use the :Node label with these required properties:
- uuid: unique identifier
- name: human-readable name
- is_type_definition: boolean (true for types, false for instances)
- type: immediate type name
- ancestors: list of ancestor types

Reference: docs/PHASE1_VERIFY.md, M2 section
Reference: docs/plans/2025-12-30-flexible-ontology-design.md
"""

from pathlib import Path

import pytest
from pyshacl import validate
from rdflib import Graph

from logos_test_utils.env import get_repo_root


@pytest.fixture
def shacl_shapes():
    """Load SHACL shapes from ontology directory."""
    repo_root = get_repo_root()
    shapes_file = repo_root / "ontology" / "shacl_shapes.ttl"
    shapes_graph = Graph()
    shapes_graph.parse(shapes_file, format="turtle")
    return shapes_graph


@pytest.fixture
def valid_data():
    """Load valid test data."""
    valid_file = Path(__file__).parent / "fixtures" / "valid_entities.ttl"
    data_graph = Graph()
    data_graph.parse(valid_file, format="turtle")
    return data_graph


@pytest.fixture
def invalid_data():
    """Load invalid test data."""
    invalid_file = Path(__file__).parent / "fixtures" / "invalid_entities.ttl"
    data_graph = Graph()
    data_graph.parse(invalid_file, format="turtle")
    return data_graph


def test_shacl_shapes_load(shacl_shapes):
    """Test that SHACL shapes file is syntactically valid and loads."""
    assert len(shacl_shapes) > 0, "SHACL shapes graph should not be empty"
    print(f"✓ Loaded {len(shacl_shapes)} SHACL triples")


def test_valid_entities_pass_validation(shacl_shapes, valid_data):
    """Test that valid entity data passes SHACL validation."""
    conforms, results_graph, results_text = validate(
        valid_data, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert conforms, f"Valid data should pass validation. Results:\n{results_text}"
    print("✓ Valid entities passed SHACL validation")


def test_invalid_entities_fail_validation(shacl_shapes, invalid_data):
    """Test that invalid entity data fails SHACL validation."""
    conforms, results_graph, results_text = validate(
        invalid_data, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert not conforms, "Invalid data should fail validation"
    print("✓ Invalid entities correctly failed SHACL validation")
    print(f"  Validation report: {results_text}")


def test_missing_uuid_detected(shacl_shapes):
    """Test that missing UUID is detected by SHACL validation."""
    data_graph = Graph()
    data_graph.parse(
        data="""
        @prefix logos: <http://logos.ai/ontology#> .
        logos:node-no-uuid a logos:Node ;
            logos:name "MissingUUID" ;
            logos:is_type_definition false ;
            logos:type "entity" ;
            logos:ancestors ("entity" "thing") .
    """,
        format="turtle",
    )

    conforms, results_graph, results_text = validate(
        data_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert not conforms, "Node without UUID should fail validation"
    assert "uuid" in results_text.lower() or "minCount" in results_text, (
        "Validation error should mention missing UUID"
    )
    print("✓ Missing UUID correctly detected")


def test_missing_name_detected(shacl_shapes):
    """Test that missing name is detected by SHACL validation."""
    data_graph = Graph()
    data_graph.parse(
        data="""
        @prefix logos: <http://logos.ai/ontology#> .
        logos:node-no-name a logos:Node ;
            logos:uuid "node-no-name" ;
            logos:is_type_definition false ;
            logos:type "entity" ;
            logos:ancestors ("entity" "thing") .
    """,
        format="turtle",
    )

    conforms, results_graph, results_text = validate(
        data_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert not conforms, "Node without name should fail validation"
    print("✓ Missing name correctly detected")


def test_missing_type_detected(shacl_shapes):
    """Test that missing type is detected by SHACL validation."""
    data_graph = Graph()
    data_graph.parse(
        data="""
        @prefix logos: <http://logos.ai/ontology#> .
        logos:node-no-type a logos:Node ;
            logos:uuid "node-no-type" ;
            logos:name "MissingType" ;
            logos:is_type_definition false ;
            logos:ancestors ("entity" "thing") .
    """,
        format="turtle",
    )

    conforms, results_graph, results_text = validate(
        data_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert not conforms, "Node without type should fail validation"
    print("✓ Missing type correctly detected")


def test_missing_is_type_definition_detected(shacl_shapes):
    """Test that missing is_type_definition is detected by SHACL validation."""
    data_graph = Graph()
    data_graph.parse(
        data="""
        @prefix logos: <http://logos.ai/ontology#> .
        logos:node-no-is-type-def a logos:Node ;
            logos:uuid "node-no-is-type-def" ;
            logos:name "MissingIsTypeDef" ;
            logos:type "entity" ;
            logos:ancestors ("entity" "thing") .
    """,
        format="turtle",
    )

    conforms, results_graph, results_text = validate(
        data_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert not conforms, "Node without is_type_definition should fail validation"
    print("✓ Missing is_type_definition correctly detected")


def test_missing_ancestors_detected(shacl_shapes):
    """Test that missing ancestors is detected by SHACL validation."""
    data_graph = Graph()
    data_graph.parse(
        data="""
        @prefix logos: <http://logos.ai/ontology#> .
        logos:node-no-ancestors a logos:Node ;
            logos:uuid "node-no-ancestors" ;
            logos:name "MissingAncestors" ;
            logos:is_type_definition false ;
            logos:type "entity" .
    """,
        format="turtle",
    )

    conforms, results_graph, results_text = validate(
        data_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert not conforms, "Node without ancestors should fail validation"
    print("✓ Missing ancestors correctly detected")


def test_valid_complete_node(shacl_shapes):
    """Test that a complete valid node passes validation."""
    data_graph = Graph()
    data_graph.parse(
        data="""
        @prefix logos: <http://logos.ai/ontology#> .
        logos:valid-node a logos:Node ;
            logos:uuid "valid-node-001" ;
            logos:name "ValidNode" ;
            logos:is_type_definition false ;
            logos:type "entity" ;
            logos:ancestors ("entity" "thing") .
    """,
        format="turtle",
    )

    conforms, results_graph, results_text = validate(
        data_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert conforms, f"Complete valid node should pass. Results:\n{results_text}"
    print("✓ Valid complete node passed validation")


def test_valid_type_definition(shacl_shapes):
    """Test that a valid type definition passes validation."""
    data_graph = Graph()
    data_graph.parse(
        data="""
        @prefix logos: <http://logos.ai/ontology#> .
        logos:type-robot a logos:Node ;
            logos:uuid "5e6f7a8b-9c0d-5e1f-2a3b-4c5d6e7f8a9b" ;
            logos:name "robot" ;
            logos:is_type_definition true ;
            logos:type "robot" ;
            logos:ancestors ("entity" "thing") .
    """,
        format="turtle",
    )

    conforms, results_graph, results_text = validate(
        data_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert conforms, f"Valid type definition should pass. Results:\n{results_text}"
    print("✓ Valid type definition passed validation")


def test_valid_bootstrap_type(shacl_shapes):
    """Test that bootstrap types with empty ancestors pass validation."""
    data_graph = Graph()
    data_graph.parse(
        data="""
        @prefix logos: <http://logos.ai/ontology#> .
        logos:type-concept a logos:Node ;
            logos:uuid "f8b89a6c-9c3e-5e4d-b2f1-83a4d7e4c5f2" ;
            logos:name "concept" ;
            logos:is_type_definition true ;
            logos:type "concept" ;
            logos:ancestors () .
    """,
        format="turtle",
    )

    conforms, results_graph, results_text = validate(
        data_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert conforms, f"Bootstrap type should pass. Results:\n{results_text}"
    print("✓ Valid bootstrap type passed validation")


def test_is_a_relationship_to_node(shacl_shapes):
    """Test that IS_A relationship to a valid Node passes validation."""
    data_graph = Graph()
    data_graph.parse(
        data="""
        @prefix logos: <http://logos.ai/ontology#> .

        logos:type-entity a logos:Node ;
            logos:uuid "e003e45c-50bd-5e4b-85db-883756ecfcf7" ;
            logos:name "entity" ;
            logos:is_type_definition true ;
            logos:type "entity" ;
            logos:ancestors ("thing") .

        logos:instance-robot a logos:Node ;
            logos:uuid "instance-robot" ;
            logos:name "robot1" ;
            logos:is_type_definition false ;
            logos:type "entity" ;
            logos:ancestors ("entity" "thing") ;
            logos:IS_A logos:type-entity .
    """,
        format="turtle",
    )

    conforms, results_graph, results_text = validate(
        data_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert conforms, f"Valid IS_A relationship should pass. Results:\n{results_text}"
    print("✓ Valid IS_A relationship passed validation")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
