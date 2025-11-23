#!/usr/bin/env python3
"""
Integration test that verifies the ontology files can be parsed and validated.
This test does not require a running Neo4j instance.
"""

import re
from pathlib import Path


def test_core_ontology_structure():
    """Test that core_ontology.cypher has expected structure."""
    ontology_file = Path(__file__).parent.parent / "ontology" / "core_ontology.cypher"
    content = ontology_file.read_text()

    # Check for required constraints
    assert "CREATE CONSTRAINT logos_entity_uuid" in content
    assert "CREATE CONSTRAINT logos_concept_uuid" in content
    assert "CREATE CONSTRAINT logos_state_uuid" in content
    assert "CREATE CONSTRAINT logos_process_uuid" in content
    assert "CREATE CONSTRAINT logos_concept_name" in content

    # Check for indexes
    assert "CREATE INDEX logos_entity_name" in content
    assert "CREATE INDEX logos_state_timestamp" in content
    assert "CREATE INDEX logos_process_timestamp" in content

    # Check for core concepts
    concepts = [
        "Manipulator",
        "Gripper",
        "Joint",
        "GraspableObject",
        "Container",
        "RigidBody",
        "Surface",
        "Workspace",
        "Location",
        "GraspAction",
        "ReleaseAction",
        "MoveAction",
        "PlaceAction",
        "GraspedState",
        "FreeState",
        "PositionedState",
    ]

    for concept in concepts:
        assert concept in content, f"Missing concept: {concept}"

    # Check for relationship documentation
    relationships = [
        "IS_A",
        "HAS_STATE",
        "CAUSES",
        "PART_OF",
        "LOCATED_AT",
        "PRECEDES",
        "REQUIRES",
    ]
    for rel in relationships:
        assert rel in content, f"Missing relationship documentation: {rel}"

    print("✓ core_ontology.cypher structure verified")


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

    print("✓ test_data_pick_and_place.cypher structure verified")


def test_shacl_shapes_structure():
    """Test that shacl_shapes.ttl has expected shapes."""
    shacl_file = Path(__file__).parent.parent / "ontology" / "shacl_shapes.ttl"
    content = shacl_file.read_text()

    # Check for required prefixes
    assert "@prefix sh:" in content
    assert "@prefix logos:" in content
    assert "@prefix rdfs:" in content
    assert "@prefix xsd:" in content

    # Check for core shapes
    shapes = [
        "logos:EntityShape",
        "logos:ConceptShape",
        "logos:StateShape",
        "logos:ProcessShape",
    ]

    for shape in shapes:
        assert shape in content, f"Missing shape: {shape}"

    # Check for domain-specific shapes
    domain_shapes = [
        "logos:SpatialPropertiesShape",
        "logos:GripperPropertiesShape",
        "logos:JointPropertiesShape",
    ]

    for shape in domain_shapes:
        assert shape in content, f"Missing domain shape: {shape}"

    # Check for relationship shapes
    rel_shapes = [
        "logos:IsARelationshipShape",
        "logos:HasStateRelationshipShape",
        "logos:CausesRelationshipShape",
    ]

    for shape in rel_shapes:
        assert shape in content, f"Missing relationship shape: {shape}"

    # Check for UUID patterns
    assert 'sh:pattern "^entity-.*"' in content
    assert 'sh:pattern "^concept-.*"' in content
    assert 'sh:pattern "^state-.*"' in content
    assert 'sh:pattern "^process-.*"' in content

    print("✓ shacl_shapes.ttl structure verified")


def test_uuid_consistency():
    """Test that UUIDs in test data follow the patterns defined in SHACL."""
    test_data_file = (
        Path(__file__).parent.parent / "ontology" / "test_data_pick_and_place.cypher"
    )
    content = test_data_file.read_text()

    # Extract all UUIDs
    entity_uuids = re.findall(r"uuid:\s*['\"]([^'\"]+)['\"]", content)

    # Check patterns
    for uuid in entity_uuids:
        assert uuid.startswith(
            ("entity-", "concept-", "state-", "process-")
        ), f"UUID doesn't follow pattern: {uuid}"

    # Check for specific expected UUIDs
    expected_entities = [
        "entity-robot-arm-01",
        "entity-gripper-01",
        "entity-block-red-01",
    ]
    expected_concepts = ["concept-manipulator", "concept-gripper", "concept-graspable"]
    expected_states = ["state-arm-home-01", "state-gripper-open-01"]
    expected_processes = ["process-move-pregrasp-01", "process-grasp-red-01"]

    for uuid in (
        expected_entities + expected_concepts + expected_states + expected_processes
    ):
        assert uuid in entity_uuids, f"Expected UUID not found: {uuid}"

    print("✓ UUID consistency verified")


def test_property_definitions():
    """Test that properties mentioned in SHACL are used in test data."""
    shacl_file = Path(__file__).parent.parent / "ontology" / "shacl_shapes.ttl"
    test_data_file = (
        Path(__file__).parent.parent / "ontology" / "test_data_pick_and_place.cypher"
    )

    shacl_content = shacl_file.read_text()
    test_content = test_data_file.read_text()

    # Properties that should appear in test data
    spatial_props = [
        "position_x",
        "position_y",
        "position_z",
        "orientation_roll",
        "orientation_pitch",
        "orientation_yaw",
    ]

    for prop in spatial_props:
        # Should be in SHACL
        assert prop in shacl_content, f"Property {prop} not in SHACL"
        # Should be in test data
        assert prop in test_content, f"Property {prop} not used in test data"

    # Gripper properties
    gripper_props = ["max_grasp_width", "max_force", "grasp_width", "applied_force"]
    for prop in gripper_props:
        assert prop in test_content, f"Gripper property {prop} not in test data"

    # Joint properties
    joint_props = ["joint_type", "min_angle", "max_angle"]
    for prop in joint_props:
        assert prop in test_content, f"Joint property {prop} not in test data"

    print("✓ Property definitions verified")


if __name__ == "__main__":
    test_core_ontology_structure()
    test_test_data_structure()
    test_shacl_shapes_structure()
    test_uuid_consistency()
    test_property_definitions()

    print("\n" + "=" * 70)
    print("✓ All ontology extension tests passed")
    print("=" * 70)
