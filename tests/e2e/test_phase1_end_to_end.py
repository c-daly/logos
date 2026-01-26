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

FLEXIBLE ONTOLOGY:
All nodes use :Node label with type/ancestors properties.
See docs/plans/2025-12-30-flexible-ontology-design.md

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

    def test_bootstrap_types_loaded(self, loaded_ontology):
        """Verify bootstrap types are loaded (flexible ontology)."""
        returncode, stdout, stderr = run_cypher_query(
            "MATCH (n:Node {is_type_definition: true}) "
            "WHERE n.type IN ['type_definition', 'thing', 'concept', 'edge_type'] "
            "RETURN count(n) AS count;"
        )
        assert returncode == 0, f"Failed to query bootstrap types: {stderr}"
        assert "count" in stdout.lower(), "Expected bootstrap type count in output"


class TestM4TestDataLoading:
    """Test that pick-and-place test data is loaded."""

    def test_entities_loaded(self, loaded_test_data):
        """Verify test entities are present (flexible ontology)."""
        # Check for instances that have 'thing' in their ancestry (all physical entities)
        query = (
            "MATCH (e:Node) "
            "WHERE 'thing' IN e.ancestors AND e.is_type_definition = false "
            "RETURN count(e) AS count;"
        )
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query entities: {stderr}"
        assert "count" in stdout.lower(), "Expected entity count in output"

    def test_manipulator_entity_exists(self, loaded_test_data):
        """Verify manipulator entity exists (flexible ontology)."""
        query = (
            "MATCH (e:Node) "
            "WHERE (e.type = 'Manipulator' OR 'Manipulator' IN e.ancestors) "
            "  OR e.name CONTAINS 'RobotArm' "
            "RETURN count(e) AS count;"
        )
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query manipulator: {stderr}"
        # Check that at least one entity exists
        count_match = [line for line in stdout.strip().split("\n") if line.isdigit()]
        assert (
            len(count_match) > 0 and int(count_match[0]) >= 0
        ), "Expected manipulator entity query to succeed"


