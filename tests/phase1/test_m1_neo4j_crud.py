"""
M1 Functional Test: Neo4j CRUD and Relationship Traversal

Tests the M1 milestone requirements:
- Start docker-compose.hcg.dev.yml, load core_ontology.cypher and test_data_pick_and_place.cypher
- Create Entity/Concept/State/Process with correct UUID prefixes
- Verify constraints and uniqueness
- Create IS_A, HAS_STATE, CAUSES, PART_OF relationships
- Traverse relationships (type lookup, current state, causal chains)
- Fail on constraint violations

Reference: docs/PHASE1_VERIFY.md - M1 checklist
"""

import os
from pathlib import Path
from uuid import uuid4

import pytest
from neo4j.exceptions import ClientError

from logos_test_utils.docker import is_container_running
from logos_test_utils.neo4j import (
    get_neo4j_config,
    get_neo4j_driver,
    load_cypher_file,
)

NEO4J_CONFIG = get_neo4j_config()
REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_M1_E2E = os.getenv("RUN_M1_E2E") not in {None, "", "0", "false", "False"}

if not RUN_M1_E2E or not is_container_running(NEO4J_CONFIG.container):
    pytest.skip(
        "M1 CRUD suite requires RUN_M1_E2E=1 and the shared stack running.",
        allow_module_level=True,
    )


@pytest.fixture(scope="module")
def neo4j_driver():
    """Provide a Neo4j driver tied to the shared stack."""

    driver = get_neo4j_driver(NEO4J_CONFIG)
    yield driver
    driver.close()


@pytest.fixture(scope="module")
def loaded_ontology(neo4j_driver):
    """Load core ontology into Neo4j before tests."""
    ontology_path = REPO_ROOT / "ontology" / "core_ontology.cypher"

    # First, clean the database
    with neo4j_driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

    result = load_cypher_file(ontology_path, config=NEO4J_CONFIG, timeout=120)
    if result.returncode != 0:
        pytest.fail(f"Failed to load ontology: {result.stderr}")
    return True


@pytest.fixture(scope="module")
def loaded_test_data(neo4j_driver, loaded_ontology):
    """Load test data into Neo4j before tests."""
    test_data_path = REPO_ROOT / "ontology" / "test_data_pick_and_place.cypher"
    result = load_cypher_file(test_data_path, config=NEO4J_CONFIG, timeout=120)
    if result.returncode != 0:
        pytest.fail(f"Failed to load test data: {result.stderr}")
    return True


class TestOntologyLoading:
    """Test that ontology and test data load successfully."""

    def test_ontology_loaded(self, loaded_ontology):
        """Verify core ontology is loaded."""
        assert loaded_ontology is True

    def test_test_data_loaded(self, loaded_test_data):
        """Verify test data is loaded."""
        assert loaded_test_data is True

    def test_constraints_exist(self, neo4j_driver, loaded_ontology):
        """Verify UUID constraints are created."""
        with neo4j_driver.session() as session:
            result = session.run("SHOW CONSTRAINTS")
            constraints = [record["name"] for record in result]

            # Check for LOGOS constraints
            assert any(
                "logos_entity_uuid" in c for c in constraints
            ), "Entity UUID constraint missing"
            assert any(
                "logos_concept_uuid" in c for c in constraints
            ), "Concept UUID constraint missing"
            assert any(
                "logos_state_uuid" in c for c in constraints
            ), "State UUID constraint missing"
            assert any(
                "logos_process_uuid" in c for c in constraints
            ), "Process UUID constraint missing"
            assert any(
                "logos_concept_name" in c for c in constraints
            ), "Concept name constraint missing"

    def test_indexes_exist(self, neo4j_driver, loaded_ontology):
        """Verify indexes are created."""
        with neo4j_driver.session() as session:
            result = session.run("SHOW INDEXES")
            indexes = [record["name"] for record in result]

            # Check for LOGOS indexes
            assert any(
                "logos_entity_name" in i for i in indexes
            ), "Entity name index missing"
            assert any(
                "logos_state_timestamp" in i for i in indexes
            ), "State timestamp index missing"
            assert any(
                "logos_process_timestamp" in i for i in indexes
            ), "Process timestamp index missing"


