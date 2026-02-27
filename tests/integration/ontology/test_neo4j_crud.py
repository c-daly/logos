"""
M1 Functional Test: Neo4j CRUD and Relationship Traversal

Tests the M1 milestone requirements with FLEXIBLE ONTOLOGY:
- Start docker-compose.hcg.dev.yml, load core_ontology.cypher and test_data_pick_and_place.cypher
- Create Entity/Concept/State/Process using :Node label with type/ancestors properties
- Verify constraints and uniqueness
- Create IS_A, HAS_STATE, CAUSES, PART_OF relationships
- Traverse relationships (type lookup, current state, causal chains)
- Fail on constraint violations

FLEXIBLE ONTOLOGY:
All nodes use the :Node label with these properties:
- uuid: unique identifier
- name: human-readable name
- is_type_definition: boolean (true for types, false for instances)
- type: immediate type name
- ancestors: list of ancestor types up to bootstrap root

Reference: docs/PHASE1_VERIFY.md - M1 checklist
Reference: docs/plans/2025-12-30-flexible-ontology-design.md
"""

from uuid import uuid4

import pytest
from neo4j.exceptions import ClientError

from logos_test_utils.docker import is_container_running
from logos_test_utils.env import get_repo_root
from logos_test_utils.neo4j import (
    get_neo4j_config,
    get_neo4j_driver,
    load_cypher_file,
)

NEO4J_CONFIG = get_neo4j_config()
REPO_ROOT = get_repo_root()

