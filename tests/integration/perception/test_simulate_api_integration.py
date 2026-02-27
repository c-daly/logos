"""
Integration tests for /simulate API endpoint.

Tests the FastAPI endpoint with real Neo4j database.
Validates that simulation results are properly stored and retrieved.

To run:
    1. Start test stack: docker compose -f docker-compose.test.yml up -d
    2. pytest tests/integration/perception/test_simulate_api_integration.py -v
"""

import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from neo4j import GraphDatabase

from logos_sophia import create_sophia_api
from logos_test_utils.docker import is_container_running
from logos_test_utils.neo4j import get_neo4j_config, wait_for_neo4j

# Test configuration
NEO4J_CONFIG = get_neo4j_config()
NEO4J_URI = os.getenv("NEO4J_URI", NEO4J_CONFIG.uri)
NEO4J_USER = os.getenv("NEO4J_USER", NEO4J_CONFIG.user)
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", NEO4J_CONFIG.password)
NEO4J_WAIT_TIMEOUT = int(os.getenv("NEO4J_WAIT_TIMEOUT", "120"))


@pytest.fixture(scope="module", autouse=True)
def ensure_neo4j_ready():
    """Fail tests if Neo4j is not available - CI should set up infrastructure."""
    if not is_container_running(NEO4J_CONFIG.container):
        pytest.fail(
            "Neo4j not available. Start with: "
            "docker compose -f docker-compose.test.yml up -d"
        )

    try:
        wait_for_neo4j(NEO4J_CONFIG, timeout=NEO4J_WAIT_TIMEOUT)
    except (RuntimeError, FileNotFoundError) as exc:
        pytest.fail(f"Neo4j not ready: {exc}")


@pytest.fixture(scope="module")
def neo4j_driver():
    """Create a real Neo4j driver."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    yield driver
    driver.close()


@pytest.fixture
def test_client(neo4j_driver):
    """Create a test client with Sophia API connected to real Neo4j."""
    app = FastAPI()
    sophia_router = create_sophia_api(neo4j_driver)
    app.include_router(sophia_router)

    return TestClient(app)


@pytest.fixture
def cleanup_simulations(neo4j_driver):
    """Clean up test simulations after each test."""
    yield
    # Clean up any ImaginedProcess and ImaginedState nodes created during tests
    with neo4j_driver.session() as session:
        session.run("""
            MATCH (s:ImaginedState)-[r]-()
            WHERE s.capability_id STARTS WITH 'test-'
            DELETE r, s
            """)
        session.run("""
            MATCH (p:ImaginedProcess)
            WHERE p.capability_id STARTS WITH 'test-'
            DELETE p
            """)


class TestSimulateAPIIntegration:
    """Integration tests for /simulate API with real Neo4j."""

    def test_health_endpoint(self, test_client):
        """Test the /sophia/health endpoint."""
        response = test_client.get("/sophia/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "sophia"

    def test_simulate_creates_process_in_neo4j(
        self, test_client, neo4j_driver, cleanup_simulations
    ):
        """Test that simulation creates an ImaginedProcess in Neo4j."""
        payload = {
            "capability_id": "test-integration-capability",
            "context": {"entity_id": "test-entity"},
            "k_steps": 3,
        }

        response = test_client.post("/sophia/simulate", json=payload)

        assert response.status_code == 200
        data = response.json()
        process_uuid = data["process_uuid"]

        # Verify the process exists in Neo4j
        with neo4j_driver.session() as session:
            result = session.run(
                """
                MATCH (p:ImaginedProcess {uuid: $uuid})
                RETURN p
                """,
                uuid=process_uuid,
            )
            record = result.single()
            assert record is not None
            process = record["p"]
            assert process["capability_id"] == "test-integration-capability"
            assert process["imagined"] is True

    def test_simulate_creates_states_in_neo4j(
        self, test_client, neo4j_driver, cleanup_simulations
    ):
        """Test that simulation creates ImaginedState nodes in Neo4j."""
        payload = {
            "capability_id": "test-states-capability",
            "context": {},
            "k_steps": 5,
        }

        response = test_client.post("/sophia/simulate", json=payload)

        assert response.status_code == 200
        data = response.json()
        process_uuid = data["process_uuid"]

        # Verify states exist in Neo4j
        with neo4j_driver.session() as session:
            result = session.run(
                """
                MATCH (p:ImaginedProcess {uuid: $uuid})-[:PREDICTS]->(s:ImaginedState)
                RETURN s ORDER BY s.step
                """,
                uuid=process_uuid,
            )
            states = list(result)
            assert len(states) == 5

            # Verify step ordering
            for i, record in enumerate(states):
                assert record["s"]["step"] == i

    def test_get_simulation_returns_stored_data(
        self, test_client, neo4j_driver, cleanup_simulations
    ):
        """Test that GET /simulate/{uuid} returns the stored simulation."""
        # Create a simulation
        create_payload = {
            "capability_id": "test-retrieve-capability",
            "context": {"entity_id": "test-entity"},
            "k_steps": 3,
        }

        create_response = test_client.post("/sophia/simulate", json=create_payload)
        assert create_response.status_code == 200
        process_uuid = create_response.json()["process_uuid"]

        # Retrieve the simulation
        response = test_client.get(f"/sophia/simulate/{process_uuid}")

        assert response.status_code == 200
        data = response.json()
        assert data["process"]["uuid"] == process_uuid
        assert data["process"]["capability_id"] == "test-retrieve-capability"
        assert len(data["states"]) == 3

    def test_simulate_with_frame_creates_relationship(
        self, test_client, neo4j_driver, cleanup_simulations
    ):
        """Test that simulation with frame_id creates TRIGGERED_SIMULATION relationship."""
        # First create a test frame in Neo4j
        frame_uuid = "test-frame-integration-123"
        with neo4j_driver.session() as session:
            session.run(
                """
                MERGE (f:PerceptionFrame {uuid: $uuid})
                SET f.created_at = datetime()
                """,
                uuid=frame_uuid,
            )

        payload = {
            "capability_id": "test-frame-capability",
            "context": {"entity_id": "test-entity"},
            "k_steps": 2,
            "frame_id": frame_uuid,
        }

        response = test_client.post("/sophia/simulate", json=payload)

        assert response.status_code == 200
        process_uuid = response.json()["process_uuid"]

        # Verify the relationship exists
        with neo4j_driver.session() as session:
            result = session.run(
                """
                MATCH (f:PerceptionFrame {uuid: $frame_uuid})
                      -[:TRIGGERED_SIMULATION]->(p:ImaginedProcess {uuid: $process_uuid})
                RETURN p, f
                """,
                process_uuid=process_uuid,
                frame_uuid=frame_uuid,
            )
            record = result.single()
            assert record is not None

            # Clean up test frame
            session.run(
                "MATCH (f:PerceptionFrame {uuid: $uuid}) DELETE f", uuid=frame_uuid
            )