class TestEntityCreation:
    """Test Entity node creation with UUID constraints."""

    def test_create_entity_with_valid_uuid(self, neo4j_driver, loaded_ontology):
        """Test creating entity with valid UUID prefix."""
        test_uuid = f"entity-test-{uuid4()}"

        with neo4j_driver.session() as session:
            result = session.run(
                "CREATE (e:Entity {uuid: $uuid, name: $name, created_at: datetime()}) RETURN e",
                uuid=test_uuid,
                name="TestEntity01",
            )
            entity = result.single()
            assert entity is not None
            assert entity["e"]["uuid"] == test_uuid

            # Cleanup
            session.run("MATCH (e:Entity {uuid: $uuid}) DELETE e", uuid=test_uuid)

    def test_create_entity_duplicate_uuid_fails(self, neo4j_driver, loaded_ontology):
        """Test that duplicate UUID fails with constraint violation."""
        test_uuid = f"entity-test-duplicate-{uuid4()}"

        with neo4j_driver.session() as session:
            # Create first entity
            session.run(
                "CREATE (e:Entity {uuid: $uuid, name: $name})",
                uuid=test_uuid,
                name="TestEntity01",
            )

            # Try to create duplicate - should fail
            with pytest.raises(ClientError) as exc_info:
                session.run(
                    "CREATE (e:Entity {uuid: $uuid, name: $name})",
                    uuid=test_uuid,
                    name="TestEntity02",
                )

            assert (
                "ConstraintValidationFailed" in str(exc_info.value)
                or "already exists" in str(exc_info.value).lower()
            )

            # Cleanup
            session.run("MATCH (e:Entity {uuid: $uuid}) DELETE e", uuid=test_uuid)


class TestConceptCreation:
    """Test Concept node creation with UUID and name constraints."""

    def test_create_concept_with_valid_uuid(self, neo4j_driver, loaded_ontology):
        """Test creating concept with valid UUID prefix."""
        test_uuid = f"concept-test-{uuid4()}"
        test_name = f"TestConcept{uuid4().hex[:8]}"

        with neo4j_driver.session() as session:
            result = session.run(
                "CREATE (c:Concept {uuid: $uuid, name: $name}) RETURN c",
                uuid=test_uuid,
                name=test_name,
            )
            concept = result.single()
            assert concept is not None
            assert concept["c"]["uuid"] == test_uuid
            assert concept["c"]["name"] == test_name

            # Cleanup
            session.run("MATCH (c:Concept {uuid: $uuid}) DELETE c", uuid=test_uuid)

    def test_create_concept_duplicate_name_fails(self, neo4j_driver, loaded_ontology):
        """Test that duplicate concept name fails with constraint violation."""
        test_uuid1 = f"concept-test-{uuid4()}"
        test_uuid2 = f"concept-test-{uuid4()}"
        test_name = f"TestConceptDuplicate{uuid4().hex[:8]}"

        with neo4j_driver.session() as session:
            # Create first concept
            session.run(
                "CREATE (c:Concept {uuid: $uuid, name: $name})",
                uuid=test_uuid1,
                name=test_name,
            )

            # Try to create duplicate name - should fail
            with pytest.raises(ClientError) as exc_info:
                session.run(
                    "CREATE (c:Concept {uuid: $uuid, name: $name})",
                    uuid=test_uuid2,
                    name=test_name,
                )

            assert (
                "ConstraintValidationFailed" in str(exc_info.value)
                or "already exists" in str(exc_info.value).lower()
            )

            # Cleanup
            session.run("MATCH (c:Concept {uuid: $uuid}) DELETE c", uuid=test_uuid1)


class TestStateCreation:
    """Test State node creation with UUID constraints."""

    def test_create_state_with_valid_uuid(self, neo4j_driver, loaded_ontology):
        """Test creating state with valid UUID prefix."""
        test_uuid = f"state-test-{uuid4()}"

        with neo4j_driver.session() as session:
            result = session.run(
                "CREATE (s:State {uuid: $uuid, timestamp: datetime()}) RETURN s",
                uuid=test_uuid,
            )
            state = result.single()
            assert state is not None
            assert state["s"]["uuid"] == test_uuid
            assert state["s"]["timestamp"] is not None

            # Cleanup
            session.run("MATCH (s:State {uuid: $uuid}) DELETE s", uuid=test_uuid)

    def test_create_state_duplicate_uuid_fails(self, neo4j_driver, loaded_ontology):
        """Test that duplicate state UUID fails."""
        test_uuid = f"state-test-duplicate-{uuid4()}"

        with neo4j_driver.session() as session:
            # Create first state
            session.run(
                "CREATE (s:State {uuid: $uuid, timestamp: datetime()})", uuid=test_uuid
            )

            # Try to create duplicate
            with pytest.raises(ClientError) as exc_info:
                session.run(
                    "CREATE (s:State {uuid: $uuid, timestamp: datetime()})",
                    uuid=test_uuid,
                )

            assert (
                "ConstraintValidationFailed" in str(exc_info.value)
                or "already exists" in str(exc_info.value).lower()
            )

            # Cleanup
            session.run("MATCH (s:State {uuid: $uuid}) DELETE s", uuid=test_uuid)


