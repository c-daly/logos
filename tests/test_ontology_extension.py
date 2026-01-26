#!/usr/bin/env python3
"""
Integration test that verifies the ontology files can be parsed and validated.
This test does not require a running Neo4j instance.

FLEXIBLE ONTOLOGY:
All nodes use the :Node label with these properties:
- uuid: unique identifier
- name: human-readable name
- is_type_definition: boolean (true for types, false for instances)
- type: immediate type name
- ancestors: list of ancestor types up to bootstrap root
"""

import re
from pathlib import Path

import pytest


def test_core_ontology_structure():
    """Test that core_ontology.cypher has expected structure for flexible ontology."""
    ontology_file = Path(__file__).parent.parent / "ontology" / "core_ontology.cypher"
    content = ontology_file.read_text()

    # Check for required constraints (flexible ontology uses single :Node label)
    assert (
        "CREATE CONSTRAINT logos_node_uuid" in content
    ), "Missing Node UUID constraint"

    # Check for indexes (flexible ontology indexes)
    assert "CREATE INDEX logos_node_type" in content, "Missing Node type index"
    assert "CREATE INDEX logos_node_name" in content, "Missing Node name index"
    assert (
        "CREATE INDEX logos_node_is_type_def" in content
    ), "Missing Node is_type_definition index"

    # Check for bootstrap types
    bootstrap_types = [
        "type_definition",
        "edge_type",
        "thing",
        "concept",
    ]
    for boot_type in bootstrap_types:
        assert boot_type in content, f"Missing bootstrap type: {boot_type}"

    # Check for flexible ontology patterns
    assert "is_type_definition" in content, "Missing is_type_definition property"
    assert "ancestors" in content, "Missing ancestors property"

    # Check that IS_A edge type is defined (the core relationship)
    assert "IS_A" in content, "Missing IS_A edge type"

    print("✓ core_ontology.cypher structure verified (flexible ontology)")


def test_test_data_structure():
    """Test that test_data_pick_and_place.cypher has expected entities."""
    test_data_file = (
        Path(__file__).parent.parent / "ontology" / "test_data_pick_and_place.cypher"
    )
    content = test_data_file.read_text()

    # Check for robot entities
    assert "RobotArm01" in content
    assert "Gripper01" in content
    assert "Joint01-Base" in content

    # Check for workspace entities
    assert "WorkTable01" in content
    assert "TargetBin01" in content

    # Check for object entities
    assert "RedBlock01" in content
    assert "BlueBlock01" in content
    assert "GreenCylinder01" in content

    # Check for processes
    assert "MoveToPreGraspPosition" in content
    assert "GraspRedBlock" in content
    assert "ReleaseRedBlock" in content

    # Check for states
    assert "ArmHomeState" in content
    assert "GripperOpenState" in content
    assert "RedBlockOnTableState" in content

    # Check for relationship types
    assert "[:IS_A]->" in content
    assert "[:HAS_STATE]->" in content
    assert "[:CAUSES]->" in content
    assert "[:PART_OF]->" in content
    assert "[:LOCATED_AT]->" in content
    assert "[:PRECEDES]->" in content
    assert "[:REQUIRES]->" in content

    # Check for flexible ontology patterns
    assert ":Node" in content, "Missing :Node label (flexible ontology)"
    assert "is_type_definition" in content, "Missing is_type_definition property"
    assert "ancestors" in content, "Missing ancestors property"

    print("✓ test_data_pick_and_place.cypher structure verified")


def test_shacl_shapes_structure():
    """Test that shacl_shapes.ttl has expected shapes for flexible ontology."""
    shacl_file = Path(__file__).parent.parent / "ontology" / "shacl_shapes.ttl"
    content = shacl_file.read_text()

    # Check for required prefixes
    assert "@prefix sh:" in content
    assert "@prefix logos:" in content
    assert "@prefix rdfs:" in content
    assert "@prefix xsd:" in content

    # Check for core shape (flexible ontology uses single NodeShape)
    assert "logos:NodeShape" in content, "Missing logos:NodeShape"

    # Check for required properties in NodeShape
    required_props = [
        "uuid",
        "name",
        "is_type_definition",
        "type",
        "ancestors",
    ]
    for prop in required_props:
        assert prop in content, f"Missing property: {prop}"

    # Check for IS_A relationship shape (core relationship)
    assert "logos:IsARelationshipShape" in content, "Missing IS_A relationship shape"

    print("✓ shacl_shapes.ttl structure verified (flexible ontology)")


