"""
Integration tests for HCG query utilities.

Tests the HCG client library, connection pooling, and query operations
against a Neo4j instance with the core ontology loaded.

Note: These tests require a running Neo4j instance with the core ontology loaded.
They can be skipped if Neo4j is not available.
"""

import os
from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from logos_hcg import HCGClient
from logos_hcg.client import HCGConnectionError, HCGQueryError
from logos_test_utils.docker import is_container_running
from logos_test_utils.neo4j import get_neo4j_config, wait_for_neo4j

# Test configuration - defaults pulled from shared stack env
RUN_HCG_TESTS = os.getenv("RUN_HCG_TESTS") not in {None, "", "0", "false", "False"}
pytestmark = pytest.mark.skipif(
    not RUN_HCG_TESTS,
    reason="Set RUN_HCG_TESTS=1 and start the shared stack to exercise HCG integration tests.",
)

NEO4J_CONFIG = get_neo4j_config()
NEO4J_URI = os.getenv("NEO4J_URI", NEO4J_CONFIG.uri)
NEO4J_USER = os.getenv("NEO4J_USER", NEO4J_CONFIG.user)
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", NEO4J_CONFIG.password)
NEO4J_WAIT_TIMEOUT = int(os.getenv("NEO4J_WAIT_TIMEOUT", "120"))
_ONTOLOGY_PRESENT: bool | None = None


@pytest.fixture(scope="session", autouse=True)
def ensure_neo4j_ready():
    """Fail fast with diagnostics if Neo4j never becomes available."""

    if not is_container_running(NEO4J_CONFIG.container):
        pytest.skip(
            "Neo4j not available. Start with: "
            "docker compose -f infra/docker-compose.hcg.dev.yml up -d"
        )

    try:
        wait_for_neo4j(NEO4J_CONFIG, timeout=NEO4J_WAIT_TIMEOUT)
    except (RuntimeError, FileNotFoundError) as exc:
        pytest.skip(
            "Neo4j not available. Start with: "
            "docker compose -f infra/docker-compose.hcg.dev.yml up -d\n"
            f"Details: {exc}"
        )


@pytest.fixture(scope="module")
def hcg_client():
    """Create an HCG client for testing."""
    client = HCGClient(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)
    yield client
    client.close()


@pytest.fixture(scope="module")
def client_with_context():
    """Test context manager usage."""
    with HCGClient(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD) as client:
        yield client


class TestConnection:
    """Test connection management and pooling."""

    def test_connection_success(self):
        """Test successful connection to Neo4j."""
        client = HCGClient(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)
        assert client.verify_connection()
        client.close()

    def test_connection_failure(self):
        """Test connection failure with invalid credentials."""
        with pytest.raises(HCGConnectionError):
            HCGClient(uri=NEO4J_URI, user="invalid", password="invalid")

    def test_connection_invalid_uri(self):
        """Test connection failure with invalid URI."""
        with pytest.raises(HCGConnectionError):
            HCGClient(uri="bolt://invalid:7687", user=NEO4J_USER, password=NEO4J_PASSWORD)

    def test_context_manager(self, client_with_context):
        """Test client usage as context manager."""
        assert client_with_context.verify_connection()

    def test_connection_pooling_config(self):
        """Test connection pooling configuration."""
        client = HCGClient(
            uri=NEO4J_URI,
            user=NEO4J_USER,
            password=NEO4J_PASSWORD,
            max_connection_pool_size=10,
            max_connection_lifetime=1800,
            connection_acquisition_timeout=30,
        )
        assert client.verify_connection()
        client.close()


class TestConceptQueries:
    """Test concept query operations."""

    def test_find_all_concepts(self, hcg_client):
        """Test finding all concepts."""
        require_ontology_loaded(hcg_client)
        concepts = hcg_client.find_all_concepts()
        assert len(concepts) > 0

        # Verify we have expected concept types
        concept_names = [c.name for c in concepts]
        assert "Manipulator" in concept_names or "GraspableObject" in concept_names

    def test_find_concept_by_name(self, hcg_client):
        """Test finding concept by exact name."""
        # Try to find a known concept from core_ontology.cypher
        concept = hcg_client.find_concept_by_name("Manipulator")

        if concept:
            assert concept.name == "Manipulator"
            assert concept.uuid is not None

    def test_find_concept_by_uuid(self, hcg_client):
        """Test finding concept by UUID."""
        # First get a concept
        concepts = hcg_client.find_all_concepts()
        if len(concepts) > 0:
            first_concept = concepts[0]

            # Find by UUID
            found = hcg_client.find_concept_by_uuid(first_concept.uuid)
            assert found is not None
            assert found.uuid == first_concept.uuid
            assert found.name == first_concept.name

    def test_find_nonexistent_concept(self, hcg_client):
        """Test finding nonexistent concept returns None."""
        concept = hcg_client.find_concept_by_uuid(uuid4())
        assert concept is None