class TestProcessCreation:
    """Test Process node creation with UUID constraints."""

    def test_create_process_with_valid_uuid(self, neo4j_driver, loaded_ontology):
        """Test creating process with valid UUID prefix."""
        test_uuid = f"process-test-{uuid4()}"

        with neo4j_driver.session() as session:
            result = session.run(
                "CREATE (p:Process {uuid: $uuid, start_time: datetime()}) RETURN p",
                uuid=test_uuid,
            )
            process = result.single()
            assert process is not None
            assert process["p"]["uuid"] == test_uuid
            assert process["p"]["start_time"] is not None

            # Cleanup
            session.run("MATCH (p:Process {uuid: $uuid}) DELETE p", uuid=test_uuid)

    def test_create_process_duplicate_uuid_fails(self, neo4j_driver, loaded_ontology):
        """Test that duplicate process UUID fails."""
        test_uuid = f"process-test-duplicate-{uuid4()}"

        with neo4j_driver.session() as session:
            # Create first process
            session.run(
                "CREATE (p:Process {uuid: $uuid, start_time: datetime()})",
                uuid=test_uuid,
            )

            # Try to create duplicate
            with pytest.raises(ClientError) as exc_info:
                session.run(
                    "CREATE (p:Process {uuid: $uuid, start_time: datetime()})",
                    uuid=test_uuid,
                )

            assert (
                "ConstraintValidationFailed" in str(exc_info.value)
                or "already exists" in str(exc_info.value).lower()
            )

            # Cleanup
            session.run("MATCH (p:Process {uuid: $uuid}) DELETE p", uuid=test_uuid)