def test_uuid_consistency():
    """Test that UUIDs in test data are valid (RFC 4122 or type-prefixed format)."""
    import uuid as uuid_module

    test_data_file = (
        Path(__file__).parent.parent / "ontology" / "test_data_pick_and_place.cypher"
    )
    content = test_data_file.read_text()

    # Extract all UUIDs
    entity_uuids = re.findall(r"uuid:\s*['\"]([^'\"]+)['\"]", content)

    # Type prefixes that are valid (for type definitions and special nodes)
    type_prefixes = (
        "type-",  # Type definitions
        "entity-",  # Legacy prefixes still accepted
        "concept-",
        "state-",
        "process-",
        "capability-",
    )

    # Check that all UUIDs are valid (either RFC 4122 or type-prefixed)
    for uuid_str in entity_uuids:
        # Accept type-prefixed UUIDs
        if uuid_str.startswith(type_prefixes):
            continue
        # Otherwise must be valid RFC 4122
        try:
            uuid_module.UUID(uuid_str)
        except ValueError:
            pytest.fail(f"Invalid UUID format: {uuid_str}")

    # Verify we found some UUIDs
    assert len(entity_uuids) > 0, "No UUIDs found in test data"

    print(f"✓ UUID consistency verified ({len(entity_uuids)} valid UUIDs)")


def test_property_definitions():
    """Test that domain-specific properties are used in test data.

    TODO: Revisit SHACL property validation once flexible ontology is running.
    The domain-specific shapes (SpatialPropertiesShape, GripperPropertiesShape,
    JointPropertiesShape) need to be added back to shacl_shapes.ttl.
    """
    # shacl_file = Path(__file__).parent.parent / "ontology" / "shacl_shapes.ttl"
    test_data_file = (
        Path(__file__).parent.parent / "ontology" / "test_data_pick_and_place.cypher"
    )

    # shacl_content = shacl_file.read_text()
    test_content = test_data_file.read_text()

    # TODO: Re-enable SHACL property validation once domain shapes are added
    # Properties that should appear in both SHACL and test data
    # spatial_props = [
    #     "position_x",
    #     "position_y",
    #     "position_z",
    #     "orientation_roll",
    #     "orientation_pitch",
    #     "orientation_yaw",
    # ]
    #
    # for prop in spatial_props:
    #     # Should be in SHACL
    #     assert prop in shacl_content, f"Property {prop} not in SHACL"
    #     # Should be in test data
    #     assert prop in test_content, f"Property {prop} not used in test data"

    # Gripper properties
    gripper_props = ["max_grasp_width", "max_force", "grasp_width", "applied_force"]
    for prop in gripper_props:
        assert prop in test_content, f"Gripper property {prop} not in test data"

    # Joint properties
    joint_props = ["joint_type", "min_angle", "max_angle"]
    for prop in joint_props:
        assert prop in test_content, f"Joint property {prop} not in test data"

    print("✓ Property definitions verified (SHACL validation TODO)")


def test_flexible_ontology_type_hierarchy():
    """Test that test data has proper type definitions and instances."""
    test_data_file = (
        Path(__file__).parent.parent / "ontology" / "test_data_pick_and_place.cypher"
    )
    content = test_data_file.read_text()

    # Check for type definitions (using Cypher SET syntax)
    type_defs = [
        "is_type_definition = true",
        "'Manipulator'",
        "'Gripper'",
        "'Joint'",
        "'GraspableObject'",
        "'Container'",
    ]
    for type_def in type_defs:
        assert type_def in content, f"Missing type definition: {type_def}"

    # Check for ancestors property usage (Cypher SET syntax)
    assert "ancestors = [" in content, "Missing ancestors property"

    # Check for proper instance patterns (Cypher SET syntax)
    instance_pattern = "is_type_definition = false"
    assert instance_pattern in content, "Missing instance declarations"

    print("✓ Flexible ontology type hierarchy verified")


if __name__ == "__main__":
    test_core_ontology_structure()
    test_test_data_structure()
    test_shacl_shapes_structure()
    test_uuid_consistency()
    test_property_definitions()
    test_flexible_ontology_type_hierarchy()

    print("\n" + "=" * 70)
    print("✓ All ontology extension tests passed (flexible ontology)")
    print("=" * 70)