class TestEntityQueries:
    """Test entity query operations."""

    def test_find_all_entities(self, hcg_client):
        """Test finding all entities with pagination."""
        entities = hcg_client.find_all_entities(skip=0, limit=10)
        assert isinstance(entities, list)
        # May be empty if no test data loaded

    def test_find_entities_by_name(self, hcg_client):
        """Test finding entities by name pattern."""
        # Search for any entity (may return empty list if no test data)
        entities = hcg_client.find_entities_by_name("test")
        assert isinstance(entities, list)

    def test_find_entity_by_uuid(self, hcg_client):
        """Test finding entity by UUID."""
        # Get an entity first
        entities = hcg_client.find_all_entities(limit=1)

        if len(entities) > 0:
            first_entity = entities[0]

            # Find by UUID
            found = hcg_client.find_entity_by_uuid(first_entity.uuid)
            assert found is not None
            assert found.uuid == first_entity.uuid

    def test_find_nonexistent_entity(self, hcg_client):
        """Test finding nonexistent entity returns None."""
        entity = hcg_client.find_entity_by_uuid(uuid4())
        assert entity is None


class TestRelationshipQueries:
    """Test relationship query operations."""

    def test_get_entity_type(self, hcg_client):
        """Test getting entity type via IS_A relationship."""
        # Get an entity that has a type
        entities = hcg_client.find_all_entities(limit=10)

        for entity in entities:
            concept = hcg_client.get_entity_type(entity.uuid)
            # Entity may or may not have a type depending on test data
            if concept:
                assert concept.uuid is not None
                assert concept.name is not None

    def test_get_entity_states(self, hcg_client):
        """Test getting entity states via HAS_STATE relationship."""
        entities = hcg_client.find_all_entities(limit=10)

        for entity in entities:
            states = hcg_client.get_entity_states(entity.uuid)
            assert isinstance(states, list)
            # May be empty if no states exist

    def test_get_entity_current_state(self, hcg_client):
        """Test getting most recent entity state."""
        entities = hcg_client.find_all_entities(limit=10)

        for entity in entities:
            state = hcg_client.get_entity_current_state(entity.uuid)
            # May be None if no states exist
            if state:
                assert state.uuid is not None
                assert state.timestamp is not None

    def test_get_entity_parts(self, hcg_client):
        """Test getting entity parts via PART_OF relationship."""
        entities = hcg_client.find_all_entities(limit=10)

        for entity in entities:
            parts = hcg_client.get_entity_parts(entity.uuid)
            assert isinstance(parts, list)
            # May be empty if entity has no parts

    def test_get_entity_parent(self, hcg_client):
        """Test getting entity parent via PART_OF relationship."""
        entities = hcg_client.find_all_entities(limit=10)

        for entity in entities:
            parent = hcg_client.get_entity_parent(entity.uuid)
            # May be None if entity has no parent
            if parent:
                assert parent.uuid is not None


class TestStateQueries:
    """Test state query operations."""

    def test_find_state_by_uuid(self, hcg_client):
        """Test finding state by UUID."""
        # Try to find states in a wide time range
        now = datetime.now()
        past = now - timedelta(days=365)
        future = now + timedelta(days=1)

        states = hcg_client.find_states_by_timestamp_range(past, future)

        if len(states) > 0:
            first_state = states[0]
            found = hcg_client.find_state_by_uuid(first_state.uuid)
            assert found is not None
            assert found.uuid == first_state.uuid

    def test_find_states_by_timestamp_range(self, hcg_client):
        """Test finding states by timestamp range."""
        now = datetime.now()
        past = now - timedelta(days=365)
        future = now + timedelta(days=1)

        states = hcg_client.find_states_by_timestamp_range(past, future)
        assert isinstance(states, list)

        # Verify states are ordered by timestamp
        for i in range(len(states) - 1):
            assert states[i].timestamp <= states[i + 1].timestamp

    def test_find_nonexistent_state(self, hcg_client):
        """Test finding nonexistent state returns None."""
        state = hcg_client.find_state_by_uuid(uuid4())
        assert state is None


