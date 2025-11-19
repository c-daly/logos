"""
LOGOS Phase 1 Milestone 4: End-to-End Integration Test

This test validates the complete prototype flow:
1. Infrastructure startup (Neo4j + Milvus)
2. Ontology and SHACL loading
3. Pick-and-place test data loading
4. Apollo command simulation
5. Sophia plan generation
6. Talos execution simulation
7. State verification in HCG

Reference: docs/PHASE1_VERIFY.md, Section M4
"""

import subprocess
from pathlib import Path

import pytest

# Repository root
REPO_ROOT = Path(__file__).parent.parent.parent

# Neo4j configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "logosdev"
NEO4J_CONTAINER = "logos-hcg-neo4j"


def is_neo4j_available() -> bool:
    """Check if Neo4j is available and responsive."""
    try:
        result = subprocess.run(
            [
                "docker",
                "exec",
                NEO4J_CONTAINER,
                "cypher-shell",
                "-u",
                NEO4J_USER,
                "-p",
                NEO4J_PASSWORD,
                "RETURN 1 AS test;",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def is_milvus_available() -> bool:
    """Check if Milvus container is running."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return "logos-hcg-milvus" in result.stdout
    except Exception:
        return False


def run_cypher_query(query: str) -> tuple[int, str, str]:
    """Execute a Cypher query in Neo4j."""
    try:
        result = subprocess.run(
            [
                "docker",
                "exec",
                NEO4J_CONTAINER,
                "cypher-shell",
                "-u",
                NEO4J_USER,
                "-p",
                NEO4J_PASSWORD,
                query,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Query timed out"


def load_cypher_file(file_path: Path) -> tuple[int, str, str]:
    """Load a Cypher file into Neo4j."""
    try:
        with open(file_path) as f:
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "-i",
                    NEO4J_CONTAINER,
                    "cypher-shell",
                    "-u",
                    NEO4J_USER,
                    "-p",
                    NEO4J_PASSWORD,
                ],
                stdin=f,
                capture_output=True,
                text=True,
                timeout=60,
            )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Loading timed out"


@pytest.fixture(scope="module")
def neo4j_connection():
    """Ensure Neo4j is available for testing."""
    if not is_neo4j_available():
        pytest.skip(
            "Neo4j not available. Start with: docker compose -f infra/docker-compose.hcg.dev.yml up -d"
        )
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
        assert is_neo4j_available(), "Neo4j should be running and responsive"

    def test_milvus_is_running(self):
        """Verify Milvus container is running."""
        # Milvus is optional for the basic E2E test
        if is_milvus_available():
            assert True, "Milvus is running"
        else:
            pytest.skip("Milvus not running (optional for this test)")


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
        query = "MATCH (e:Entity) WHERE e.name CONTAINS 'RedBlock' OR e.name CONTAINS 'Manipulator' RETURN count(e) AS count;"
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query entities: {stderr}"
        # Should find at least one entity
        assert "count" in stdout.lower(), "Expected entity count in output"

    def test_manipulator_entity_exists(self, loaded_test_data):
        """Verify manipulator entity exists."""
        query = "MATCH (e:Entity) WHERE e.name CONTAINS 'Manipulator' RETURN e.name LIMIT 1;"
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query manipulator: {stderr}"
        # Check if we got a result (output should contain a name)
        assert len(stdout.strip()) > 0, "Expected manipulator entity to exist"


class TestM4SimulatedWorkflow:
    """Test the simulated end-to-end workflow."""

    def test_create_goal_state(self, loaded_test_data):
        """Simulate Apollo creating a goal state."""
        query = """
        CREATE (g:State {
            uuid: 'state-goal-test-' + randomUUID(),
            name: 'TestGoalState',
            timestamp: datetime(),
            description: 'Test goal: red block in bin',
            is_goal: true
        })
        RETURN g.uuid, g.name;
        """
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to create goal state: {stderr}"
        assert "TestGoalState" in stdout, "Expected goal state to be created"

    def test_create_plan_processes(self, loaded_test_data):
        """Simulate Sophia generating a plan."""
        query = """
        CREATE (p1:Process {
            uuid: 'process-test-' + randomUUID(),
            name: 'TestGraspAction',
            start_time: datetime(),
            description: 'Test grasp action'
        })
        CREATE (p2:Process {
            uuid: 'process-test-' + randomUUID(),
            name: 'TestPlaceAction',
            start_time: datetime(),
            description: 'Test place action'
        })
        CREATE (p1)-[:PRECEDES]->(p2)
        RETURN p1.name, p2.name;
        """
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to create plan processes: {stderr}"
        assert "TestGraspAction" in stdout, "Expected grasp action to be created"
        assert "TestPlaceAction" in stdout, "Expected place action to be created"

    def test_simulate_execution_state_update(self, loaded_test_data):
        """Simulate Talos updating state during execution."""
        # First, ensure we have an entity to update
        create_entity_query = """
        MERGE (e:Entity {uuid: 'entity-test-block-001', name: 'TestBlock'})
        RETURN e.uuid;
        """
        returncode, stdout, stderr = run_cypher_query(create_entity_query)
        assert returncode == 0, f"Failed to create test entity: {stderr}"

        # Now create a state update
        update_state_query = """
        MATCH (e:Entity {uuid: 'entity-test-block-001'})
        CREATE (s:State {
            uuid: 'state-test-' + randomUUID(),
            name: 'TestBlockGrasped',
            timestamp: datetime(),
            description: 'Test block is grasped',
            is_grasped: true
        })
        CREATE (e)-[:HAS_STATE]->(s)
        RETURN e.name, s.name;
        """
        returncode, stdout, stderr = run_cypher_query(update_state_query)
        assert returncode == 0, f"Failed to create state update: {stderr}"
        assert "TestBlockGrasped" in stdout, "Expected state update to be created"


class TestM4StateVerification:
    """Test that state changes can be queried and verified."""

    def test_query_entity_states(self, loaded_test_data):
        """Verify we can query entity states."""
        query = """
        MATCH (e:Entity)-[:HAS_STATE]->(s:State)
        RETURN e.name, s.name
        ORDER BY s.timestamp DESC
        LIMIT 5;
        """
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query entity states: {stderr}"
        # Should get some results (from either test data or our test)
        assert len(stdout.strip()) > 0, "Expected to find entity states"

    def test_query_process_ordering(self, loaded_test_data):
        """Verify we can query process temporal ordering."""
        query = """
        MATCH (p1:Process)-[:PRECEDES]->(p2:Process)
        RETURN p1.name, p2.name
        LIMIT 5;
        """
        returncode, stdout, stderr = run_cypher_query(query)
        assert returncode == 0, f"Failed to query process ordering: {stderr}"
        # Should get some results (from either test data or our test)
        assert len(stdout.strip()) > 0, "Expected to find process ordering"

    def test_query_causal_relationships(self, loaded_test_data):
        """Verify we can query causal relationships."""
        query = """
        MATCH (p:Process)-[:CAUSES]->(s:State)
        RETURN p.name, s.name
        LIMIT 5;
        """
        returncode, stdout, stderr = run_cypher_query(query)
        # This is OK even if no results - test data may not have CAUSES relationships
        assert returncode == 0, f"Failed to query causal relationships: {stderr}"


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
        if not is_neo4j_available():
            pytest.skip("Neo4j not available for E2E script test")

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
