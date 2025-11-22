#!/usr/bin/env python3
"""
SHACL Validation via Neo4j n10s - Functional Tests

Tests that SHACL validation via Neo4j n10s correctly validates data:
- Loads SHACL shapes into Neo4j
- Validates valid fixture data (should pass)
- Validates invalid fixture data (should fail with violations)
- Rejects bad writes through Neo4j (wrong UUID prefix, missing required properties)

Reference: Phase 1 Gate c-daly/logos#163
"""

import os
from pathlib import Path

import pytest
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

RUN_NEO4J_SHACL = os.getenv("RUN_NEO4J_SHACL") == "1"
pytestmark = pytest.mark.skipif(
    not RUN_NEO4J_SHACL,
    reason="Neo4j SHACL validation runs only when RUN_NEO4J_SHACL=1",
)


@pytest.fixture(scope="module")
def neo4j_driver():
    """Create Neo4j driver for testing."""
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "logosdev")

    driver = GraphDatabase.driver(uri, auth=(user, password))

    # Test connection
    try:
        driver.verify_connectivity()
    except Exception as e:
        pytest.skip(f"Neo4j not available: {e}")

    yield driver
    driver.close()


@pytest.fixture(scope="module")
def neo4j_session(neo4j_driver):
    """Create Neo4j session for testing."""
    with neo4j_driver.session(database="neo4j") as session:
        yield session


def _has_n10s(session):
    """Return list of available n10s procedures."""
    return [
        p[0]
        for p in session.run(
            "SHOW PROCEDURES YIELD name WHERE name STARTS WITH 'n10s' RETURN name"
        ).values()
    ]


def _clear_instance_data(session):
    """Delete only user data, not SHACL shapes/config."""
    session.run(
        """
        MATCH (n)
        WHERE n:Entity OR n:Concept OR n:State OR n:Process OR n.uuid IS NOT NULL
        DETACH DELETE n
        """
    )


def _ensure_shapes(session, procedures):
    """Ensure SHACL shapes are loaded; load from disk if missing."""
    try:
        shapes_count = len(session.run("CALL n10s.validation.shacl.listShapes()").data())
        if shapes_count > 0:
            return
    except Exception:
        # If listShapes fails (e.g. "No shapes compiled"), assume we need to load them
        pass

    shapes_file = Path(__file__).parent.parent.parent / "ontology" / "shacl_shapes.ttl"

    if not shapes_file.exists():
        print(f"DEBUG: Shapes file not found at {shapes_file}")
        return

    shapes_text = shapes_file.read_text(encoding="utf-8")

    if "n10s.validation.shacl.clear" in procedures:
        session.run("CALL n10s.validation.shacl.clear()")
    elif "n10s.validation.shacl.dropShapes" in procedures:
        session.run("CALL n10s.validation.shacl.dropShapes()")

    session.run(
        "CALL n10s.validation.shacl.import.inline($rdf, 'Turtle')",
        rdf=shapes_text,
    )