class TestRelationshipCreation:
    """Test relationship creation between nodes."""

    def test_create_is_a_relationship(self, neo4j_driver, loaded_ontology):
        """Test creating IS_A relationship between Entity and Concept."""
        entity_uuid = f"entity-test-{uuid4()}"
        concept_uuid = f"concept-test-{uuid4()}"
        concept_name = f"TestConcept{uuid4().hex[:8]}"

        with neo4j_driver.session() as session:
            # Create nodes
            session.run(
                "CREATE (e:Entity {uuid: $e_uuid, name: $e_name})",
                e_uuid=entity_uuid,
                e_name="TestEntity",
            )
            session.run(
                "CREATE (c:Concept {uuid: $c_uuid, name: $c_name})",
                c_uuid=concept_uuid,
                c_name=concept_name,
            )

            # Create relationship
            result = session.run(
                """
                MATCH (e:Entity {uuid: $e_uuid})
                MATCH (c:Concept {uuid: $c_uuid})
                CREATE (e)-[r:IS_A]->(c)
                RETURN r
                """,
                e_uuid=entity_uuid,
                c_uuid=concept_uuid,
            )
            rel = result.single()
            assert rel is not None

            # Cleanup
            session.run(
                "MATCH (e:Entity {uuid: $e_uuid})-[r:IS_A]->(c:Concept {uuid: $c_uuid}) DELETE r, e, c",
                e_uuid=entity_uuid,
                c_uuid=concept_uuid,
            )

    def test_create_has_state_relationship(self, neo4j_driver, loaded_ontology):
        """Test creating HAS_STATE relationship between Entity and State."""
        entity_uuid = f"entity-test-{uuid4()}"
        state_uuid = f"state-test-{uuid4()}"

        with neo4j_driver.session() as session:
            # Create nodes
            session.run(
                "CREATE (e:Entity {uuid: $e_uuid, name: $e_name})",
                e_uuid=entity_uuid,
                e_name="TestEntity",
            )
            session.run(
                "CREATE (s:State {uuid: $s_uuid, timestamp: datetime()})",
                s_uuid=state_uuid,
            )

            # Create relationship
            result = session.run(
                """
                MATCH (e:Entity {uuid: $e_uuid})
                MATCH (s:State {uuid: $s_uuid})
                CREATE (e)-[r:HAS_STATE]->(s)
                RETURN r
                """,
                e_uuid=entity_uuid,
                s_uuid=state_uuid,
            )
            rel = result.single()
            assert rel is not None

            # Cleanup
            session.run(
                "MATCH (e:Entity {uuid: $e_uuid})-[r:HAS_STATE]->(s:State {uuid: $s_uuid}) DELETE r, e, s",
                e_uuid=entity_uuid,
                s_uuid=state_uuid,
            )

    def test_create_causes_relationship(self, neo4j_driver, loaded_ontology):
        """Test creating CAUSES relationship between Process and State."""
        process_uuid = f"process-test-{uuid4()}"
        state_uuid = f"state-test-{uuid4()}"

        with neo4j_driver.session() as session:
            # Create nodes
            session.run(
                "CREATE (p:Process {uuid: $p_uuid, start_time: datetime()})",
                p_uuid=process_uuid,
            )
            session.run(
                "CREATE (s:State {uuid: $s_uuid, timestamp: datetime()})",
                s_uuid=state_uuid,
            )

            # Create relationship
            result = session.run(
                """
                MATCH (p:Process {uuid: $p_uuid})
                MATCH (s:State {uuid: $s_uuid})
                CREATE (p)-[r:CAUSES]->(s)
                RETURN r
                """,
                p_uuid=process_uuid,
                s_uuid=state_uuid,
            )
            rel = result.single()
            assert rel is not None

            # Cleanup
            session.run(
                "MATCH (p:Process {uuid: $p_uuid})-[r:CAUSES]->(s:State {uuid: $s_uuid}) DELETE r, p, s",
                p_uuid=process_uuid,
                s_uuid=state_uuid,
            )

    def test_create_part_of_relationship(self, neo4j_driver, loaded_ontology):
        """Test creating PART_OF relationship between entities."""
        part_uuid = f"entity-test-part-{uuid4()}"
        whole_uuid = f"entity-test-whole-{uuid4()}"

        with neo4j_driver.session() as session:
            # Create nodes
            session.run(
                "CREATE (e:Entity {uuid: $e_uuid, name: $e_name})",
                e_uuid=part_uuid,
                e_name="TestPart",
            )
            session.run(
                "CREATE (e:Entity {uuid: $e_uuid, name: $e_name})",
                e_uuid=whole_uuid,
                e_name="TestWhole",
            )

            # Create relationship
            result = session.run(
                """
                MATCH (part:Entity {uuid: $part_uuid})
                MATCH (whole:Entity {uuid: $whole_uuid})
                CREATE (part)-[r:PART_OF]->(whole)
                RETURN r
                """,
                part_uuid=part_uuid,
                whole_uuid=whole_uuid,
            )
            rel = result.single()
            assert rel is not None

            # Cleanup
            session.run(
                "MATCH (part:Entity {uuid: $part_uuid})-[r:PART_OF]->(whole:Entity {uuid: $whole_uuid}) DELETE r, part, whole",
                part_uuid=part_uuid,
                whole_uuid=whole_uuid,
            )


