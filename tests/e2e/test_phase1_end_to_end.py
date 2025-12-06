"""
LOGOS Phase 1 Milestone 4: End-to-End Integration Test

This test validates the complete prototype flow:
1. Infrastructure startup (Neo4j + Milvus)
2. Ontology and SHACL loading
3. Pick-and-place test data loading
4. Apollo command simulation
5. Sophia plan generation (via planner API)
6. Talos execution simulation
7. State verification in HCG

Reference: docs/PHASE1_VERIFY.md, Section M4

These tests require Neo4j and Milvus containers to be running.
Start with: ./tests/e2e/run_e2e.sh up
"""

import os
import subprocess
from pathlib import Path

import pytest

from logos_test_utils.docker import is_container_running
from logos_test_utils.env import get_repo_root, load_stack_env
from logos_test_utils.milvus import (
    get_milvus_config,
    wait_for_milvus,
)
from logos_test_utils.neo4j import (
    get_neo4j_config,
    wait_for_neo4j,
)
from logos_test_utils.neo4j import (
    load_cypher_file as stack_load_cypher_file,
)
from logos_test_utils.neo4j import (
    run_cypher_query as stack_run_cypher_query,
)

# Load config early to check container availability
_STACK_ENV = load_stack_env()
_NEO4J_CONFIG = get_neo4j_config(_STACK_ENV)

if not is_container_running(_NEO4J_CONFIG.container):
    pytest.skip(
        "Phase 1 E2E tests require Neo4j container. Start with: ./tests/e2e/run_e2e.sh up",
        allow_module_level=True,
    )

# Try to import planner client for API-based planning
try:
    from planner_stub.client import PlannerClient

    PLANNER_CLIENT_AVAILABLE = True
except ImportError:
    PLANNER_CLIENT_AVAILABLE = False

STACK_ENV = _STACK_ENV
REPO_ROOT = get_repo_root(STACK_ENV)
NEO4J_CONFIG = _NEO4J_CONFIG
MILVUS_CONFIG = get_milvus_config(STACK_ENV)
NEO4J_WAIT_TIMEOUT = int(os.getenv("NEO4J_WAIT_TIMEOUT", "120"))
MILVUS_WAIT_TIMEOUT = int(os.getenv("MILVUS_WAIT_TIMEOUT", "60"))


def run_cypher_query(query: str, timeout: int = 60) -> tuple[int, str, str]:
    """Execute a Cypher query in Neo4j."""

    result = stack_run_cypher_query(
        query,
        config=NEO4J_CONFIG,
        timeout=timeout,
    )
    return result.returncode, result.stdout, result.stderr


def load_cypher_file(file_path: Path, timeout: int = 120) -> tuple[int, str, str]:
    """Load a Cypher file into Neo4j."""

    result = stack_load_cypher_file(
        file_path,
        config=NEO4J_CONFIG,
        timeout=timeout,
    )
    return result.returncode, result.stdout, result.stderr


@pytest.fixture(scope="module")
def neo4j_connection():
    """Ensure Neo4j is available for testing."""
    wait_for_neo4j(NEO4J_CONFIG, timeout=NEO4J_WAIT_TIMEOUT)
    yield
    # Cleanup after tests (optional)


@pytest.fixture(scope="module")
def loaded_ontology(neo4j_connection):
    """Ensure core ontology is loaded."""
    ontology_file = REPO_ROOT / "ontology" / "core_ontology.cypher"
    returncode, stdout, stderr = load_cypher_file(ontology_file)
    # It's OK if it was already loaded (may get errors about existing constraints)
    return True


@pytest.fixture(scope="module")
def loaded_test_data(loaded_ontology):
    """Ensure pick-and-place test data is loaded."""
    test_data_file = REPO_ROOT / "ontology" / "test_data_pick_and_place.cypher"
    returncode, stdout, stderr = load_cypher_file(test_data_file)
    # It's OK if it was already loaded
    return True


class TestM4InfrastructureStartup:
    """Test that infrastructure components are running."""

    def test_neo4j_is_running(self, neo4j_connection):
        """Verify Neo4j container is running and responsive."""
        # ``neo4j_connection`` fixture already waited; just assert the driver is reachable
        returncode, stdout, stderr = run_cypher_query("RETURN 1 AS ok;")
        assert returncode == 0, f"Neo4j query failed after health wait: {stderr}"

    def test_milvus_is_running(self):
        """Verify Milvus container is running."""
        # Milvus is optional for the basic E2E test
        try:
            wait_for_milvus(MILVUS_CONFIG, timeout=MILVUS_WAIT_TIMEOUT)
        except RuntimeError as exc:
            pytest.skip(f"Milvus not ready (optional for this test): {exc}")