@pytest.fixture(scope="function")
def setup_neo4j(neo4j_session):
    """Set up Neo4j with SHACL shapes for each test (lightweight, preserves shapes)."""
    procedures = _has_n10s(neo4j_session)
    if not procedures:
        pytest.skip("n10s plugin not installed in Neo4j")

    # Check current config
    current_config = {}
    try:
        result = neo4j_session.run("CALL n10s.graphconfig.show()").data()
        if result:
            current_config = result[0]
    except Exception:
        pass

    print(f"DEBUG: Current config: {current_config}")

    # If config is missing or not KEEP, re-init
    # We check for 'KEEP' or 4 (which seems to be the enum value for KEEP)
    vocab_uris = current_config.get('handleVocabUris')
    if vocab_uris != 'KEEP' and vocab_uris != 4:
        if current_config:
            try:
                # Ensure graph is empty before dropping config
                neo4j_session.run("MATCH (n) DETACH DELETE n")
                neo4j_session.run("CALL n10s.graphconfig.drop()")
                print("DEBUG: Dropped existing config")
            except Exception as e:
                print(f"DEBUG: Drop config failed: {e}")

        try:
            neo4j_session.run(
                "CALL n10s.graphconfig.init({handleVocabUris:'KEEP',handleRDFTypes:'LABELS',handleMultival:'ARRAY',keepLangTag:true})"
            )
            print("DEBUG: Initialized n10s with KEEP")
        except Exception as e:
            print(f"DEBUG: Init config failed: {e}")

    # Ensure constraint exists (n10s requires it)
    try:
        neo4j_session.run("CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS FOR (r:Resource) REQUIRE r.uri IS UNIQUE")
    except Exception as e:
        print(f"DEBUG: Create constraint failed: {e}")

    # Register namespaces
    namespaces = {
        "logos": "http://logos.ontology/",
        "sh": "http://www.w3.org/ns/shacl#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "xsd": "http://www.w3.org/2001/XMLSchema#"
    }
    for prefix, uri in namespaces.items():
        try:
            neo4j_session.run(f"CALL n10s.nsprefixes.add('{prefix}', '{uri}')")
        except Neo4jError:
            pass

    _ensure_shapes(neo4j_session, procedures)
    _clear_instance_data(neo4j_session)

    shapes_count = len(
        neo4j_session.run("CALL n10s.validation.shacl.listShapes()").data()
    )
    assert shapes_count > 0, "SHACL shapes should be loaded"

    yield neo4j_session

    _clear_instance_data(neo4j_session)


def test_neo4j_connection(neo4j_session):
    """Test that Neo4j connection is working."""
    result = neo4j_session.run("RETURN 1 AS test").single()
    assert result["test"] == 1
    print("✓ Neo4j connection verified")


def test_n10s_plugin_loaded(neo4j_session):
    """Test that n10s plugin is loaded and procedures are available."""
    procedures = [
        p[0]
        for p in neo4j_session.run(
            "SHOW PROCEDURES YIELD name WHERE name STARTS WITH 'n10s' RETURN name"
        ).values()
    ]

    assert len(procedures) > 0, "n10s procedures should be available"

    # Check for key procedures
    required_procedures = [
        "n10s.graphconfig.init",
        "n10s.validation.shacl.import.inline",
        "n10s.validation.shacl.validate",
    ]

    for proc in required_procedures:
        matching = [p for p in procedures if proc in p]
        assert len(matching) > 0, f"Procedure {proc} should be available"

    print(f"✓ n10s plugin loaded with {len(procedures)} procedures")


def test_shacl_shapes_loaded(setup_neo4j):
    """Test that SHACL shapes are successfully loaded into Neo4j."""
    shapes = setup_neo4j.run("CALL n10s.validation.shacl.listShapes()").data()

    assert len(shapes) > 0, "At least one SHACL shape should be loaded"

    print(f"✓ Loaded {len(shapes)} SHACL shapes")


def test_validate_valid_entities(setup_neo4j):
    """Test that valid_entities.ttl passes SHACL validation."""
    valid_file = Path(__file__).parent / "fixtures" / "valid_entities.ttl"
    valid_text = valid_file.read_text(encoding="utf-8")

    # Import valid data (keep original namespace)
    setup_neo4j.run("CALL n10s.rdf.import.inline($rdf, 'Turtle')", rdf=valid_text)

    # Validate the data
    validation_result = setup_neo4j.run("CALL n10s.validation.shacl.validate()")

    # Check that validation passed (conforms = true or no violations)
    # Consume the result to check for violations
    violations = []
    for record in validation_result:
        violations.append(record)

    # If there are any violations, the test should fail
    if violations:
        pytest.fail(
            f"Valid data should not have violations. Found {len(violations)} violations: {violations}"
        )

    print("✓ Valid entities passed SHACL validation in Neo4j")


