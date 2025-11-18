#!/usr/bin/env python3
"""
M2 Verification: SHACL Validation via Neo4j with n10s

Tests that SHACL validation rules loaded into Neo4j via the neosemantics (n10s)
plugin successfully enforce data quality constraints.

This test suite validates:
1. Loading SHACL shapes into Neo4j via n10s
2. Validation of valid test data (should pass)
3. Validation of invalid test data (should fail with violations)
4. Rejection of bad writes through Neo4j (constraint enforcement at database level)

Reference: docs/PHASE1_VERIFY.md, M2 section
Issue: c-daly/logos#163, c-daly/logos#167
"""

import os
from pathlib import Path

import pytest
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

# Test configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "logosdev")
REPO_ROOT = Path(__file__).parent.parent.parent


def is_neo4j_available() -> bool:
    """Check if Neo4j is available for testing."""
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            result.single()
        driver.close()
        return True
    except (ServiceUnavailable, Exception):
        return False


def is_n10s_available(driver) -> bool:
    """Check if n10s plugin is available in Neo4j."""
    try:
        with driver.session() as session:
            result = session.run(
                "SHOW PROCEDURES YIELD name WHERE name STARTS WITH 'n10s' "
                "RETURN count(name) AS count"
            )
            count = result.single()["count"]
            return count > 0
    except Exception:
        return False


# Skip all tests if Neo4j or n10s is not available
pytestmark = pytest.mark.skipif(
    not is_neo4j_available() or not is_n10s_available(GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))) if is_neo4j_available() else True,
    reason="Neo4j with n10s plugin not available. Start with: docker compose -f infra/docker-compose.hcg.dev.yml up -d"
)