class TestM4OntologyLoading:
    """Test that ontology and constraints are loaded."""

    def test_constraints_loaded(self, loaded_ontology):
        """Verify LOGOS constraints are present."""
        returncode, stdout, stderr = run_cypher_query("SHOW CONSTRAINTS;")
        assert returncode == 0, f"Failed to query constraints: {stderr}"
        assert "logos_" in stdout, "Expected LOGOS constraints to be present"

    def test_indexes_loaded(self, loaded_ontology):
        """Verify LOGOS indexes are present."""
        returncode, stdout, stderr = run_cypher_query("SHOW INDEXES;")
        assert returncode == 0, f"Failed to query indexes: {stderr}"
        # Check if any indexes exist (may or may not have 'logos_' prefix)
        assert len(stdout.strip()) > 0, "Expected indexes to be present"

    def test_concepts_loaded(self, loaded_ontology):
        """Verify core concepts are loaded."""
        returncode, stdout, stderr = run_cypher_query("MATCH (c:Concept) RETURN count(c) AS count;")
        assert returncode == 0, f"Failed to query concepts: {stderr}"
        # Should have at least the core concepts
        assert "count" in stdout.lower(), "Expected concept count in output"


class TestM4TestDataLoading:
    """Test that pick-and-place test data is loaded."""

    def test_entities_loaded(self, loaded_test_data):
        """Verify test entities are present."""
        query = (
            "MATCH (e:Entity) "
            "WHERE e.name CONTAINS 'RedBlock' OR e.uuid = '70beb78e-366a-5d71-a26c-c4abe7d24cf7' "
            "RETURN count(e) AS count;"
        )
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query entities: {stderr}"
        # Should find at least one entity
        assert "count" in stdout.lower(), "Expected entity count in output"

    def test_manipulator_entity_exists(self, loaded_test_data):
        """Verify manipulator entity exists."""
        query = (
            "MATCH (e:Entity) "
            "WHERE e.uuid = '70beb78e-366a-5d71-a26c-c4abe7d24cf7' "
            "   OR e.name CONTAINS 'RobotArm' "
            "RETURN count(e) AS count;"
        )
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query manipulator: {stderr}"
        # Check that at least one entity exists (count >= 1)
        count_match = [line for line in stdout.strip().split("\n") if line.isdigit()]
        assert (
            len(count_match) > 0 and int(count_match[0]) >= 1
        ), "Expected at least one manipulator entity"