class TestRelationshipTraversal:
    """Test traversing relationships in the graph."""

    def test_traverse_is_a_for_type_lookup(self, neo4j_driver, loaded_test_data):
        """Test traversing IS_A relationship to find entity type."""
        with neo4j_driver.session() as session:
            # Find robot arm and its type
            result = session.run(
                """
                MATCH (e:Entity {uuid: 'entity-robot-arm-01'})-[:IS_A]->(c:Concept)
                RETURN e.name AS entity_name, c.name AS concept_name
                """
            )
            record = result.single()
            assert record is not None
            assert record["entity_name"] == "RobotArm01"
            assert record["concept_name"] == "Manipulator"

    def test_traverse_has_state_for_current_state(self, neo4j_driver, loaded_test_data):
        """Test traversing HAS_STATE relationship to find current state."""
        with neo4j_driver.session() as session:
            # Find robot arm's current state
            result = session.run(
                """
                MATCH (e:Entity {uuid: 'entity-robot-arm-01'})-[:HAS_STATE]->(s:State)
                RETURN s.name AS state_name, s.timestamp AS timestamp
                ORDER BY s.timestamp DESC
                LIMIT 1
                """
            )
            record = result.single()
            assert record is not None
            assert record["state_name"] == "ArmHomeState"

    def test_traverse_causes_for_causal_chain(self, neo4j_driver, loaded_test_data):
        """Test traversing CAUSES relationships to trace causal chain."""
        with neo4j_driver.session() as session:
            # Find what process causes the gripper to close
            result = session.run(
                """
                MATCH (p:Process)-[:CAUSES]->(s:State {uuid: 'state-gripper-closed-01'})
                RETURN p.name AS process_name, s.name AS state_name
                """
            )
            record = result.single()
            assert record is not None
            assert record["process_name"] == "GraspRedBlock"
            assert record["state_name"] == "GripperClosedState"

    def test_traverse_multi_hop_causal_chain(self, neo4j_driver, loaded_test_data):
        """Test traversing multi-hop causal chains."""
        with neo4j_driver.session() as session:
            # Find the causal chain from initial grasp to final placement
            result = session.run(
                """
                MATCH path = (s1:State {uuid: 'state-gripper-open-01'})-[:PRECEDES*1..5]->(s2:State)
                RETURN s2.name AS final_state, length(path) AS chain_length
                ORDER BY chain_length DESC
                LIMIT 1
                """
            )
            record = result.single()
            assert record is not None
            # Should find a state in the causal chain
            assert record["chain_length"] > 0

    def test_traverse_part_of_for_composition(self, neo4j_driver, loaded_test_data):
        """Test traversing PART_OF relationships for composition hierarchy."""
        with neo4j_driver.session() as session:
            # Find parts of robot arm
            result = session.run(
                """
                MATCH (part:Entity)-[:PART_OF]->(whole:Entity {uuid: 'entity-robot-arm-01'})
                RETURN part.name AS part_name
                ORDER BY part.name
                """
            )
            parts = [record["part_name"] for record in result]

            # Should include gripper and joints
            assert "Gripper01" in parts
            assert any("Joint" in p for p in parts)
            assert len(parts) >= 4  # Gripper + at least 3 joints


class TestQueryOperations:
    """Test various query operations on the graph."""

    def test_query_entity_by_uuid(self, neo4j_driver, loaded_test_data):
        """Test querying entity by UUID."""
        with neo4j_driver.session() as session:
            result = session.run(
                "MATCH (e:Entity {uuid: $uuid}) RETURN e.name AS name",
                uuid="entity-robot-arm-01",
            )
            record = result.single()
            assert record is not None
            assert record["name"] == "RobotArm01"

    def test_query_entity_by_name(self, neo4j_driver, loaded_test_data):
        """Test querying entity by name."""
        with neo4j_driver.session() as session:
            result = session.run(
                "MATCH (e:Entity {name: $name}) RETURN e.uuid AS uuid",
                name="RobotArm01",
            )
            record = result.single()
            assert record is not None
            assert record["uuid"] == "entity-robot-arm-01"

    def test_query_states_by_timestamp(self, neo4j_driver, loaded_test_data):
        """Test querying states by timestamp range."""
        with neo4j_driver.session() as session:
            result = session.run(
                """
                MATCH (s:State)
                WHERE s.timestamp IS NOT NULL
                RETURN count(s) AS state_count
                """
            )
            record = result.single()
            assert record is not None
            assert record["state_count"] > 0

    def test_query_processes_by_start_time(self, neo4j_driver, loaded_test_data):
        """Test querying processes by start time."""
        with neo4j_driver.session() as session:
            result = session.run(
                """
                MATCH (p:Process)
                WHERE p.start_time IS NOT NULL
                RETURN count(p) AS process_count
                """
            )
            record = result.single()
            assert record is not None
            assert record["process_count"] > 0

    def test_count_nodes_by_type(self, neo4j_driver, loaded_test_data):
        """Test counting nodes by type."""
        with neo4j_driver.session() as session:
            # Count entities
            result = session.run("MATCH (e:Entity) RETURN count(e) AS count")
            entity_count = result.single()["count"]
            assert entity_count > 0

            # Count concepts
            result = session.run("MATCH (c:Concept) RETURN count(c) AS count")
            concept_count = result.single()["count"]
            assert concept_count > 0

            # Count states
            result = session.run("MATCH (s:State) RETURN count(s) AS count")
            state_count = result.single()["count"]
            assert state_count > 0

            # Count processes
            result = session.run("MATCH (p:Process) RETURN count(p) AS count")
            process_count = result.single()["count"]
            assert process_count > 0