class TestProcessQueries:
    """Test process query operations."""

    def test_find_process_by_uuid(self, hcg_client):
        """Test finding process by UUID."""
        now = datetime.now()
        past = now - timedelta(days=365)
        future = now + timedelta(days=1)

        processes = hcg_client.find_processes_by_time_range(past, future)

        if len(processes) > 0:
            first_process = processes[0]
            found = hcg_client.find_process_by_uuid(first_process.uuid)
            assert found is not None
            assert found.uuid == first_process.uuid

    def test_find_processes_by_time_range(self, hcg_client):
        """Test finding processes by time range."""
        now = datetime.now()
        past = now - timedelta(days=365)
        future = now + timedelta(days=1)

        processes = hcg_client.find_processes_by_time_range(past, future)
        assert isinstance(processes, list)

        # Verify processes are ordered by start_time
        for i in range(len(processes) - 1):
            assert processes[i].start_time <= processes[i + 1].start_time

    def test_get_process_causes(self, hcg_client):
        """Test getting states caused by a process."""
        now = datetime.now()
        past = now - timedelta(days=365)
        future = now + timedelta(days=1)

        processes = hcg_client.find_processes_by_time_range(past, future)

        for process in processes:
            states = hcg_client.get_process_causes(process.uuid)
            assert isinstance(states, list)

    def test_get_process_requirements(self, hcg_client):
        """Test getting states required by a process."""
        now = datetime.now()
        past = now - timedelta(days=365)
        future = now + timedelta(days=1)

        processes = hcg_client.find_processes_by_time_range(past, future)

        for process in processes:
            states = hcg_client.get_process_requirements(process.uuid)
            assert isinstance(states, list)

    def test_find_nonexistent_process(self, hcg_client):
        """Test finding nonexistent process returns None."""
        process = hcg_client.find_process_by_uuid(uuid4())
        assert process is None


class TestCausalTraversal:
    """Test causal traversal operations."""

    def test_traverse_causality_forward(self, hcg_client):
        """Test forward causal traversal."""
        now = datetime.now()
        past = now - timedelta(days=365)
        future = now + timedelta(days=1)

        states = hcg_client.find_states_by_timestamp_range(past, future)

        for state in states[:5]:  # Test first 5 states
            results = hcg_client.traverse_causality_forward(state.uuid, max_depth=5)
            assert isinstance(results, list)

            # Verify structure of results
            for result in results:
                assert "process" in result
                assert "state" in result
                assert "depth" in result

    def test_traverse_causality_backward(self, hcg_client):
        """Test backward causal traversal."""
        now = datetime.now()
        past = now - timedelta(days=365)
        future = now + timedelta(days=1)

        states = hcg_client.find_states_by_timestamp_range(past, future)

        for state in states[:5]:  # Test first 5 states
            results = hcg_client.traverse_causality_backward(state.uuid, max_depth=5)
            assert isinstance(results, list)

            # Verify structure of results
            for result in results:
                assert "state" in result
                assert "process" in result
                assert "depth" in result


class TestUtilityOperations:
    """Test utility operations."""

    def test_count_nodes_by_type(self, hcg_client):
        """Test counting nodes by type."""
        require_ontology_loaded(hcg_client)
        counts = hcg_client.count_nodes_by_type()

        assert "entity_count" in counts
        assert "concept_count" in counts
        assert "state_count" in counts
        assert "process_count" in counts

        # Should have at least some concepts from core ontology
        assert counts["concept_count"] > 0

    def test_verify_connection(self, hcg_client):
        """Test connection verification."""
        assert hcg_client.verify_connection() is True


class TestErrorHandling:
    """Test error handling and retry logic."""

    def test_invalid_query_raises_error(self, hcg_client):
        """Test that invalid queries raise appropriate errors."""
        # Try to execute a malformed query
        with pytest.raises(HCGQueryError):
            hcg_client._execute_query("INVALID CYPHER QUERY")

    def test_query_with_invalid_parameters(self, hcg_client):
        """Test query with invalid parameters."""
        # This should not raise an error, just return empty results
        result = hcg_client.find_entity_by_uuid("not-a-valid-uuid-format")
        assert result is None


def require_ontology_loaded(client: HCGClient) -> None:
    """Skip tests that require ontology data when nothing has been loaded."""

    global _ONTOLOGY_PRESENT
    if _ONTOLOGY_PRESENT is None:
        _ONTOLOGY_PRESENT = bool(client.find_all_concepts())

    if not _ONTOLOGY_PRESENT:
        pytest.skip("Neo4j core ontology not loaded; skipping data-dependent HCG tests")