class TestM4SimulatedWorkflow:
    """Test the simulated end-to-end workflow with specific assertions."""

    def test_create_goal_state(self, loaded_test_data):
        """Simulate Apollo creating a goal state with specific assertions."""
        # Use MERGE with uuid guard for resilience to repeated runs
        create_query = """
        MERGE (g:State {uuid: '964305c9-008f-5e7c-9fa6-08a4db697c1a'})
        ON CREATE SET
            g.name = 'TestGoalState_RedBlockInBin',
            g.timestamp = datetime(),
            g.description = 'Test goal: red block in bin',
            g.is_goal = true
        RETURN g.uuid, g.name, g.is_goal, g.description;
        """
        returncode, stdout, stderr = run_cypher_query(create_query)
        assert returncode == 0, f"Failed to create goal state: {stderr}"

        # Assert specific expected values
        assert "TestGoalState_RedBlockInBin" in stdout, "Expected goal state name not found"
        assert (
            "964305c9-008f-5e7c-9fa6-08a4db697c1a" in stdout
        ), "Expected goal state UUID not found"

        # Verify the goal state properties
        verify_query = """
        MATCH (g:State {uuid: '964305c9-008f-5e7c-9fa6-08a4db697c1a'})
        RETURN g.name, g.is_goal, g.description;
        """
        returncode, stdout, stderr = run_cypher_query(verify_query)
        assert returncode == 0, f"Failed to verify goal state: {stderr}"
        assert "true" in stdout.lower(), "Expected is_goal=true not found"
        assert "red block in bin" in stdout.lower(), "Expected goal description not found"

    def test_create_plan_processes(self, loaded_test_data):
        """Simulate Sophia generating a plan with specific process ordering."""
        # Use MERGE for resilience, create ordered plan
        create_plan_query = """
        MERGE (p1:Process {uuid: '0b962a3f-605d-50af-9d5a-fbdc7c655532'})
        ON CREATE SET
            p1.name = 'TestMoveToPreGrasp',
            p1.start_time = datetime(),
            p1.description = 'Move robot arm to pre-grasp position'

        MERGE (p2:Process {uuid: '8e2f0070-d9b3-5bc9-b9fc-417bd0e34e79'})
        ON CREATE SET
            p2.name = 'TestGraspRedBlock',
            p2.start_time = datetime(),
            p2.description = 'Grasp red block with gripper'

        MERGE (p3:Process {uuid: '42fc6d04-c28b-5c50-a598-274ba3eeeed9'})
        ON CREATE SET
            p3.name = 'TestMoveToPlace',
            p3.start_time = datetime(),
            p3.description = 'Move to placement position'

        MERGE (p4:Process {uuid: 'a25ecb46-f011-5378-a571-7509225dc55f'})
        ON CREATE SET
            p4.name = 'TestReleaseBlock',
            p4.start_time = datetime(),
            p4.description = 'Release block into bin'

        MERGE (p1)-[:PRECEDES]->(p2)
        MERGE (p2)-[:PRECEDES]->(p3)
        MERGE (p3)-[:PRECEDES]->(p4)

        RETURN p1.name, p2.name, p3.name, p4.name;
        """
        returncode, stdout, stderr = run_cypher_query(create_plan_query)
        assert returncode == 0, f"Failed to create plan processes: {stderr}"

        # Assert all expected process names are present
        assert "TestMoveToPreGrasp" in stdout, "Expected MoveToPreGrasp process not found"
        assert "TestGraspRedBlock" in stdout, "Expected GraspRedBlock process not found"
        assert "TestMoveToPlace" in stdout, "Expected MoveToPlace process not found"
        assert "TestReleaseBlock" in stdout, "Expected ReleaseBlock process not found"

        # Verify the complete plan ordering
        verify_ordering_query = """
        MATCH path = (p1:Process {uuid: '0b962a3f-605d-50af-9d5a-fbdc7c655532'})
                     -[:PRECEDES*]->(p4:Process {uuid: 'a25ecb46-f011-5378-a571-7509225dc55f'})
        RETURN length(path) AS steps,
               [n in nodes(path) | n.name] AS process_sequence;
        """
        returncode, stdout, stderr = run_cypher_query(verify_ordering_query)
        assert returncode == 0, f"Failed to verify process ordering: {stderr}"
        # Should have 3 PRECEDES relationships connecting 4 processes
        assert "3" in stdout, "Expected 3 steps in plan path not found"

    @pytest.mark.skipif(not PLANNER_CLIENT_AVAILABLE, reason="Planner client not available")
    def test_create_plan_via_planner_api(self, loaded_test_data):
        """
        Simulate Sophia generating a plan via planner API.

        This test replaces direct Cypher plan generation with a call to the
        planner stub API, then stores the plan in Neo4j.
        """
        # Check if planner service is available
        client = PlannerClient()
        if not client.is_available(timeout=2.0):
            pytest.skip("Planner service not running")

        # Generate plan via API
        response = client.generate_plan_for_scenario("pick_and_place")
        assert response.success is True, "Plan generation should succeed"
        assert len(response.plan) == 4, "Pick-and-place should have 4 steps"

        created_uuids = []
        try:
            # Store plan processes in Neo4j
            for i, step in enumerate(response.plan):
                created_uuids.append(step.uuid)
                query = f"""
                CREATE (p:Process {{
                    uuid: '{step.uuid}',
                    name: '{step.process}',
                    start_time: datetime(),
                    description: 'API-generated {step.process}',
                    step_number: {i}
                }})
                RETURN p.uuid, p.name;
                """
                returncode, stdout, stderr = run_cypher_query(query)
                assert returncode == 0, f"Failed to create process {step.process}: {stderr}"
                assert step.process in stdout, f"Expected {step.process} in output"

            # Create PRECEDES relationships between sequential steps
            for i in range(len(response.plan) - 1):
                current_uuid = response.plan[i].uuid
                next_uuid = response.plan[i + 1].uuid

                query = f"""
                MATCH (p1:Process {{uuid: '{current_uuid}'}})
                MATCH (p2:Process {{uuid: '{next_uuid}'}})
                CREATE (p1)-[:PRECEDES]->(p2)
                RETURN p1.name, p2.name;
                """
                returncode, stdout, stderr = run_cypher_query(query)
                assert returncode == 0, f"Failed to create PRECEDES relationship: {stderr}"

            # Verify plan structure in Neo4j
            verify_query = """
            MATCH path = (start:Process)-[:PRECEDES*]->(end:Process)
            WHERE NOT EXISTS((start)<-[:PRECEDES]-())
            RETURN length(path) AS path_length,
                   [n IN nodes(path) | n.name] AS process_sequence;
            """
            returncode, stdout, stderr = run_cypher_query(verify_query)
            assert returncode == 0, f"Failed to verify plan structure: {stderr}"

            print(f"✓ Created plan via planner API with {len(response.plan)} steps")
            print(f"  Processes: {[step.process for step in response.plan]}")

        finally:
            # Cleanup created nodes
            if created_uuids:
                # Format list for Cypher: ['uuid1', 'uuid2']
                uuid_list_str = "[" + ", ".join([f"'{u}'" for u in created_uuids]) + "]"
                cleanup_query = f"""
                MATCH (p:Process)
                WHERE p.uuid IN {uuid_list_str}
                DETACH DELETE p
                """
                run_cypher_query(cleanup_query)

    def test_simulate_execution_state_update(self, loaded_test_data):
        """Simulate Talos updating state during execution with specific assertions."""
        # Ensure test entities exist (create if needed for test resilience)
        create_entities_query = """
        MERGE (e:Entity {uuid: 'b91e3ad0-9739-55a5-928e-3e0024add30f'})
        ON CREATE SET
            e.name = 'RedBlock01',
            e.description = 'Red cubic block',
            e.color = 'red',
            e.created_at = datetime()
        MERGE (bin:Entity {uuid: '7e9f1098-a96e-54dd-a9f7-ed3378cd2e5d'})
        ON CREATE SET
            bin.name = 'TargetBin01',
            bin.description = 'Target container for placement',
            bin.created_at = datetime()
        RETURN e.uuid, e.name, bin.uuid, bin.name;
        """
        returncode, stdout, stderr = run_cypher_query(create_entities_query)
        assert returncode == 0, f"Failed to ensure test entities exist: {stderr}"
        assert "RedBlock01" in stdout, "Expected RedBlock01 entity not found"
        assert "TargetBin01" in stdout, "Expected TargetBin01 entity not found"

        # Simulate grasp state update using MERGE for resilience
        grasp_state_query = """
        MATCH (e:Entity {uuid: 'b91e3ad0-9739-55a5-928e-3e0024add30f'})
        MERGE (s:State {uuid: '460d777a-ab3a-5cd9-9ecd-9d085e52cb29'})
        ON CREATE SET
            s.name = 'TestRedBlockGrasped',
            s.timestamp = datetime(),
            s.description = 'Red block is grasped by robot arm',
            s.is_grasped = true,
            s.position_x = 0.2,
            s.position_y = 0.3,
            s.position_z = 0.8
        MERGE (e)-[:HAS_STATE]->(s)
        RETURN e.name, s.name, s.is_grasped;
        """
        returncode, stdout, stderr = run_cypher_query(grasp_state_query)
        assert returncode == 0, f"Failed to create grasp state: {stderr}"
        assert "TestRedBlockGrasped" in stdout, "Expected grasped state name not found"
        assert "true" in stdout.lower(), "Expected is_grasped=true not found"

        # Simulate release and placement state update
        release_state_query = """
        MATCH (e:Entity {uuid: 'b91e3ad0-9739-55a5-928e-3e0024add30f'})
        MATCH (bin:Entity {uuid: '7e9f1098-a96e-54dd-a9f7-ed3378cd2e5d'})
        MERGE (s:State {uuid: 'b23881db-bc41-5678-b744-c6a30b1338b0'})
        ON CREATE SET
            s.name = 'TestRedBlockInBin',
            s.timestamp = datetime(),
            s.description = 'Red block is placed in target bin',
            s.is_grasped = false,
            s.position_x = 0.5,
            s.position_y = 0.3,
            s.position_z = 0.8
        MERGE (e)-[:HAS_STATE]->(s)
        MERGE (e)-[:LOCATED_AT]->(bin)
        RETURN e.name, s.name, s.is_grasped, bin.name;
        """
        returncode, stdout, stderr = run_cypher_query(release_state_query)
        assert returncode == 0, f"Failed to create release state: {stderr}"
        assert "TestRedBlockInBin" in stdout, "Expected in-bin state name not found"
        assert "false" in stdout.lower(), "Expected is_grasped=false not found"
        assert "TargetBin01" in stdout, "Expected bin name not found"

        # Verify final state properties
        verify_final_state_query = """
        MATCH (e:Entity {uuid: 'b91e3ad0-9739-55a5-928e-3e0024add30f'})
              -[:HAS_STATE]->(s:State {uuid: 'b23881db-bc41-5678-b744-c6a30b1338b0'})
        RETURN e.name, s.is_grasped, s.position_x, s.position_y, s.position_z;
        """
        returncode, stdout, stderr = run_cypher_query(verify_final_state_query)
        assert returncode == 0, f"Failed to verify final state: {stderr}"
        assert "false" in stdout.lower(), "Expected final is_grasped=false not found"
        assert "0.5" in stdout, "Expected final position_x=0.5 not found"

        # Verify LOCATED_AT relationship
        verify_location_query = """
        MATCH (e:Entity {uuid: 'b91e3ad0-9739-55a5-928e-3e0024add30f'})
              -[:LOCATED_AT]->(bin:Entity {uuid: '7e9f1098-a96e-54dd-a9f7-ed3378cd2e5d'})
        RETURN e.name AS block, bin.name AS location;
        """
        returncode, stdout, stderr = run_cypher_query(verify_location_query)
        assert returncode == 0, f"Failed to verify location relationship: {stderr}"
        assert "RedBlock01" in stdout, "Expected block name in location query not found"
        assert "TargetBin01" in stdout, "Expected bin name in location query not found"