if not is_container_running(NEO4J_CONFIG.container):
    pytest.skip(
        "Neo4j container not running. Start with: ./tests/e2e/run_e2e.sh up",
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
        """Verify UUID constraint on :Node label exists (flexible ontology)."""
        with neo4j_driver.session() as session:
            result = session.run("SHOW CONSTRAINTS")
            constraints = [record["name"] for record in result]

            # Check for flexible ontology constraint (single UUID constraint on :Node)
            assert any(
                "logos_node_uuid" in c for c in constraints
            ), "Node UUID constraint missing"

    def test_indexes_exist(self, neo4j_driver, loaded_ontology):
        """Verify indexes for flexible ontology exist."""
        with neo4j_driver.session() as session:
            result = session.run("SHOW INDEXES")
            indexes = [record["name"] for record in result]

            # Check for flexible ontology indexes
            assert any(
                "logos_node_type" in i for i in indexes
            ), "Node type index missing"
            assert any(
                "logos_node_name" in i for i in indexes
            ), "Node name index missing"
            assert any(
                "logos_node_relation" in i for i in indexes
            ), "Node relation index missing"


class TestEntityCreation:
    """Test Entity node creation with UUID constraints (flexible ontology)."""

    def test_create_entity_with_valid_uuid(self, neo4j_driver, loaded_ontology):
        """Test creating entity using :Node with type='entity' and ancestors."""
        test_uuid = f"entity-test-{uuid4()}"

        with neo4j_driver.session() as session:
            result = session.run(
                """
                CREATE (e:Node {
                    uuid: $uuid,
                    name: $name,
                    is_type_definition: false,
                    type: 'entity',
                    ancestors: ['entity', 'thing'],
                    created_at: datetime()
                }) RETURN e
                """,
                uuid=test_uuid,
                name="TestEntity01",
            )
            entity = result.single()
            assert entity is not None
            assert entity["e"]["uuid"] == test_uuid
            assert entity["e"]["type"] == "entity"
            assert "thing" in entity["e"]["ancestors"]

            # Cleanup
            session.run("MATCH (e:Node {uuid: $uuid}) DELETE e", uuid=test_uuid)

    def test_create_entity_duplicate_uuid_fails(self, neo4j_driver, loaded_ontology):
        """Test that duplicate UUID fails with constraint violation."""
        test_uuid = f"entity-test-duplicate-{uuid4()}"

        with neo4j_driver.session() as session:
            # Create first entity
            session.run(
                """
                CREATE (e:Node {
                    uuid: $uuid,
                    name: $name,
                    is_type_definition: false,
                    type: 'entity',
                    ancestors: ['entity', 'thing']
                })
                """,
                uuid=test_uuid,
                name="TestEntity01",
            )

            # Try to create duplicate - should fail
            with pytest.raises(ClientError) as exc_info:
                session.run(
                    """
                    CREATE (e:Node {
                        uuid: $uuid,
                        name: $name,
                        is_type_definition: false,
                        type: 'entity',
                        ancestors: ['entity', 'thing']
                    })
                    """,
                    uuid=test_uuid,
                    name="TestEntity02",
                )

            assert (
                "ConstraintValidationFailed" in str(exc_info.value)
                or "already exists" in str(exc_info.value).lower()
            )

            # Cleanup
            session.run("MATCH (e:Node {uuid: $uuid}) DELETE e", uuid=test_uuid)


class TestConceptCreation:
    """Test Concept node creation with UUID constraints (flexible ontology)."""

    def test_create_concept_with_valid_uuid(self, neo4j_driver, loaded_ontology):
        """Test creating concept using :Node with type='concept'."""
        test_uuid = f"concept-test-{uuid4()}"
        test_name = f"TestConcept{uuid4().hex[:8]}"

        with neo4j_driver.session() as session:
            result = session.run(
                """
                CREATE (c:Node {
                    uuid: $uuid,
                    name: $name,
                    is_type_definition: false,
                    type: 'concept',
                    ancestors: ['concept']
                }) RETURN c
                """,
                uuid=test_uuid,
                name=test_name,
            )
            concept = result.single()
            assert concept is not None
            assert concept["c"]["uuid"] == test_uuid
            assert concept["c"]["name"] == test_name
            assert concept["c"]["type"] == "concept"

            # Cleanup
            session.run("MATCH (c:Node {uuid: $uuid}) DELETE c", uuid=test_uuid)

    def test_create_concept_type_definition(self, neo4j_driver, loaded_ontology):
        """Test creating a type definition node."""
        test_uuid = f"type-test-{uuid4()}"
        test_name = f"TestType{uuid4().hex[:8]}"

        with neo4j_driver.session() as session:
            result = session.run(
                """
                CREATE (t:Node {
                    uuid: $uuid,
                    name: $name,
                    is_type_definition: true,
                    type: $name,
                    ancestors: ['concept']
                }) RETURN t
                """,
                uuid=test_uuid,
                name=test_name,
            )
            type_def = result.single()
            assert type_def is not None
            assert type_def["t"]["is_type_definition"] is True
            assert type_def["t"]["type"] == test_name

            # Cleanup
            session.run("MATCH (t:Node {uuid: $uuid}) DELETE t", uuid=test_uuid)


class TestStateCreation:
    """Test State node creation with UUID constraints (flexible ontology)."""

    def test_create_state_with_valid_uuid(self, neo4j_driver, loaded_ontology):
        """Test creating state using :Node with type='state'."""
        test_uuid = f"state-test-{uuid4()}"

        with neo4j_driver.session() as session:
            result = session.run(
                """
                CREATE (s:Node {
                    uuid: $uuid,
                    name: 'TestState',
                    is_type_definition: false,
                    type: 'state',
                    ancestors: ['state', 'concept'],
                    timestamp: datetime()
                }) RETURN s
                """,
                uuid=test_uuid,
            )
            state = result.single()
            assert state is not None
            assert state["s"]["uuid"] == test_uuid
            assert state["s"]["type"] == "state"
            assert state["s"]["timestamp"] is not None

            # Cleanup
            session.run("MATCH (s:Node {uuid: $uuid}) DELETE s", uuid=test_uuid)

    def test_create_state_duplicate_uuid_fails(self, neo4j_driver, loaded_ontology):
        """Test that duplicate state UUID fails."""
        test_uuid = f"state-test-duplicate-{uuid4()}"

        with neo4j_driver.session() as session:
            # Create first state
            session.run(
                """
                CREATE (s:Node {
                    uuid: $uuid,
                    name: 'TestState1',
                    is_type_definition: false,
                    type: 'state',
                    ancestors: ['state', 'concept'],
                    timestamp: datetime()
                })
                """,
                uuid=test_uuid,
            )

            # Try to create duplicate
            with pytest.raises(ClientError) as exc_info:
                session.run(
                    """
                    CREATE (s:Node {
                        uuid: $uuid,
                        name: 'TestState2',
                        is_type_definition: false,
                        type: 'state',
                        ancestors: ['state', 'concept'],
                        timestamp: datetime()
                    })
                    """,
                    uuid=test_uuid,
                )

            assert (
                "ConstraintValidationFailed" in str(exc_info.value)
                or "already exists" in str(exc_info.value).lower()
            )

            # Cleanup
            session.run("MATCH (s:Node {uuid: $uuid}) DELETE s", uuid=test_uuid)


class TestProcessCreation:
    """Test Process node creation with UUID constraints (flexible ontology)."""

    def test_create_process_with_valid_uuid(self, neo4j_driver, loaded_ontology):
        """Test creating process using :Node with type='process'."""
        test_uuid = f"process-test-{uuid4()}"

        with neo4j_driver.session() as session:
            result = session.run(
                """
                CREATE (p:Node {
                    uuid: $uuid,
                    name: 'TestProcess',
                    is_type_definition: false,
                    type: 'process',
                    ancestors: ['process', 'concept'],
                    start_time: datetime()
                }) RETURN p
                """,
                uuid=test_uuid,
            )
            process = result.single()
            assert process is not None
            assert process["p"]["uuid"] == test_uuid
            assert process["p"]["type"] == "process"
            assert process["p"]["start_time"] is not None

            # Cleanup
            session.run("MATCH (p:Node {uuid: $uuid}) DELETE p", uuid=test_uuid)

    def test_create_process_duplicate_uuid_fails(self, neo4j_driver, loaded_ontology):
        """Test that duplicate process UUID fails."""
        test_uuid = f"process-test-duplicate-{uuid4()}"

        with neo4j_driver.session() as session:
            # Create first process
            session.run(
                """
                CREATE (p:Node {
                    uuid: $uuid,
                    name: 'TestProcess1',
                    is_type_definition: false,
                    type: 'process',
                    ancestors: ['process', 'concept'],
                    start_time: datetime()
                })
                """,
                uuid=test_uuid,
            )

            # Try to create duplicate
            with pytest.raises(ClientError) as exc_info:
                session.run(
                    """
                    CREATE (p:Node {
                        uuid: $uuid,
                        name: 'TestProcess2',
                        is_type_definition: false,
                        type: 'process',
                        ancestors: ['process', 'concept'],
                        start_time: datetime()
                    })
                    """,
                    uuid=test_uuid,
                )

            assert (
                "ConstraintValidationFailed" in str(exc_info.value)
                or "already exists" in str(exc_info.value).lower()
            )

            # Cleanup
            session.run("MATCH (p:Node {uuid: $uuid}) DELETE p", uuid=test_uuid)


class TestRelationshipCreation:
    """Test relationship creation between nodes (flexible ontology)."""

    def test_create_is_a_relationship(self, neo4j_driver, loaded_ontology):
        """Test creating IS_A relationship between Entity and type definition."""
        entity_uuid = f"entity-test-{uuid4()}"
        type_uuid = f"type-test-{uuid4()}"
        type_name = f"TestType{uuid4().hex[:8]}"

        with neo4j_driver.session() as session:
            # Create entity node
            session.run(
                """
                CREATE (e:Node {
                    uuid: $e_uuid,
                    name: $e_name,
                    is_type_definition: false,
                    type: $type_name,
                    ancestors: [$type_name, 'thing']
                })
                """,
                e_uuid=entity_uuid,
                e_name="TestEntity",
                type_name=type_name,
            )
            # Create type definition node
            session.run(
                """
                CREATE (t:Node {
                    uuid: $t_uuid,
                    name: $t_name,
                    is_type_definition: true,
                    type: $t_name,
                    ancestors: ['thing']
                })
                """,
                t_uuid=type_uuid,
                t_name=type_name,
            )

            # Create relationship
            result = session.run(
                """
                MATCH (e:Node {uuid: $e_uuid})
                MATCH (t:Node {uuid: $t_uuid})
                CREATE (e)-[r:IS_A]->(t)
                RETURN r
                """,
                e_uuid=entity_uuid,
                t_uuid=type_uuid,
            )
            rel = result.single()
            assert rel is not None

            # Cleanup
            session.run(
                "MATCH (e:Node {uuid: $e_uuid})-[r:IS_A]->(t:Node {uuid: $t_uuid}) "
                "DELETE r, e, t",
                e_uuid=entity_uuid,
                t_uuid=type_uuid,
            )

    def test_create_has_state_relationship(self, neo4j_driver, loaded_ontology):
        """Test creating HAS_STATE relationship between Entity and State."""
        entity_uuid = f"entity-test-{uuid4()}"
        state_uuid = f"state-test-{uuid4()}"

        with neo4j_driver.session() as session:
            # Create entity node
            session.run(
                """
                CREATE (e:Node {
                    uuid: $e_uuid,
                    name: $e_name,
                    is_type_definition: false,
                    type: 'entity',
                    ancestors: ['entity', 'thing']
                })
                """,
                e_uuid=entity_uuid,
                e_name="TestEntity",
            )
            # Create state node
            session.run(
                """
                CREATE (s:Node {
                    uuid: $s_uuid,
                    name: 'TestState',
                    is_type_definition: false,
                    type: 'state',
                    ancestors: ['state', 'concept'],
                    timestamp: datetime()
                })
                """,
                s_uuid=state_uuid,
            )

            # Create relationship
            result = session.run(
                """
                MATCH (e:Node {uuid: $e_uuid})
                MATCH (s:Node {uuid: $s_uuid})
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
                "MATCH (e:Node {uuid: $e_uuid})-[r:HAS_STATE]->(s:Node {uuid: $s_uuid}) "
                "DELETE r, e, s",
                e_uuid=entity_uuid,
                s_uuid=state_uuid,
            )

    def test_create_causes_relationship(self, neo4j_driver, loaded_ontology):
        """Test creating CAUSES relationship between Process and State."""
        process_uuid = f"process-test-{uuid4()}"
        state_uuid = f"state-test-{uuid4()}"

        with neo4j_driver.session() as session:
            # Create process node
            session.run(
                """
                CREATE (p:Node {
                    uuid: $p_uuid,
                    name: 'TestProcess',
                    is_type_definition: false,
                    type: 'process',
                    ancestors: ['process', 'concept'],
                    start_time: datetime()
                })
                """,
                p_uuid=process_uuid,
            )
            # Create state node
            session.run(
                """
                CREATE (s:Node {
                    uuid: $s_uuid,
                    name: 'TestState',
                    is_type_definition: false,
                    type: 'state',
                    ancestors: ['state', 'concept'],
                    timestamp: datetime()
                })
                """,
                s_uuid=state_uuid,
            )

            # Create relationship
            result = session.run(
                """
                MATCH (p:Node {uuid: $p_uuid})
                MATCH (s:Node {uuid: $s_uuid})
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
                "MATCH (p:Node {uuid: $p_uuid})-[r:CAUSES]->(s:Node {uuid: $s_uuid}) "
                "DELETE r, p, s",
                p_uuid=process_uuid,
                s_uuid=state_uuid,
            )

    def test_create_part_of_relationship(self, neo4j_driver, loaded_ontology):
        """Test creating PART_OF relationship between entities."""
        part_uuid = f"entity-test-part-{uuid4()}"
        whole_uuid = f"entity-test-whole-{uuid4()}"

        with neo4j_driver.session() as session:
            # Create part entity node
            session.run(
                """
                CREATE (e:Node {
                    uuid: $e_uuid,
                    name: $e_name,
                    is_type_definition: false,
                    type: 'entity',
                    ancestors: ['entity', 'thing']
                })
                """,
                e_uuid=part_uuid,
                e_name="TestPart",
            )
            # Create whole entity node
            session.run(
                """
                CREATE (e:Node {
                    uuid: $e_uuid,
                    name: $e_name,
                    is_type_definition: false,
                    type: 'entity',
                    ancestors: ['entity', 'thing']
                })
                """,
                e_uuid=whole_uuid,
                e_name="TestWhole",
            )

            # Create relationship
            result = session.run(
                """
                MATCH (part:Node {uuid: $part_uuid})
                MATCH (whole:Node {uuid: $whole_uuid})
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
                "MATCH (part:Node {uuid: $part_uuid})-[r:PART_OF]->"
                "(whole:Node {uuid: $whole_uuid}) DELETE r, part, whole",
                part_uuid=part_uuid,
                whole_uuid=whole_uuid,
            )


class TestRelationshipTraversal:
    """Test traversing relationships in the graph (flexible ontology)."""

    def test_traverse_is_a_for_type_lookup(self, neo4j_driver, loaded_test_data):
        """Test traversing IS_A relationship to find entity type."""
        with neo4j_driver.session() as session:
            # Find robot arm and its type
            # UUID from test_data_pick_and_place.cypher: RobotArm01
            result = session.run("""
                MATCH (e:Node {uuid: 'c551e7ad-c12a-40bc-8c29-3a721fa311cb'})-[:IS_A]->(t:Node)
                WHERE t.is_type_definition = true
                RETURN e.name AS entity_name, t.name AS type_name
                """)
            record = result.single()
            assert record is not None
            assert record["entity_name"] == "RobotArm01"
            assert record["type_name"] == "Manipulator"

    def test_traverse_has_state_for_current_state(self, neo4j_driver, loaded_test_data):
        """Test traversing HAS_STATE relationship to find current state."""
        with neo4j_driver.session() as session:
            # Find robot arm's current state
            # UUID from test_data_pick_and_place.cypher: RobotArm01
            result = session.run("""
                MATCH (e:Node {uuid: 'c551e7ad-c12a-40bc-8c29-3a721fa311cb'})
                      -[:HAS_STATE]->(s:Node)
                WHERE s.type = 'state' OR 'state' IN s.ancestors
                RETURN s.name AS state_name, s.timestamp AS timestamp
                ORDER BY s.timestamp DESC
                LIMIT 1
                """)
            record = result.single()
            assert record is not None
            assert record["state_name"] == "ArmHomeState"

    def test_traverse_causes_for_causal_chain(self, neo4j_driver, loaded_test_data):
        """Test traversing CAUSES relationships to trace causal chain."""
        with neo4j_driver.session() as session:
            # Find what process causes the block to be grasped
            # UUID from test_data_pick_and_place.cypher: RedBlockGraspedState
            result = session.run("""
                MATCH (p:Node)-[:CAUSES]->(s:Node {uuid: 'f25e11ff-f33f-43a7-a4d8-a2839ec39976'})
                WHERE p.type = 'process' OR 'process' IN p.ancestors
                RETURN p.name AS process_name, s.name AS state_name
                """)
            record = result.single()
            assert record is not None
            assert record["process_name"] == "GraspRedBlock"
            assert record["state_name"] == "RedBlockGraspedState"

    def test_traverse_multi_hop_causal_chain(self, neo4j_driver, loaded_test_data):
        """Test traversing multi-hop causal chains."""
        with neo4j_driver.session() as session:
            # Find the causal chain from initial home state to final states
            # UUID from test_data_pick_and_place.cypher: ArmHomeState (start of PRECEDES chain)
            result = session.run("""
                MATCH path = (s1:Node {uuid: '1957c02d-a22a-483c-8ccb-cd04e7f03817'})
                             -[:PRECEDES*1..5]->(s2:Node)
                RETURN s2.name AS final_state, length(path) AS chain_length
                ORDER BY chain_length DESC
                LIMIT 1
                """)
            record = result.single()
            assert record is not None
            # Should find a state in the causal chain
            assert record["chain_length"] > 0

    def test_traverse_part_of_for_composition(self, neo4j_driver, loaded_test_data):
        """Test traversing PART_OF relationships for composition hierarchy."""
        with neo4j_driver.session() as session:
            # Find parts of robot arm
            # UUID from test_data_pick_and_place.cypher: RobotArm01
            result = session.run("""
                MATCH (part:Node)-[:PART_OF]->(whole:Node {uuid: 'c551e7ad-c12a-40bc-8c29-3a721fa311cb'})
                WHERE 'thing' IN part.ancestors
                RETURN part.name AS part_name
                ORDER BY part.name
                """)
            parts = [record["part_name"] for record in result]

            # Should include gripper and joints
            assert "Gripper01" in parts
            assert any("Joint" in p for p in parts)
            assert len(parts) >= 4  # Gripper + at least 3 joints


class TestQueryOperations:
    """Test various query operations on the graph (flexible ontology)."""

    def test_query_entity_by_uuid(self, neo4j_driver, loaded_test_data):
        """Test querying entity by UUID."""
        with neo4j_driver.session() as session:
            # UUID from test_data_pick_and_place.cypher: RobotArm01
            result = session.run(
                "MATCH (e:Node {uuid: $uuid}) RETURN e.name AS name",
                uuid="c551e7ad-c12a-40bc-8c29-3a721fa311cb",
            )
            record = result.single()
            assert record is not None
            assert record["name"] == "RobotArm01"

    def test_query_entity_by_name(self, neo4j_driver, loaded_test_data):
        """Test querying entity by name."""
        with neo4j_driver.session() as session:
            result = session.run(
                """
                MATCH (e:Node {name: $name})
                WHERE 'thing' IN e.ancestors
                RETURN e.uuid AS uuid
                """,
                name="RobotArm01",
            )
            record = result.single()
            assert record is not None
            # UUID from test_data_pick_and_place.cypher: RobotArm01
            assert record["uuid"] == "c551e7ad-c12a-40bc-8c29-3a721fa311cb"

    def test_query_states_by_timestamp(self, neo4j_driver, loaded_test_data):
        """Test querying states by timestamp range."""
        with neo4j_driver.session() as session:
            result = session.run("""
                MATCH (s:Node)
                WHERE (s.type = 'state' OR 'state' IN s.ancestors)
                  AND s.timestamp IS NOT NULL
                RETURN count(s) AS state_count
                """)
            record = result.single()
            assert record is not None
            assert record["state_count"] > 0

    def test_query_processes_by_start_time(self, neo4j_driver, loaded_test_data):
        """Test querying processes by start time."""
        with neo4j_driver.session() as session:
            result = session.run("""
                MATCH (p:Node)
                WHERE (p.type = 'process' OR 'process' IN p.ancestors)
                  AND p.start_time IS NOT NULL
                RETURN count(p) AS process_count
                """)
            record = result.single()
            assert record is not None
            assert record["process_count"] > 0

    def test_count_nodes_by_type(self, neo4j_driver, loaded_test_data):
        """Test counting nodes by type property."""
        with neo4j_driver.session() as session:
            # Count entities (things)
            result = session.run(
                "MATCH (e:Node) WHERE 'thing' IN e.ancestors RETURN count(e) AS count"
            )
            entity_count = result.single()["count"]
            assert entity_count > 0

            # Count concepts (non-things)
            result = session.run("""
                MATCH (c:Node)
                WHERE 'concept' IN c.ancestors AND NOT 'thing' IN c.ancestors
                RETURN count(c) AS count
                """)
            concept_count = result.single()["count"]
            assert concept_count > 0

            # Count states
            result = session.run("""
                MATCH (s:Node)
                WHERE s.type = 'state' OR 'state' IN s.ancestors
                RETURN count(s) AS count
                """)
            state_count = result.single()["count"]
            assert state_count > 0

            # Count processes
            result = session.run("""
                MATCH (p:Node)
                WHERE p.type = 'process' OR 'process' IN p.ancestors
                RETURN count(p) AS count
                """)
            process_count = result.single()["count"]
            assert process_count > 0

    def test_query_by_type_property(self, neo4j_driver, loaded_test_data):
        """Test querying nodes by their type property."""
        with neo4j_driver.session() as session:
            # Query by exact type
            result = session.run("""
                MATCH (n:Node {type: 'Manipulator'})
                WHERE n.is_type_definition = false
                RETURN n.name AS name
                """)
            records = list(result)
            assert len(records) > 0
            assert any(r["name"] == "RobotArm01" for r in records)

    def test_query_type_definitions(self, neo4j_driver, loaded_test_data):
        """Test querying type definitions vs instances."""
        with neo4j_driver.session() as session:
            # Count type definitions
            result = session.run("""
                MATCH (t:Node {is_type_definition: true})
                RETURN count(t) AS type_count
                """)
            type_count = result.single()["type_count"]
            assert type_count > 0

            # Count instances
            result = session.run("""
                MATCH (i:Node {is_type_definition: false})
                RETURN count(i) AS instance_count
                """)
            instance_count = result.single()["instance_count"]
            assert instance_count > 0

            # Both type definitions and instances should exist
            # (no ordering assumption - type count depends on ontology complexity)
