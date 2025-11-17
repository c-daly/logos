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
        valid_data,
        shacl_graph=shacl_shapes,
        inference='rdfs',
        abort_on_first=False
    )

    assert conforms, f"Valid data should pass validation. Results:\n{results_text}"
    print("✓ Valid entities passed SHACL validation")


def test_invalid_entities_fail_validation(shacl_shapes, invalid_data):
    """Test that invalid entity data fails SHACL validation."""
    conforms, results_graph, results_text = validate(
        invalid_data,
        shacl_graph=shacl_shapes,
        inference='rdfs',
        abort_on_first=False
    )

    assert not conforms, "Invalid data should fail validation"
    print("✓ Invalid entities correctly failed SHACL validation")
    print(f"  Validation report: {results_text}")


def test_missing_uuid_detected(shacl_shapes):
    """Test that missing UUID is detected by SHACL validation."""
    data_graph = Graph()
    data_graph.parse(data="""
        @prefix logos: <http://logos.ontology/> .
        logos:entity-no-uuid a logos:Entity ;
            logos:name "MissingUUID" .
    """, format="turtle")

    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shacl_shapes,
        inference='rdfs',
        abort_on_first=False
    )

    assert not conforms, "Entity without UUID should fail validation"
    assert "uuid" in results_text.lower() or "minCount" in results_text, \
        "Validation error should mention missing UUID"
    print("✓ Missing UUID correctly detected")


def test_wrong_uuid_format_detected(shacl_shapes):
    """Test that wrong UUID format is detected by SHACL validation."""
    data_graph = Graph()
    data_graph.parse(data="""
        @prefix logos: <http://logos.ontology/> .
        logos:entity-wrong a logos:Entity ;
            logos:uuid "wrong-format-123" ;
            logos:name "WrongFormat" .
    """, format="turtle")

    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shacl_shapes,
        inference='rdfs',
        abort_on_first=False
    )

    assert not conforms, "Entity with wrong UUID format should fail validation"
    assert "pattern" in results_text.lower() or "entity-" in results_text.lower(), \
        "Validation error should mention pattern violation"
    print("✓ Wrong UUID format correctly detected")


def test_concept_name_required(shacl_shapes):
    """Test that Concept requires name field."""
    data_graph = Graph()
    data_graph.parse(data="""
        @prefix logos: <http://logos.ontology/> .
        logos:concept-no-name a logos:Concept ;
            logos:uuid "concept-missing-name" .
    """, format="turtle")

    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shacl_shapes,
        inference='rdfs',
        abort_on_first=False
    )

    assert not conforms, "Concept without name should fail validation"
    print("✓ Missing concept name correctly detected")


def test_state_timestamp_required(shacl_shapes):
    """Test that State requires timestamp field."""
    data_graph = Graph()
    data_graph.parse(data="""
        @prefix logos: <http://logos.ontology/> .
        logos:state-no-timestamp a logos:State ;
            logos:uuid "state-missing-timestamp" ;
            logos:name "NoTimestamp" .
    """, format="turtle")

    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shacl_shapes,
        inference='rdfs',
        abort_on_first=False
    )

    assert not conforms, "State without timestamp should fail validation"
    print("✓ Missing state timestamp correctly detected")


def test_process_start_time_required(shacl_shapes):
    """Test that Process requires start_time field."""
    data_graph = Graph()
    data_graph.parse(data="""
        @prefix logos: <http://logos.ontology/> .
        logos:process-no-time a logos:Process ;
            logos:uuid "process-missing-time" ;
            logos:name "NoTime" .
    """, format="turtle")

    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shacl_shapes,
        inference='rdfs',
        abort_on_first=False
    )

    assert not conforms, "Process without start_time should fail validation"
    print("✓ Missing process start_time correctly detected")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