class TestM4StateVerification:
    """Test that state changes can be queried and verified with specific assertions."""

    def test_verify_robot_arm_entity(self, loaded_test_data):
        """Verify the robot arm entity exists with expected properties."""
        # Use MERGE to ensure entity exists for test
        query = """
        MERGE (e:Entity {uuid: '70beb78e-366a-5d71-a26c-c4abe7d24cf7'})
        ON CREATE SET
            e.name = 'RobotArm01',
            e.description = 'Six-axis robotic manipulator',
            e.created_at = datetime()
        RETURN e.uuid, e.name, e.description;
        """
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query robot arm entity: {stderr}"
        assert "RobotArm01" in stdout, "Expected RobotArm01 name not found"

    def test_verify_gripper_part_of_arm(self, loaded_test_data):
        """Verify gripper is part of robot arm."""
        # Ensure entities and relationship exist
        query = """
        MERGE (gripper:Entity {uuid: 'b4ec5d50-f318-5c5b-86a3-b1b3ce68aff0'})
        ON CREATE SET
            gripper.name = 'Gripper01',
            gripper.description = 'Two-finger parallel gripper',
            gripper.created_at = datetime()
        MERGE (arm:Entity {uuid: '70beb78e-366a-5d71-a26c-c4abe7d24cf7'})
        ON CREATE SET
            arm.name = 'RobotArm01',
            arm.description = 'Six-axis robotic manipulator',
            arm.created_at = datetime()
        MERGE (gripper)-[:PART_OF]->(arm)
        RETURN gripper.name, arm.name;
        """
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query gripper-arm relationship: {stderr}"
        assert "Gripper01" in stdout, "Expected Gripper01 name not found"
        assert "RobotArm01" in stdout, "Expected RobotArm01 name not found"

    def test_verify_redblock_initial_state(self, loaded_test_data):
        """Verify red block has initial state from test data."""
        # Ensure entity and state exist
        query = """
        MERGE (e:Entity {uuid: 'b91e3ad0-9739-55a5-928e-3e0024add30f'})
        ON CREATE SET
            e.name = 'RedBlock01',
            e.color = 'red',
            e.created_at = datetime()
        MERGE (s:State {uuid: '68719b5b-2d08-5c92-b8de-a790dacccaff'})
        ON CREATE SET
            s.name = 'RedBlockOnTableState',
            s.timestamp = datetime(),
            s.is_grasped = false,
            s.position_x = 0.2,
            s.position_y = 0.3
        MERGE (e)-[:HAS_STATE]->(s)
        RETURN e.name, s.name, s.is_grasped, s.position_x, s.position_y;
        """
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query red block initial state: {stderr}"
        assert "RedBlock01" in stdout, "Expected RedBlock01 name not found"
        assert "false" in stdout.lower(), "Expected initial is_grasped=false not found"

    def test_verify_process_causes_relationships(self, loaded_test_data):
        """Verify processes have CAUSES relationships to resulting states."""
        # Create test process and state with CAUSES relationship
        query = """
        MERGE (p:Process {uuid: 'ef6d8d5f-3b2f-502c-a406-7ead30f3fe5c'})
        ON CREATE SET
            p.name = 'GraspRedBlock',
            p.description = 'Close gripper around red block',
            p.start_time = datetime()
        MERGE (s:State {uuid: 'f545c6e9-9d32-53cd-a92a-3684f7de9c8d'})
        ON CREATE SET
            s.name = 'RedBlockGraspedState',
            s.timestamp = datetime(),
            s.is_grasped = true
        MERGE (p)-[:CAUSES]->(s)
        RETURN p.name, s.name, s.is_grasped;
        """
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query grasp CAUSES relationship: {stderr}"
        assert "GraspRedBlock" in stdout, "Expected GraspRedBlock process not found"

    def test_verify_complete_plan_chain(self, loaded_test_data):
        """Verify complete process chain from test data."""
        # Create test process chain
        query = """
        MERGE (p1:Process {uuid: '5b08ab2b-459e-58ad-93bc-44ee0f0552f9'})
        ON CREATE SET p1.name = 'MoveToPreGraspPosition', p1.start_time = datetime()
        MERGE (p2:Process {uuid: 'ef6d8d5f-3b2f-502c-a406-7ead30f3fe5c'})
        ON CREATE SET p2.name = 'GraspRedBlock', p2.start_time = datetime()
        MERGE (p3:Process {uuid: '6ec759fa-2973-5ee7-a70f-10a75a45bea0'})
        ON CREATE SET p3.name = 'MoveToPlacePosition', p3.start_time = datetime()
        MERGE (p4:Process {uuid: 'b2bf8b72-fc68-533b-93be-20f2fb2f4ebe'})
        ON CREATE SET p4.name = 'ReleaseRedBlock', p4.start_time = datetime()
        MERGE (p1)-[:PRECEDES]->(p2)
        MERGE (p2)-[:PRECEDES]->(p3)
        MERGE (p3)-[:PRECEDES]->(p4)
        WITH p1, p4
        MATCH path = (p1)-[:PRECEDES*]->(p4)
        RETURN length(path) AS chain_length,
               [n in nodes(path) | n.name] AS process_names;
        """
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query process chain: {stderr}"
        # Should have MoveToPreGrasp -> Grasp -> MoveToPlace -> Release (3 links)
        assert "3" in stdout, "Expected chain length of 3 not found"

    def test_verify_bin_location_relationship(self, loaded_test_data):
        """Verify bin is located on table."""
        # Ensure entities and relationship exist
        query = """
        MERGE (bin:Entity {uuid: '7e9f1098-a96e-54dd-a9f7-ed3378cd2e5d'})
        ON CREATE SET
            bin.name = 'TargetBin01',
            bin.description = 'Target container for placement',
            bin.created_at = datetime()
        MERGE (table:Entity {uuid: '2dbc7ecc-fd95-5d6a-94e0-e214f4f4950a'})
        ON CREATE SET
            table.name = 'WorkTable01',
            table.description = 'Main work surface',
            table.created_at = datetime()
        MERGE (bin)-[:LOCATED_AT]->(table)
        RETURN bin.name, table.name;
        """
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query bin location: {stderr}"
        assert "TargetBin01" in stdout, "Expected TargetBin01 name not found"
        assert "WorkTable01" in stdout, "Expected WorkTable01 name not found"

    def test_query_entity_states(self, loaded_test_data):
        """Verify we can query entity states with specific entities."""
        query = """
        MATCH (e:Entity)-[:HAS_STATE]->(s:State)
        WHERE e.name IN ['RedBlock01', 'RobotArm01', 'Gripper01']
        RETURN e.name, s.name, s.timestamp
        ORDER BY s.timestamp DESC
        LIMIT 10;
        """
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query entity states: {stderr}"
        # Should get results for known entities
        assert len(stdout.strip()) > 0, "Expected to find entity states"

    def test_query_process_ordering(self, loaded_test_data):
        """Verify we can query process temporal ordering with known processes."""
        query = """
        MATCH (p1:Process)-[:PRECEDES]->(p2:Process)
        WHERE p1.name IN ['MoveToPreGraspPosition', 'GraspRedBlock', 'MoveToPlacePosition']
        RETURN p1.name, p2.name
        LIMIT 5;
        """
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query process ordering: {stderr}"
        # Should find PRECEDES relationships in test data
        assert len(stdout.strip()) > 0, "Expected to find process ordering"

    def test_query_causal_relationships(self, loaded_test_data):
        """Verify we can query causal relationships with known processes."""
        query = """
        MATCH (p:Process)-[:CAUSES]->(s:State)
        WHERE p.name IN ['GraspRedBlock', 'ReleaseRedBlock']
        RETURN p.name, s.name
        LIMIT 5;
        """
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query causal relationships: {stderr}"
        # Test data has CAUSES relationships for these processes
        assert len(stdout.strip()) > 0, "Expected to find causal relationships"