@pytest.fixture(scope="module")
def neo4j_driver():
    """Create a Neo4j driver for testing."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    yield driver
    driver.close()


@pytest.fixture(scope="module")
def clean_graph(neo4j_driver):
    """Clear the Neo4j graph before tests."""
    with neo4j_driver.session() as session:
        # Clear all data
        session.run("MATCH (n) DETACH DELETE n")

        # Clear n10s config if it exists
        try:
            session.run("CALL n10s.graphconfig.drop()")
        except Exception:
            pass  # Config may not exist

        # Clear SHACL shapes if they exist
        try:
            result = session.run(
                "SHOW PROCEDURES YIELD name WHERE name = 'n10s.validation.shacl.clear' "
                "RETURN count(name) AS count"
            )
            if result.single()["count"] > 0:
                session.run("CALL n10s.validation.shacl.clear()")
        except Exception:
            pass  # Procedure may not exist or shapes may not be loaded

    yield

    # Cleanup after tests
    with neo4j_driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        try:
            session.run("CALL n10s.graphconfig.drop()")
        except Exception:
            pass


@pytest.fixture(scope="module")
def initialized_n10s(neo4j_driver, clean_graph):
    """Initialize n10s graph configuration."""
    with neo4j_driver.session() as session:
        # Initialize n10s with proper configuration
        session.run(
            """
            CALL n10s.graphconfig.init({
                handleVocabUris: 'MAP',
                handleRDFTypes: 'LABELS',
                handleMultival: 'ARRAY',
                keepLangTag: true
            })
            """
        )

        # Add namespace prefix
        try:
            session.run("CALL n10s.nsprefixes.remove('logos')")
        except Exception:
            pass
        session.run("CALL n10s.nsprefixes.add('logos', 'http://logos.ontology/')")

    yield

    # Cleanup is handled by clean_graph fixture


@pytest.fixture(scope="module")
def loaded_shacl_shapes(neo4j_driver, initialized_n10s):
    """Load SHACL shapes into Neo4j via n10s."""
    shapes_file = REPO_ROOT / "ontology" / "shacl_shapes.ttl"

    # Read and rewrite shapes to use Neo4j graph schema namespace
    shapes_text = shapes_file.read_text(encoding="utf-8")
    shapes_rewritten = shapes_text.replace("http://logos.ontology/", "neo4j://graph.schema#")

    with neo4j_driver.session() as session:
        # Import SHACL shapes
        session.run(
            """
            CALL n10s.validation.shacl.import.inline($rdf, "Turtle")
            """,
            rdf=shapes_rewritten
        )

        # Verify shapes are loaded
        result = session.run("CALL n10s.validation.shacl.listShapes()")
        shapes_count = len(list(result))

        if shapes_count == 0:
            pytest.fail("Failed to load SHACL shapes - no shapes found")

    yield shapes_count


class TestN10sAvailability:
    """Test that n10s plugin is available and functioning."""

    def test_n10s_procedures_available(self, neo4j_driver):
        """Test that n10s procedures are available in Neo4j."""
        with neo4j_driver.session() as session:
            result = session.run(
                "SHOW PROCEDURES YIELD name WHERE name STARTS WITH 'n10s' "
                "RETURN name ORDER BY name"
            )
            procedures = [record["name"] for record in result]

            assert len(procedures) > 0, "No n10s procedures found"

            # Check for key procedures
            assert any("n10s.graphconfig" in p for p in procedures), \
                "n10s.graphconfig procedures missing"
            assert any("n10s.validation.shacl" in p for p in procedures), \
                "n10s.validation.shacl procedures missing"

            print(f"✓ Found {len(procedures)} n10s procedures")


class TestSHACLShapesLoading:
    """Test loading SHACL shapes into Neo4j via n10s."""

    def test_n10s_initialization(self, initialized_n10s, neo4j_driver):
        """Test that n10s graph configuration is initialized."""
        with neo4j_driver.session() as session:
            result = session.run("CALL n10s.graphconfig.show() YIELD param, value")
            config = {record["param"]: record["value"] for record in result}

            assert len(config) > 0, "n10s configuration is empty"
            assert "handleVocabUris" in config, "handleVocabUris not configured"

            print(f"✓ n10s configured with {len(config)} parameters")

    def test_shacl_shapes_loaded(self, loaded_shacl_shapes):
        """Test that SHACL shapes are loaded into Neo4j."""
        assert loaded_shacl_shapes > 0, "No SHACL shapes loaded"
        print(f"✓ Loaded {loaded_shacl_shapes} SHACL shapes into Neo4j")


class TestValidDataValidation:
    """Test validation of valid test data."""

    def test_valid_entities_pass_validation(self, neo4j_driver, loaded_shacl_shapes):
        """Test that valid entity data passes SHACL validation via Neo4j."""
        valid_file = REPO_ROOT / "tests" / "phase1" / "fixtures" / "valid_entities.ttl"

        # Load valid data
        valid_text = valid_file.read_text(encoding="utf-8")
        valid_rewritten = valid_text.replace("http://logos.ontology/", "neo4j://graph.schema#")

        with neo4j_driver.session() as session:
            # Clear previous data (keep shapes)
            session.run(
                """
                MATCH (n)
                WHERE NOT (n:sh__NodeShape OR n:sh__PropertyShape OR n:rdf__Property)
                DETACH DELETE n
                """
            )

            # Import valid data
            result = session.run(
                """
                CALL n10s.rdf.import.inline($rdf, "Turtle")
                YIELD terminationStatus, triplesLoaded
                RETURN terminationStatus, triplesLoaded
                """,
                rdf=valid_rewritten
            )
            record = result.single()
            assert record["terminationStatus"] == "OK", \
                f"Failed to load valid data: {record['terminationStatus']}"

            triples_loaded = record["triplesLoaded"]
            print(f"✓ Loaded {triples_loaded} valid data triples")

            # Run SHACL validation
            result = session.run(
                """
                CALL n10s.validation.shacl.validate()
                YIELD focusNode, propertyShape, severity, resultMessage
                RETURN focusNode, propertyShape, severity, resultMessage
                """
            )

            violations = list(result)

            if violations:
                violation_messages = []
                for v in violations:
                    violation_messages.append(
                        f"  - {v['focusNode']}: {v['resultMessage']}"
                    )
                pytest.fail(
                    f"Valid data should pass validation but found {len(violations)} violations:\n"
                    + "\n".join(violation_messages)
                )

            print("✓ Valid entities passed SHACL validation via Neo4j")


class TestInvalidDataValidation:
    """Test validation of invalid test data."""

    def test_invalid_entities_fail_validation(self, neo4j_driver, loaded_shacl_shapes):
        """Test that invalid entity data fails SHACL validation via Neo4j."""
        invalid_file = REPO_ROOT / "tests" / "phase1" / "fixtures" / "invalid_entities.ttl"

        # Load invalid data
        invalid_text = invalid_file.read_text(encoding="utf-8")
        invalid_rewritten = invalid_text.replace("http://logos.ontology/", "neo4j://graph.schema#")

        with neo4j_driver.session() as session:
            # Clear previous data (keep shapes)
            session.run(
                """
                MATCH (n)
                WHERE NOT (n:sh__NodeShape OR n:sh__PropertyShape OR n:rdf__Property)
                DETACH DELETE n
                """
            )

            # Import invalid data
            result = session.run(
                """
                CALL n10s.rdf.import.inline($rdf, "Turtle")
                YIELD terminationStatus, triplesLoaded
                RETURN terminationStatus, triplesLoaded
                """,
                rdf=invalid_rewritten
            )
            record = result.single()
            assert record["terminationStatus"] == "OK", \
                f"Failed to load invalid data: {record['terminationStatus']}"

            triples_loaded = record["triplesLoaded"]
            print(f"✓ Loaded {triples_loaded} invalid data triples")

            # Run SHACL validation
            result = session.run(
                """
                CALL n10s.validation.shacl.validate()
                YIELD focusNode, propertyShape, severity, resultMessage
                RETURN focusNode, propertyShape, severity, resultMessage
                """
            )

            violations = list(result)

            assert len(violations) > 0, \
                "Invalid data should fail validation but no violations found"

            print(f"✓ Invalid entities correctly failed SHACL validation with {len(violations)} violations:")
            for i, v in enumerate(violations[:5], 1):  # Show first 5 violations
                print(f"  {i}. {v['focusNode']}: {v['resultMessage']}")
            if len(violations) > 5:
                print(f"  ... and {len(violations) - 5} more violations")


class TestBadWriteRejection:
    """Test that bad writes through Neo4j are rejected by SHACL validation."""

    def test_wrong_uuid_prefix_rejected(self, neo4j_driver, loaded_shacl_shapes):
        """Test that entity with wrong UUID prefix is rejected by SHACL validation."""
        with neo4j_driver.session() as session:
            # Clear previous data (keep shapes)
            session.run(
                """
                MATCH (n)
                WHERE NOT (n:sh__NodeShape OR n:sh__PropertyShape OR n:rdf__Property)
                DETACH DELETE n
                """
            )

            # Try to create entity with wrong UUID prefix via RDF
            bad_rdf = """
                @prefix logos: <neo4j://graph.schema#> .
                @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

                logos:entity-bad-prefix a logos:Entity ;
                    logos:uuid "wrong-prefix-123" ;
                    logos:name "BadPrefixEntity" .
            """

            # Import the bad data
            result = session.run(
                """
                CALL n10s.rdf.import.inline($rdf, "Turtle")
                YIELD terminationStatus, triplesLoaded
                RETURN terminationStatus, triplesLoaded
                """,
                rdf=bad_rdf
            )
            record = result.single()
            assert record["terminationStatus"] == "OK", \
                "Failed to load data for validation test"

            # Run SHACL validation - should fail
            result = session.run(
                """
                CALL n10s.validation.shacl.validate()
                YIELD focusNode, propertyShape, severity, resultMessage
                RETURN focusNode, propertyShape, severity, resultMessage
                """
            )

            violations = list(result)

            # Check that we have violations related to UUID pattern
            uuid_violations = [
                v for v in violations
                if "uuid" in str(v.get("propertyShape", "")).lower()
                or "pattern" in str(v.get("resultMessage", "")).lower()
            ]

            assert len(uuid_violations) > 0, \
                f"Expected UUID pattern violation but found {len(violations)} violations of other types"

            print("✓ Wrong UUID prefix correctly rejected by SHACL validation")
            print(f"  Violation: {uuid_violations[0]['resultMessage']}")

    def test_missing_required_field_rejected(self, neo4j_driver, loaded_shacl_shapes):
        """Test that entity missing required field is rejected by SHACL validation."""
        with neo4j_driver.session() as session:
            # Clear previous data (keep shapes)
            session.run(
                """
                MATCH (n)
                WHERE NOT (n:sh__NodeShape OR n:sh__PropertyShape OR n:rdf__Property)
                DETACH DELETE n
                """
            )

            # Try to create entity without UUID (required field) via RDF
            bad_rdf = """
                @prefix logos: <neo4j://graph.schema#> .

                logos:entity-no-uuid a logos:Entity ;
                    logos:name "NoUUIDEntity" .
            """

            # Import the bad data
            result = session.run(
                """
                CALL n10s.rdf.import.inline($rdf, "Turtle")
                YIELD terminationStatus, triplesLoaded
                RETURN terminationStatus, triplesLoaded
                """,
                rdf=bad_rdf
            )
            record = result.single()
            assert record["terminationStatus"] == "OK", \
                "Failed to load data for validation test"

            # Run SHACL validation - should fail
            result = session.run(
                """
                CALL n10s.validation.shacl.validate()
                YIELD focusNode, propertyShape, severity, resultMessage
                RETURN focusNode, propertyShape, severity, resultMessage
                """
            )

            violations = list(result)

            # Check that we have violations related to missing UUID
            uuid_violations = [
                v for v in violations
                if "uuid" in str(v.get("propertyShape", "")).lower()
                or "minCount" in str(v.get("resultMessage", "")).lower()
            ]

            assert len(uuid_violations) > 0, \
                f"Expected missing UUID violation but found {len(violations)} violations of other types"

            print("✓ Missing required UUID field correctly rejected by SHACL validation")
            print(f"  Violation: {uuid_violations[0]['resultMessage']}")

    def test_concept_missing_name_rejected(self, neo4j_driver, loaded_shacl_shapes):
        """Test that Concept missing required name field is rejected."""
        with neo4j_driver.session() as session:
            # Clear previous data (keep shapes)
            session.run(
                """
                MATCH (n)
                WHERE NOT (n:sh__NodeShape OR n:sh__PropertyShape OR n:rdf__Property)
                DETACH DELETE n
                """
            )

            # Try to create concept without name (required field) via RDF
            bad_rdf = """
                @prefix logos: <neo4j://graph.schema#> .

                logos:concept-no-name a logos:Concept ;
                    logos:uuid "concept-missing-name-123" .
            """

            # Import the bad data
            result = session.run(
                """
                CALL n10s.rdf.import.inline($rdf, "Turtle")
                YIELD terminationStatus, triplesLoaded
                RETURN terminationStatus, triplesLoaded
                """,
                rdf=bad_rdf
            )
            record = result.single()
            assert record["terminationStatus"] == "OK", \
                "Failed to load data for validation test"

            # Run SHACL validation - should fail
            result = session.run(
                """
                CALL n10s.validation.shacl.validate()
                YIELD focusNode, propertyShape, severity, resultMessage
                RETURN focusNode, propertyShape, severity, resultMessage
                """
            )

            violations = list(result)

            # Check that we have violations related to missing name
            name_violations = [
                v for v in violations
                if "name" in str(v.get("propertyShape", "")).lower()
                or "minCount" in str(v.get("resultMessage", "")).lower()
            ]

            assert len(name_violations) > 0, \
                f"Expected missing name violation but found {len(violations)} violations of other types"

            print("✓ Missing required name field correctly rejected by SHACL validation")
            print(f"  Violation: {name_violations[0]['resultMessage']}")

    def test_negative_spatial_property_rejected(self, neo4j_driver, loaded_shacl_shapes):
        """Test that entity with negative spatial property is rejected."""
        with neo4j_driver.session() as session:
            # Clear previous data (keep shapes)
            session.run(
                """
                MATCH (n)
                WHERE NOT (n:sh__NodeShape OR n:sh__PropertyShape OR n:rdf__Property)
                DETACH DELETE n
                """
            )

            # Try to create entity with negative width via RDF
            bad_rdf = """
                @prefix logos: <neo4j://graph.schema#> .
                @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

                logos:entity-negative-width a logos:Entity ;
                    logos:uuid "entity-negative-spatial" ;
                    logos:name "NegativeSpatial" ;
                    logos:width "-0.5"^^xsd:decimal .
            """

            # Import the bad data
            result = session.run(
                """
                CALL n10s.rdf.import.inline($rdf, "Turtle")
                YIELD terminationStatus, triplesLoaded
                RETURN terminationStatus, triplesLoaded
                """,
                rdf=bad_rdf
            )
            record = result.single()
            assert record["terminationStatus"] == "OK", \
                "Failed to load data for validation test"

            # Run SHACL validation - should fail
            result = session.run(
                """
                CALL n10s.validation.shacl.validate()
                YIELD focusNode, propertyShape, severity, resultMessage
                RETURN focusNode, propertyShape, severity, resultMessage
                """
            )

            violations = list(result)

            # Check that we have violations related to negative values
            spatial_violations = [
                v for v in violations
                if "width" in str(v.get("propertyShape", "")).lower()
                or "minInclusive" in str(v.get("resultMessage", "")).lower()
            ]

            assert len(spatial_violations) > 0, \
                f"Expected negative spatial value violation but found {len(violations)} violations of other types"

            print("✓ Negative spatial property correctly rejected by SHACL validation")
            print(f"  Violation: {spatial_violations[0]['resultMessage']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
