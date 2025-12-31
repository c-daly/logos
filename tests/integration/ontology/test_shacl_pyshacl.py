"""
SHACL validation using pyshacl (connectionless).

These tests validate the ontology shapes against known-valid and known-invalid
fixtures without requiring Neo4j or n10s. They serve as a fast sanity check
for shape correctness and fixture coverage in CI.

FLEXIBLE ONTOLOGY:
All nodes use logos:Node with required properties:
- uuid, name, is_type_definition, type, ancestors

Reference: docs/plans/2025-12-30-flexible-ontology-design.md
"""

from pathlib import Path

import pytest
from pyshacl import validate
from rdflib import Graph

from logos_test_utils.env import get_repo_root


def _load_graph(path: Path) -> Graph:
    g = Graph()
    g.parse(path, format="turtle")
    return g


@pytest.fixture(scope="module")
def shapes_graph() -> Graph:
    repo_root = get_repo_root()
    shapes_path = repo_root / "ontology" / "shacl_shapes.ttl"
    return _load_graph(shapes_path)


def _assert_validation(data_graph: Graph, shapes_graph: Graph, expect_conforms: bool) -> None:
    conforms, report, _ = validate(
        data_graph=data_graph,
        shacl_graph=shapes_graph,
        inference="rdfs",
        abort_on_first=False,
    )
    if expect_conforms:
        assert conforms, f"Expected conforming data, but got violations:\n{report}"
    else:
        assert not conforms, "Expected validation failures, but data conformed"


def test_valid_entities_conform(shapes_graph: Graph) -> None:
    data = _load_graph(Path(__file__).parent / "fixtures" / "valid_entities.ttl")
    _assert_validation(data, shapes_graph, expect_conforms=True)


def test_invalid_entities_fail(shapes_graph: Graph) -> None:
    data = _load_graph(Path(__file__).parent / "fixtures" / "invalid_entities.ttl")
    _assert_validation(data, shapes_graph, expect_conforms=False)


def test_missing_uuid_fails(shapes_graph: Graph) -> None:
    """Test that a node missing uuid fails validation."""
    ttl = """
        @prefix logos: <http://logos.ai/ontology#> .

        logos:node-no-uuid a logos:Node ;
            logos:name "NodeWithoutUUID" ;
            logos:is_type_definition false ;
            logos:type "entity" ;
            logos:ancestors ("entity" "thing") .
    """
    g = Graph()
    g.parse(data=ttl, format="turtle")
    _assert_validation(g, shapes_graph, expect_conforms=False)


def test_missing_name_fails(shapes_graph: Graph) -> None:
    """Test that a node missing name fails validation."""
    ttl = """
        @prefix logos: <http://logos.ai/ontology#> .

        logos:node-no-name a logos:Node ;
            logos:uuid "node-no-name" ;
            logos:is_type_definition false ;
            logos:type "entity" ;
            logos:ancestors ("entity" "thing") .
    """
    g = Graph()
    g.parse(data=ttl, format="turtle")
    _assert_validation(g, shapes_graph, expect_conforms=False)


def test_missing_type_fails(shapes_graph: Graph) -> None:
    """Test that a node missing type fails validation."""
    ttl = """
        @prefix logos: <http://logos.ai/ontology#> .

        logos:node-no-type a logos:Node ;
            logos:uuid "node-no-type" ;
            logos:name "NodeWithoutType" ;
            logos:is_type_definition false ;
            logos:ancestors ("entity" "thing") .
    """
    g = Graph()
    g.parse(data=ttl, format="turtle")
    _assert_validation(g, shapes_graph, expect_conforms=False)


def test_missing_is_type_definition_fails(shapes_graph: Graph) -> None:
    """Test that a node missing is_type_definition fails validation."""
    ttl = """
        @prefix logos: <http://logos.ai/ontology#> .

        logos:node-no-is-type-def a logos:Node ;
            logos:uuid "node-no-is-type-def" ;
            logos:name "NodeWithoutIsTypeDef" ;
            logos:type "entity" ;
            logos:ancestors ("entity" "thing") .
    """
    g = Graph()
    g.parse(data=ttl, format="turtle")
    _assert_validation(g, shapes_graph, expect_conforms=False)


def test_node_round_trip(shapes_graph: Graph) -> None:
    """
    Test node round-trip: create valid nodes with relationships, validate them.

    This test verifies flexible ontology acceptance criteria:
    - Type definitions with proper structure
    - Instances with correct type/ancestors
    - IS_A relationships between nodes
    - All nodes pass SHACL validation
    """
    ttl = """
        @prefix logos: <http://logos.ai/ontology#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        # Type definition: robot (IS_A entity IS_A thing)
        logos:type-robot a logos:Node ;
            logos:uuid "5e6f7a8b-9c0d-5e1f-2a3b-4c5d6e7f8a9b" ;
            logos:name "robot" ;
            logos:is_type_definition true ;
            logos:type "robot" ;
            logos:ancestors ("entity" "thing") ;
            logos:description "A robotic manipulator type" .

        # Type definition: robot_state (IS_A state IS_A concept)
        logos:type-robot_state a logos:Node ;
            logos:uuid "6f7a8b9c-0d1e-5f2a-3b4c-5d6e7f8a9b0c" ;
            logos:name "robot_state" ;
            logos:is_type_definition true ;
            logos:type "robot_state" ;
            logos:ancestors ("state" "concept") ;
            logos:description "State type for robots" .

        # Instance: robot-arm-01
        logos:instance-robot-arm-01 a logos:Node ;
            logos:uuid "instance-robot-arm-01" ;
            logos:name "RobotArm01" ;
            logos:is_type_definition false ;
            logos:type "robot" ;
            logos:ancestors ("robot" "entity" "thing") ;
            logos:description "Six-axis robotic manipulator" .

        # Instance: robot-arm-01 initial state
        logos:instance-robot-state-initial a logos:Node ;
            logos:uuid "instance-robot-state-initial" ;
            logos:name "RobotArm01Initial" ;
            logos:is_type_definition false ;
            logos:type "robot_state" ;
            logos:ancestors ("robot_state" "state" "concept") ;
            logos:timestamp "2024-01-01T00:00:00Z"^^xsd:dateTime .

        # IS_A relationships
        logos:instance-robot-arm-01 logos:IS_A logos:type-robot .
        logos:instance-robot-state-initial logos:IS_A logos:type-robot_state .
    """
    g = Graph()
    g.parse(data=ttl, format="turtle")

    # Validate - should pass
    _assert_validation(g, shapes_graph, expect_conforms=True)


def test_valid_bootstrap_types(shapes_graph: Graph) -> None:
    """Test that bootstrap types with empty ancestors pass validation."""
    ttl = """
        @prefix logos: <http://logos.ai/ontology#> .

        # Bootstrap type: concept
        logos:type-concept a logos:Node ;
            logos:uuid "f8b89a6c-9c3e-5e4d-b2f1-83a4d7e4c5f2" ;
            logos:name "concept" ;
            logos:is_type_definition true ;
            logos:type "concept" ;
            logos:ancestors () .

        # Bootstrap type: thing
        logos:type-thing a logos:Node ;
            logos:uuid "a1234567-89ab-5cde-f012-3456789abcde" ;
            logos:name "thing" ;
            logos:is_type_definition true ;
            logos:type "thing" ;
            logos:ancestors () .
    """
    g = Graph()
    g.parse(data=ttl, format="turtle")
    _assert_validation(g, shapes_graph, expect_conforms=True)