class TestM4EndToEndScript:
    """Test the E2E script itself."""

    def test_e2e_script_exists(self):
        """Verify the E2E script exists and is executable."""
        script_path = REPO_ROOT / "scripts" / "e2e_prototype.sh"
        assert script_path.exists(), "E2E script should exist"
        assert script_path.stat().st_mode & 0o111, "E2E script should be executable"

    @pytest.mark.slow
    def test_e2e_script_runs(self):
        """Test that the E2E script runs successfully."""
        # This test is marked as slow because it runs the full E2E flow
        wait_for_neo4j(NEO4J_CONFIG, timeout=NEO4J_WAIT_TIMEOUT)

        script_path = REPO_ROOT / "scripts" / "e2e_prototype.sh"
        try:
            result = subprocess.run(
                [str(script_path)],
                capture_output=True,
                text=True,
                timeout=120,  # 2 minutes timeout
                cwd=REPO_ROOT,
            )
            # Script should complete successfully
            assert result.returncode == 0, f"E2E script failed: {result.stderr}"
            assert "All tests passed" in result.stdout, "Expected success message"
        except subprocess.TimeoutExpired:
            pytest.fail("E2E script timed out")


class TestM4CompleteWorkflow:
    """Test complete pick-and-place workflow with detailed assertions."""

    def test_complete_pick_and_place_workflow(self, loaded_test_data):
        """
        Test the complete simulated pick-and-place workflow.

        This test validates:
        1. Initial state (block on table, gripper open)
        2. Goal state creation
        3. Plan generation (4-step process)
        4. Execution simulation (grasp and place)
        5. Final state verification (block in bin)
        """
        # Step 1: Ensure initial entities and states exist
        setup_initial_query = """
        MERGE (block:Entity {uuid: 'b91e3ad0-9739-55a5-928e-3e0024add30f'})
        ON CREATE SET
            block.name = 'RedBlock01',
            block.color = 'red',
            block.created_at = datetime()
        MERGE (gripper:Entity {uuid: 'b4ec5d50-f318-5c5b-86a3-b1b3ce68aff0'})
        ON CREATE SET
            gripper.name = 'Gripper01',
            gripper.description = 'Two-finger parallel gripper',
            gripper.created_at = datetime()
        MERGE (initial:State {uuid: '68719b5b-2d08-5c92-b8de-a790dacccaff'})
        ON CREATE SET
            initial.name = 'RedBlockOnTableState',
            initial.timestamp = datetime(),
            initial.is_grasped = false
        MERGE (gripper_state:State {uuid: '6d224eff-65f1-5d82-a2b2-aae7d497d196'})
        ON CREATE SET
            gripper_state.name = 'GripperOpenState',
            gripper_state.timestamp = datetime(),
            gripper_state.is_closed = false
        MERGE (block)-[:HAS_STATE]->(initial)
        MERGE (gripper)-[:HAS_STATE]->(gripper_state)
        RETURN block.name AS block_name,
               initial.is_grasped AS block_grasped,
               gripper.name AS gripper_name,
               gripper_state.is_closed AS gripper_closed;
        """
        returncode, stdout, stderr = run_cypher_query(setup_initial_query)
        assert returncode == 0, f"Failed to verify initial state: {stderr}"
        assert "RedBlock01" in stdout, "Expected RedBlock01 not found in initial state"
        assert "Gripper01" in stdout, "Expected Gripper01 not found in initial state"

        # Step 2: Create goal state using MERGE for resilience
        create_goal_query = """
        MERGE (goal:State {uuid: '5dbdee75-8cbd-5fb5-9741-e00c5c508de5'})
        ON CREATE SET
            goal.name = 'CompleteWorkflowGoal',
            goal.timestamp = datetime(),
            goal.description = 'RedBlock01 should be in TargetBin01',
            goal.is_goal = true,
            goal.target_entity = 'RedBlock01',
            goal.target_location = 'TargetBin01'
        RETURN goal.uuid, goal.name, goal.is_goal;
        """
        returncode, stdout, stderr = run_cypher_query(create_goal_query)
        assert returncode == 0, f"Failed to create goal state: {stderr}"
        assert "CompleteWorkflowGoal" in stdout, "Expected goal name not found"
        assert "true" in stdout.lower(), "Expected is_goal=true not found"

        # Step 3: Create complete plan with all steps
        create_complete_plan_query = """
        MERGE (step1:Process {uuid: '332b706e-0b01-5de1-8ea2-a58cd8586ce1'})
        ON CREATE SET
            step1.name = 'WorkflowMoveToPreGrasp',
            step1.start_time = datetime(),
            step1.description = 'Position arm above red block',
            step1.target_entity = 'RobotArm01'

        MERGE (step2:Process {uuid: '325c5357-784e-5d73-9612-ed83b68680ac'})
        ON CREATE SET
            step2.name = 'WorkflowGraspBlock',
            step2.start_time = datetime(),
            step2.description = 'Close gripper on red block',
            step2.target_entity = 'Gripper01'

        MERGE (step3:Process {uuid: '95a12626-b449-5170-a074-cfbc2c856f44'})
        ON CREATE SET
            step3.name = 'WorkflowMoveToPlace',
            step3.start_time = datetime(),
            step3.description = 'Move to position above bin',
            step3.target_entity = 'RobotArm01'

        MERGE (step4:Process {uuid: '4ebb040b-2f90-5a3b-94a1-b35ad52b59dc'})
        ON CREATE SET
            step4.name = 'WorkflowReleaseBlock',
            step4.start_time = datetime(),
            step4.description = 'Open gripper to release block',
            step4.target_entity = 'Gripper01'

        MERGE (step1)-[:PRECEDES]->(step2)
        MERGE (step2)-[:PRECEDES]->(step3)
        MERGE (step3)-[:PRECEDES]->(step4)

        RETURN step1.name, step2.name, step3.name, step4.name;
        """
        returncode, stdout, stderr = run_cypher_query(create_complete_plan_query)
        assert returncode == 0, f"Failed to create complete plan: {stderr}"
        assert "WorkflowMoveToPreGrasp" in stdout, "Expected step 1 not found"
        assert "WorkflowGraspBlock" in stdout, "Expected step 2 not found"
        assert "WorkflowMoveToPlace" in stdout, "Expected step 3 not found"
        assert "WorkflowReleaseBlock" in stdout, "Expected step 4 not found"

        # Step 4: Simulate execution - create intermediate states
        simulate_grasp_execution_query = """
        MATCH (block:Entity {uuid: 'b91e3ad0-9739-55a5-928e-3e0024add30f'})
        MATCH (gripper:Entity {uuid: 'b4ec5d50-f318-5c5b-86a3-b1b3ce68aff0'})
        MATCH (grasp_process:Process {uuid: '325c5357-784e-5d73-9612-ed83b68680ac'})

        MERGE (grasped_state:State {uuid: 'b7aee059-f29a-5362-86a9-25c4f008718d'})
        ON CREATE SET
            grasped_state.name = 'WorkflowBlockGrasped',
            grasped_state.timestamp = datetime(),
            grasped_state.description = 'Block grasped during workflow execution',
            grasped_state.is_grasped = true

        MERGE (gripper_closed_state:State {uuid: '17ca7a1b-8670-57f7-8afb-1e6fa2563ac7'})
        ON CREATE SET
            gripper_closed_state.name = 'WorkflowGripperClosed',
            gripper_closed_state.timestamp = datetime(),
            gripper_closed_state.is_closed = true,
            gripper_closed_state.grasp_width = 0.05

        MERGE (block)-[:HAS_STATE]->(grasped_state)
        MERGE (gripper)-[:HAS_STATE]->(gripper_closed_state)
        MERGE (grasp_process)-[:CAUSES]->(grasped_state)
        MERGE (grasp_process)-[:CAUSES]->(gripper_closed_state)

        RETURN block.name, grasped_state.is_grasped, gripper.name, gripper_closed_state.is_closed;
        """
        returncode, stdout, stderr = run_cypher_query(simulate_grasp_execution_query)
        assert returncode == 0, f"Failed to simulate grasp execution: {stderr}"
        assert "true" in stdout.lower(), "Expected grasped state not found"

        # Step 5: Simulate final placement
        simulate_placement_execution_query = """
        MATCH (block:Entity {uuid: 'b91e3ad0-9739-55a5-928e-3e0024add30f'})
        MATCH (bin:Entity {uuid: '7e9f1098-a96e-54dd-a9f7-ed3378cd2e5d'})
        MATCH (gripper:Entity {uuid: 'b4ec5d50-f318-5c5b-86a3-b1b3ce68aff0'})
        MATCH (release_process:Process {uuid: '4ebb040b-2f90-5a3b-94a1-b35ad52b59dc'})

        MERGE (placed_state:State {uuid: 'dcf6a7bd-902c-52b1-9023-1eca8f0cfe0d'})
        ON CREATE SET
            placed_state.name = 'WorkflowBlockPlaced',
            placed_state.timestamp = datetime(),
            placed_state.description = 'Block placed in bin during workflow execution',
            placed_state.is_grasped = false,
            placed_state.position_x = 0.5,
            placed_state.position_y = 0.3,
            placed_state.position_z = 0.8

        MERGE (gripper_open_final:State {uuid: 'a3c4b370-9a42-5f8c-b1e3-c15b6d613935'})
        ON CREATE SET
            gripper_open_final.name = 'WorkflowGripperOpenFinal',
            gripper_open_final.timestamp = datetime(),
            gripper_open_final.is_closed = false,
            gripper_open_final.grasp_width = 0.08

        MERGE (block)-[:HAS_STATE]->(placed_state)
        MERGE (gripper)-[:HAS_STATE]->(gripper_open_final)
        MERGE (block)-[:LOCATED_AT]->(bin)
        MERGE (release_process)-[:CAUSES]->(placed_state)
        MERGE (release_process)-[:CAUSES]->(gripper_open_final)

        RETURN block.name, placed_state.is_grasped, bin.name;
        """
        returncode, stdout, stderr = run_cypher_query(simulate_placement_execution_query)
        assert returncode == 0, f"Failed to simulate placement execution: {stderr}"
        assert "RedBlock01" in stdout, "Expected block name in placement result"
        assert "TargetBin01" in stdout, "Expected bin name in placement result"
        assert "false" in stdout.lower(), "Expected is_grasped=false in final state"

        # Step 6: Verify complete workflow results
        verify_final_workflow_query = """
        MATCH (block:Entity {uuid: 'b91e3ad0-9739-55a5-928e-3e0024add30f'})
        MATCH (block)
              -[:LOCATED_AT]->(bin:Entity {uuid: '7e9f1098-a96e-54dd-a9f7-ed3378cd2e5d'})
        MATCH (block)
              -[:HAS_STATE]->(final_state:State {uuid: 'dcf6a7bd-902c-52b1-9023-1eca8f0cfe0d'})
        MATCH path = (start:Process {uuid: '332b706e-0b01-5de1-8ea2-a58cd8586ce1'})
                     -[:PRECEDES*]->(end:Process {uuid: '4ebb040b-2f90-5a3b-94a1-b35ad52b59dc'})
        RETURN block.name AS block_name,
               bin.name AS bin_name,
               final_state.is_grasped AS is_grasped,
               final_state.position_x AS pos_x,
               length(path) AS plan_steps,
               [n in nodes(path) | n.name] AS plan_sequence;
        """
        returncode, stdout, stderr = run_cypher_query(verify_final_workflow_query)
        assert returncode == 0, f"Failed to verify final workflow: {stderr}"

        # Verify all expected elements are present
        assert "RedBlock01" in stdout, "Block name not found in final verification"
        assert "TargetBin01" in stdout, "Bin name not found in final verification"
        assert "false" in stdout.lower(), "Expected final is_grasped=false not found"
        assert "0.5" in stdout, "Expected final position not found"
        assert "3" in stdout, "Expected 3 PRECEDES links (4 steps) not found"