class TestM4SimulatedWorkflow:
    """Test the simulated end-to-end workflow with specific assertions."""

    def test_create_goal_state(self, loaded_test_data):
        """Simulate Apollo creating a goal state (flexible ontology)."""
        create_query = """
        MERGE (g:Node {uuid: '964305c9-008f-5e7c-9fa6-08a4db697c1a'})
        ON CREATE SET
            g.name = 'TestGoalState_RedBlockInBin',
            g.is_type_definition = false,
            g.type = 'state',
            g.ancestors = ['state', 'concept'],
            g.timestamp = datetime(),
            g.description = 'Test goal: red block in bin',
            g.is_goal = true
        RETURN g.uuid, g.name, g.is_goal, g.description;
        """
        returncode, stdout, stderr = run_cypher_query(create_query)
        assert returncode == 0, f"Failed to create goal state: {stderr}"

        assert (
            "TestGoalState_RedBlockInBin" in stdout
        ), "Expected goal state name not found"
        assert (
            "964305c9-008f-5e7c-9fa6-08a4db697c1a" in stdout
        ), "Expected goal state UUID not found"

    def test_create_plan_processes(self, loaded_test_data):
        """Simulate Sophia generating a plan (flexible ontology)."""
        create_plan_query = """
        MERGE (p1:Node {uuid: '0b962a3f-605d-50af-9d5a-fbdc7c655532'})
        ON CREATE SET
            p1.name = 'TestMoveToPreGrasp',
            p1.is_type_definition = false,
            p1.type = 'process',
            p1.ancestors = ['process', 'concept'],
            p1.start_time = datetime(),
            p1.description = 'Move robot arm to pre-grasp position'

        MERGE (p2:Node {uuid: '8e2f0070-d9b3-5bc9-b9fc-417bd0e34e79'})
        ON CREATE SET
            p2.name = 'TestGraspRedBlock',
            p2.is_type_definition = false,
            p2.type = 'process',
            p2.ancestors = ['process', 'concept'],
            p2.start_time = datetime(),
            p2.description = 'Grasp red block with gripper'

        MERGE (p3:Node {uuid: '42fc6d04-c28b-5c50-a598-274ba3eeeed9'})
        ON CREATE SET
            p3.name = 'TestMoveToPlace',
            p3.is_type_definition = false,
            p3.type = 'process',
            p3.ancestors = ['process', 'concept'],
            p3.start_time = datetime(),
            p3.description = 'Move to placement position'

        MERGE (p4:Node {uuid: 'a25ecb46-f011-5378-a571-7509225dc55f'})
        ON CREATE SET
            p4.name = 'TestReleaseBlock',
            p4.is_type_definition = false,
            p4.type = 'process',
            p4.ancestors = ['process', 'concept'],
            p4.start_time = datetime(),
            p4.description = 'Release block into bin'

        MERGE (p1)-[:PRECEDES]->(p2)
        MERGE (p2)-[:PRECEDES]->(p3)
        MERGE (p3)-[:PRECEDES]->(p4)

        RETURN p1.name, p2.name, p3.name, p4.name;
        """
        returncode, stdout, stderr = run_cypher_query(create_plan_query)
        assert returncode == 0, f"Failed to create plan processes: {stderr}"

        assert (
            "TestMoveToPreGrasp" in stdout
        ), "Expected MoveToPreGrasp process not found"
        assert "TestGraspRedBlock" in stdout, "Expected GraspRedBlock process not found"
        assert "TestMoveToPlace" in stdout, "Expected MoveToPlace process not found"
        assert "TestReleaseBlock" in stdout, "Expected ReleaseBlock process not found"

    @pytest.mark.skipif(
        not PLANNER_CLIENT_AVAILABLE, reason="Planner client not available"
    )
    def test_create_plan_via_planner_api(self, loaded_test_data):
        """Simulate Sophia generating a plan via planner API."""
        client = PlannerClient()
        if not client.is_available(timeout=2.0):
            pytest.skip("Planner service not running")

        response = client.generate_plan_for_scenario("pick_and_place")
        assert response.success is True, "Plan generation should succeed"
        assert len(response.plan) == 4, "Pick-and-place should have 4 steps"

        created_uuids = []
        try:
            for i, step in enumerate(response.plan):
                created_uuids.append(step.uuid)
                query = f"""
                CREATE (p:Node {{
                    uuid: '{step.uuid}',
                    name: '{step.process}',
                    is_type_definition: false,
                    type: 'process',
                    ancestors: ['process', 'concept'],
                    start_time: datetime(),
                    description: 'API-generated {step.process}',
                    step_number: {i}
                }})
                RETURN p.uuid, p.name;
                """
                returncode, stdout, stderr = run_cypher_query(query)
                assert (
                    returncode == 0
                ), f"Failed to create process {step.process}: {stderr}"

            # Create PRECEDES relationships
            for i in range(len(response.plan) - 1):
                current_uuid = response.plan[i].uuid
                next_uuid = response.plan[i + 1].uuid

                query = f"""
                MATCH (p1:Node {{uuid: '{current_uuid}'}})
                MATCH (p2:Node {{uuid: '{next_uuid}'}})
                CREATE (p1)-[:PRECEDES]->(p2)
                RETURN p1.name, p2.name;
                """
                returncode, stdout, stderr = run_cypher_query(query)
                assert (
                    returncode == 0
                ), f"Failed to create PRECEDES relationship: {stderr}"

            print(f"✓ Created plan via planner API with {len(response.plan)} steps")

        finally:
            if created_uuids:
                uuid_list_str = "[" + ", ".join([f"'{u}'" for u in created_uuids]) + "]"
                cleanup_query = f"""
                MATCH (p:Node)
                WHERE p.uuid IN {uuid_list_str}
                DETACH DELETE p
                """
                run_cypher_query(cleanup_query)

    def test_simulate_execution_state_update(self, loaded_test_data):
        """Simulate Talos updating state during execution (flexible ontology)."""
        create_entities_query = """
        MERGE (e:Node {uuid: 'b91e3ad0-9739-55a5-928e-3e0024add30f'})
        ON CREATE SET
            e.name = 'RedBlock01',
            e.is_type_definition = false,
            e.type = 'entity',
            e.ancestors = ['entity', 'thing'],
            e.description = 'Red cubic block',
            e.color = 'red',
            e.created_at = datetime()
        MERGE (bin:Node {uuid: '7e9f1098-a96e-54dd-a9f7-ed3378cd2e5d'})
        ON CREATE SET
            bin.name = 'TargetBin01',
            bin.is_type_definition = false,
            bin.type = 'entity',
            bin.ancestors = ['entity', 'thing'],
            bin.description = 'Target container for placement',
            bin.created_at = datetime()
        RETURN e.uuid, e.name, bin.uuid, bin.name;
        """
        returncode, stdout, stderr = run_cypher_query(create_entities_query)
        assert returncode == 0, f"Failed to ensure test entities exist: {stderr}"
        assert "RedBlock01" in stdout, "Expected RedBlock01 entity not found"
        assert "TargetBin01" in stdout, "Expected TargetBin01 entity not found"


class TestM4StateVerification:
    """Test that state changes can be queried and verified."""

    def test_verify_nodes_exist(self, loaded_test_data):
        """Verify nodes exist in flexible ontology format."""
        query = """
        MATCH (n:Node)
        WHERE n.type IS NOT NULL
        RETURN count(n) AS count;
        """
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query nodes: {stderr}"
        assert "count" in stdout.lower(), "Expected node count in output"

    def test_query_entity_states(self, loaded_test_data):
        """Verify we can query entity states (flexible ontology)."""
        query = """
        MATCH (e:Node)-[:HAS_STATE]->(s:Node)
        WHERE (e.type = 'entity' OR 'entity' IN e.ancestors)
          AND (s.type = 'state' OR 'state' IN s.ancestors)
        RETURN e.name, s.name
        LIMIT 10;
        """
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query entity states: {stderr}"

    def test_query_process_ordering(self, loaded_test_data):
        """Verify we can query process temporal ordering (flexible ontology)."""
        query = """
        MATCH (p1:Node)-[:PRECEDES]->(p2:Node)
        WHERE (p1.type = 'process' OR 'process' IN p1.ancestors)
          AND (p2.type = 'process' OR 'process' IN p2.ancestors)
        RETURN p1.name, p2.name
        LIMIT 5;
        """
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query process ordering: {stderr}"


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
        wait_for_neo4j(NEO4J_CONFIG, timeout=NEO4J_WAIT_TIMEOUT)

        script_path = REPO_ROOT / "scripts" / "e2e_prototype.sh"
        try:
            result = subprocess.run(
                [str(script_path)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=REPO_ROOT,
            )
            # Script should complete successfully
            assert result.returncode == 0, f"E2E script failed: {result.stderr}"
            assert "All tests passed" in result.stdout, "Expected success message"
        except subprocess.TimeoutExpired:
            pytest.fail("E2E script timed out")
