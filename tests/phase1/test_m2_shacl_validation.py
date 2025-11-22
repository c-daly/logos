#!/usr/bin/env python3
"""
M2 Verification: SHACL Validation Catches Errors

Tests that SHACL validation rules successfully catch malformed graph updates
and enforce data quality.

Reference: docs/PHASE1_VERIFY.md, M2 section
"""

from pathlib import Path

import pytest
from pyshacl import validate
from rdflib import Graph


@pytest.fixture
def shacl_shapes():
    """Load SHACL shapes from ontology directory."""
    shapes_file = Path(__file__).parent.parent.parent / "ontology" / "shacl_shapes.ttl"
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
        @prefix logos: <http://logos.ontology/> .
        logos:entity-no-uuid a logos:Entity ;
            logos:name "MissingUUID" .
    """,
        format="turtle",
    )

    conforms, results_graph, results_text = validate(
        data_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert not conforms, "Entity without UUID should fail validation"
    assert (
        "uuid" in results_text.lower() or "minCount" in results_text
    ), "Validation error should mention missing UUID"
    print("✓ Missing UUID correctly detected")


def test_wrong_uuid_format_detected(shacl_shapes):
    """Test that wrong UUID format is detected by SHACL validation."""
    data_graph = Graph()
    data_graph.parse(
        data="""
        @prefix logos: <http://logos.ontology/> .
        logos:entity-wrong a logos:Entity ;
            logos:uuid "wrong-format-123" ;
            logos:name "WrongFormat" .
    """,
        format="turtle",
    )

    conforms, results_graph, results_text = validate(
        data_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert not conforms, "Entity with wrong UUID format should fail validation"
    assert (
        "pattern" in results_text.lower() or "entity-" in results_text.lower()
    ), "Validation error should mention pattern violation"
    print("✓ Wrong UUID format correctly detected")


def test_concept_name_required(shacl_shapes):
    """Test that Concept requires name field."""
    data_graph = Graph()
    data_graph.parse(
        data="""
        @prefix logos: <http://logos.ontology/> .
        logos:concept-no-name a logos:Concept ;
            logos:uuid "concept-missing-name" .
    """,
        format="turtle",
    )

    conforms, results_graph, results_text = validate(
        data_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert not conforms, "Concept without name should fail validation"
    print("✓ Missing concept name correctly detected")


def test_state_timestamp_required(shacl_shapes):
    """Test that State requires timestamp field."""
    data_graph = Graph()
    data_graph.parse(
        data="""
        @prefix logos: <http://logos.ontology/> .
        logos:state-no-timestamp a logos:State ;
            logos:uuid "state-missing-timestamp" ;
            logos:name "NoTimestamp" .
    """,
        format="turtle",
    )

    conforms, results_graph, results_text = validate(
        data_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert not conforms, "State without timestamp should fail validation"
    print("✓ Missing state timestamp correctly detected")


def test_process_start_time_required(shacl_shapes):
    """Test that Process requires start_time field."""
    data_graph = Graph()
    data_graph.parse(
        data="""
        @prefix logos: <http://logos.ontology/> .
        logos:process-no-time a logos:Process ;
            logos:uuid "process-missing-time" ;
            logos:name "NoTime" .
    """,
        format="turtle",
    )

    conforms, results_graph, results_text = validate(
        data_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert not conforms, "Process without start_time should fail validation"
    print("✓ Missing process start_time correctly detected")


def test_spatial_properties_validation(shacl_shapes):
    """Test that spatial properties validate correctly with positive values."""
    data_graph = Graph()
    data_graph.parse(
        data="""
        @prefix logos: <http://logos.ontology/> .
        logos:entity-spatial a logos:Entity ;
            logos:uuid "entity-spatial-test" ;
            logos:name "SpatialTest" ;
            logos:width "0.5"^^<http://www.w3.org/2001/XMLSchema#decimal> ;
            logos:height "0.3"^^<http://www.w3.org/2001/XMLSchema#decimal> ;
            logos:mass "1.5"^^<http://www.w3.org/2001/XMLSchema#decimal> .
    """,
        format="turtle",
    )

    conforms, results_graph, results_text = validate(
        data_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert conforms, f"Valid spatial properties should pass. Results:\n{results_text}"
    print("✓ Valid spatial properties passed validation")


def test_negative_spatial_properties_rejected(shacl_shapes):
    """Test that negative spatial values are rejected."""
    data_graph = Graph()
    data_graph.parse(
        data="""
        @prefix logos: <http://logos.ontology/> .
        logos:entity-negative a logos:Entity ;
            logos:uuid "entity-negative-test" ;
            logos:name "NegativeTest" ;
            logos:width "-0.5"^^<http://www.w3.org/2001/XMLSchema#decimal> .
    """,
        format="turtle",
    )

    conforms, results_graph, results_text = validate(
        data_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert not conforms, "Negative spatial values should fail validation"
    print("✓ Negative spatial values correctly rejected")


def test_joint_type_enumeration(shacl_shapes):
    """Test that joint_type accepts only valid enumerated values."""
    # Test valid joint type
    valid_graph = Graph()
    valid_graph.parse(
        data="""
        @prefix logos: <http://logos.ontology/> .
        logos:joint-valid a logos:Entity ;
            logos:uuid "entity-joint-valid" ;
            logos:name "ValidJoint" ;
            logos:joint_type "revolute" .
    """,
        format="turtle",
    )

    conforms, _, results_text = validate(
        valid_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert conforms, f"Valid joint type should pass. Results:\n{results_text}"

    # Test invalid joint type
    invalid_graph = Graph()
    invalid_graph.parse(
        data="""
        @prefix logos: <http://logos.ontology/> .
        logos:joint-invalid a logos:Entity ;
            logos:uuid "entity-joint-invalid" ;
            logos:name "InvalidJoint" ;
            logos:joint_type "invalid_type" .
    """,
        format="turtle",
    )

    conforms, _, results_text = validate(
        invalid_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert not conforms, "Invalid joint type should fail validation"
    print("✓ Joint type enumeration correctly enforced")


def test_is_a_relationship_type(shacl_shapes):
    """Test that IS_A relationship validates target is a Concept."""
    # Valid IS_A relationship
    valid_graph = Graph()
    valid_graph.parse(
        data="""
        @prefix logos: <http://logos.ontology/> .
        logos:concept-test a logos:Concept ;
            logos:uuid "concept-test" ;
            logos:name "TestConcept" .
        logos:entity-test a logos:Entity ;
            logos:uuid "entity-test" ;
            logos:name "TestEntity" ;
            logos:IS_A logos:concept-test .
    """,
        format="turtle",
    )

    conforms, _, results_text = validate(
        valid_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert conforms, f"Valid IS_A relationship should pass. Results:\n{results_text}"
    print("✓ Valid IS_A relationship passed validation")


def test_has_state_relationship_type(shacl_shapes):
    """Test that HAS_STATE relationship validates target is a State."""
    valid_graph = Graph()
    valid_graph.parse(
        data="""
        @prefix logos: <http://logos.ontology/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        logos:state-test a logos:State ;
            logos:uuid "state-test" ;
            logos:timestamp "2025-11-17T00:00:00Z"^^xsd:dateTime .
        logos:entity-test a logos:Entity ;
            logos:uuid "entity-test" ;
            logos:name "TestEntity" ;
            logos:HAS_STATE logos:state-test .
    """,
        format="turtle",
    )

    conforms, _, results_text = validate(
        valid_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert (
        conforms
    ), f"Valid HAS_STATE relationship should pass. Results:\n{results_text}"
    print("✓ Valid HAS_STATE relationship passed validation")


def test_causes_relationship_type(shacl_shapes):
    """Test that CAUSES relationship validates target is a State."""
    valid_graph = Graph()
    valid_graph.parse(
        data="""
        @prefix logos: <http://logos.ontology/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        logos:state-result a logos:State ;
            logos:uuid "state-result" ;
            logos:timestamp "2025-11-17T00:00:00Z"^^xsd:dateTime .
        logos:process-test a logos:Process ;
            logos:uuid "process-test" ;
            logos:start_time "2025-11-17T00:00:00Z"^^xsd:dateTime ;
            logos:CAUSES logos:state-result .
    """,
        format="turtle",
    )

    conforms, _, results_text = validate(
        valid_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert conforms, f"Valid CAUSES relationship should pass. Results:\n{results_text}"
    print("✓ Valid CAUSES relationship passed validation")


def test_part_of_relationship_type(shacl_shapes):
    """Test that PART_OF relationship validates target is an Entity."""
    valid_graph = Graph()
    valid_graph.parse(
        data="""
        @prefix logos: <http://logos.ontology/> .
        logos:parent-entity a logos:Entity ;
            logos:uuid "entity-parent" ;
            logos:name "ParentEntity" .
        logos:child-entity a logos:Entity ;
            logos:uuid "entity-child" ;
            logos:name "ChildEntity" ;
            logos:PART_OF logos:parent-entity .
    """,
        format="turtle",
    )

    conforms, _, results_text = validate(
        valid_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert conforms, f"Valid PART_OF relationship should pass. Results:\n{results_text}"
    print("✓ Valid PART_OF relationship passed validation")


def test_located_at_relationship_type(shacl_shapes):
    """Test that LOCATED_AT relationship validates target is an Entity."""
    valid_graph = Graph()
    valid_graph.parse(
        data="""
        @prefix logos: <http://logos.ontology/> .
        logos:location-entity a logos:Entity ;
            logos:uuid "entity-location" ;
            logos:name "Location" .
        logos:object-entity a logos:Entity ;
            logos:uuid "entity-object" ;
            logos:name "Object" ;
            logos:LOCATED_AT logos:location-entity .
    """,
        format="turtle",
    )

    conforms, _, results_text = validate(
        valid_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert (
        conforms
    ), f"Valid LOCATED_AT relationship should pass. Results:\n{results_text}"
    print("✓ Valid LOCATED_AT relationship passed validation")


def test_attached_to_relationship_type(shacl_shapes):
    """Test that ATTACHED_TO relationship validates target is an Entity."""
    valid_graph = Graph()
    valid_graph.parse(
        data="""
        @prefix logos: <http://logos.ontology/> .
        logos:base-entity a logos:Entity ;
            logos:uuid "entity-base" ;
            logos:name "Base" .
        logos:attached-entity a logos:Entity ;
            logos:uuid "entity-attached" ;
            logos:name "Attached" ;
            logos:ATTACHED_TO logos:base-entity .
    """,
        format="turtle",
    )

    conforms, _, results_text = validate(
        valid_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert (
        conforms
    ), f"Valid ATTACHED_TO relationship should pass. Results:\n{results_text}"
    print("✓ Valid ATTACHED_TO relationship passed validation")


def test_precedes_relationship_type(shacl_shapes):
    """Test that PRECEDES relationship validates both nodes are States."""
    valid_graph = Graph()
    valid_graph.parse(
        data="""
        @prefix logos: <http://logos.ontology/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        logos:state-first a logos:State ;
            logos:uuid "state-first" ;
            logos:timestamp "2025-11-17T00:00:00Z"^^xsd:dateTime .
        logos:state-second a logos:State ;
            logos:uuid "state-second" ;
            logos:timestamp "2025-11-17T00:01:00Z"^^xsd:dateTime ;
            logos:PRECEDES logos:state-first .
    """,
        format="turtle",
    )

    conforms, _, results_text = validate(
        valid_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert (
        conforms
    ), f"Valid PRECEDES relationship should pass. Results:\n{results_text}"
    print("✓ Valid PRECEDES relationship passed validation")


def test_requires_relationship_type(shacl_shapes):
    """Test that REQUIRES relationship validates target is a State."""
    valid_graph = Graph()
    valid_graph.parse(
        data="""
        @prefix logos: <http://logos.ontology/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        logos:state-precondition a logos:State ;
            logos:uuid "state-precondition" ;
            logos:timestamp "2025-11-17T00:00:00Z"^^xsd:dateTime .
        logos:process-requires a logos:Process ;
            logos:uuid "process-requires" ;
            logos:start_time "2025-11-17T00:00:00Z"^^xsd:dateTime ;
            logos:REQUIRES logos:state-precondition .
    """,
        format="turtle",
    )

    conforms, _, results_text = validate(
        valid_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert (
        conforms
    ), f"Valid REQUIRES relationship should pass. Results:\n{results_text}"
    print("✓ Valid REQUIRES relationship passed validation")


def test_can_perform_relationship_type(shacl_shapes):
    """Test that CAN_PERFORM relationship validates target is a Concept."""
    valid_graph = Graph()
    valid_graph.parse(
        data="""
        @prefix logos: <http://logos.ontology/> .
        logos:concept-capability a logos:Concept ;
            logos:uuid "concept-capability" ;
            logos:name "Capability" .
        logos:entity-capable a logos:Entity ;
            logos:uuid "entity-capable" ;
            logos:name "CapableEntity" ;
            logos:CAN_PERFORM logos:concept-capability .
    """,
        format="turtle",
    )

    conforms, _, results_text = validate(
        valid_graph, shacl_graph=shacl_shapes, inference="rdfs", abort_on_first=False
    )

    assert (
        conforms
    ), f"Valid CAN_PERFORM relationship should pass. Results:\n{results_text}"
    print("✓ Valid CAN_PERFORM relationship passed validation")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