def test_validate_invalid_entities(setup_neo4j):
    """Test that invalid_entities.ttl fails SHACL validation with violations."""
    invalid_file = Path(__file__).parent / "fixtures" / "invalid_entities.ttl"
    invalid_text = invalid_file.read_text(encoding="utf-8")

    # Import invalid data (keep original namespace)
    import_result = setup_neo4j.run("CALL n10s.rdf.import.inline($rdf, 'Turtle')", rdf=invalid_text).data()
    print(f"\nDEBUG: Import result: {import_result}")

    # DEBUG: Check what nodes were created
    nodes = setup_neo4j.run("MATCH (n) RETURN labels(n) as labels, properties(n) as props").data()
    print(f"\nDEBUG: Nodes in graph: {nodes}")

    # Validate the data
    validation_result = setup_neo4j.run("CALL n10s.validation.shacl.validate()")

    # Check that validation failed (violations should be present)
    violations = []
    for record in validation_result:
        violations.append(record)

    print(f"DEBUG: Found {len(violations)} violations")
    for v in violations:
        print(f"DEBUG: Violation: {v}")

    assert len(violations) > 0, "Invalid data should produce validation violations"

    print(
        f"✓ Invalid entities correctly produced {len(violations)} validation violations"
    )
    print("  Sample violations:")
    for i, violation in enumerate(violations[:3]):  # Show first 3 violations
        print(f"    - Violation {i+1}: {violation}")


def test_reject_bad_write_wrong_uuid_prefix(setup_neo4j):
    """Test that Neo4j rejects write with wrong UUID prefix through validation."""
    # Create an entity with wrong UUID prefix (keep original namespace)
    bad_entity_ttl = """
        @prefix logos: <http://logos.ontology/> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        logos:entity-bad-prefix a logos:Entity ;
            logos:uuid "wrong-prefix-123" ;
            logos:name "BadEntity" .
    """

    # Import the bad data
    setup_neo4j.run("CALL n10s.rdf.import.inline($rdf, 'Turtle')", rdf=bad_entity_ttl)

    # Validate - should fail
    validation_result = setup_neo4j.run("CALL n10s.validation.shacl.validate()")

    # Should have violations for wrong UUID pattern
    violations = []
    for record in validation_result:
        violations.append(record)

    assert len(violations) > 0, "Wrong UUID prefix should produce validation violations"

    # Check that the violation is about the UUID pattern
    violation_found = False
    for violation in violations:
        violation_str = str(violation)
        if "uuid" in violation_str.lower() or "pattern" in violation_str.lower():
            violation_found = True
            break

    assert violation_found, "Violation should be related to UUID pattern"

    print("✓ Wrong UUID prefix correctly rejected by SHACL validation")


def test_reject_bad_write_missing_required_property(setup_neo4j):
    """Test that Neo4j rejects write with missing required property through validation."""
    # Create a Concept without required 'name' field (keep original namespace)
    bad_concept_ttl = """
        @prefix logos: <http://logos.ontology/> .

        logos:concept-no-name a logos:Concept ;
            logos:uuid "concept-missing-name" .
    """

    # Import the bad data
    setup_neo4j.run("CALL n10s.rdf.import.inline($rdf, 'Turtle')", rdf=bad_concept_ttl)

    # Validate - should fail
    validation_result = setup_neo4j.run("CALL n10s.validation.shacl.validate()")

    # Should have violations for missing required property
    violations = []
    for record in validation_result:
        violations.append(record)

    assert (
        len(violations) > 0
    ), "Missing required property should produce validation violations"

    print("✓ Missing required property correctly rejected by SHACL validation")
    print(f"  {len(violations)} violations detected")


def test_reject_bad_write_entity_missing_uuid(setup_neo4j):
    """Test that Neo4j rejects entity write with missing UUID."""
    # Create an entity without UUID (keep original namespace)
    bad_entity_ttl = """
        @prefix logos: <http://logos.ontology/> .

        logos:entity-no-uuid a logos:Entity ;
            logos:name "EntityWithoutUUID" .
    """

    # Import the bad data
    setup_neo4j.run("CALL n10s.rdf.import.inline($rdf, 'Turtle')", rdf=bad_entity_ttl)

    # Validate - should fail
    validation_result = setup_neo4j.run("CALL n10s.validation.shacl.validate()")

    # Should have violations for missing UUID
    violations = []
    for record in validation_result:
        violations.append(record)

    assert len(violations) > 0, "Missing UUID should produce validation violations"

    print("✓ Missing UUID correctly rejected by SHACL validation")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
