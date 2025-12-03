"""
Integration tests for SimulationService.

Tests the simulation service with real Neo4j database.
Validates that simulations are properly stored and retrieved.
"""

import os

import pytest
from neo4j import GraphDatabase

from logos_perception import JEPAConfig, SimulationRequest
from logos_sophia import SimulationService
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
    """Skip tests if Neo4j is not available."""
    if not is_container_running(NEO4J_CONFIG.container):
        pytest.skip(
            "Neo4j not available. Start with: "
            "docker compose -f tests/e2e/stack/logos/docker-compose.test.yml up -d"
        )

    try:
        wait_for_neo4j(NEO4J_CONFIG, timeout=NEO4J_WAIT_TIMEOUT)
    except (RuntimeError, FileNotFoundError) as exc:
        pytest.skip(f"Neo4j not ready: {exc}")


@pytest.fixture(scope="module")
def neo4j_driver():
    """Create a real Neo4j driver."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    yield driver
    driver.close()


@pytest.fixture
def simulation_service(neo4j_driver):
    """Create a SimulationService with real Neo4j."""
    return SimulationService(neo4j_driver)


@pytest.fixture
def cleanup_simulations(neo4j_driver):
    """Clean up test simulations after each test."""
    yield
    with neo4j_driver.session() as session:
        session.run(
            """
            MATCH (s:ImaginedState)
            WHERE s.uuid STARTS WITH 'test-' OR EXISTS {
                MATCH (s)<-[:HAS_STATE]-(p:ImaginedProcess)
                WHERE p.capability_id STARTS WITH 'test-'
            }
            DETACH DELETE s
            """
        )
        session.run(
            """
            MATCH (p:ImaginedProcess)
            WHERE p.capability_id STARTS WITH 'test-'
            DETACH DELETE p
            """
        )


class TestSimulationServiceIntegration:
    """Integration tests for SimulationService with real Neo4j."""

    def test_run_simulation_stores_process(
        self, simulation_service, neo4j_driver, cleanup_simulations
    ):
        """Test that run_simulation creates an ImaginedProcess in Neo4j."""
        request = SimulationRequest(
            capability_id="test-integration-process",
            context={"entity_id": "test-entity"},
            k_steps=3,
        )

        result = simulation_service.run_simulation(request)
        process_uuid = result.process.uuid

        # Verify in Neo4j
        with neo4j_driver.session() as session:
            record = session.run(
                """
                MATCH (p:ImaginedProcess {uuid: $uuid})
                RETURN p
                """,
                uuid=process_uuid,
            ).single()

            assert record is not None
            process = record["p"]
            assert process["capability_id"] == "test-integration-process"
            assert process["imagined"] is True
            assert process["horizon"] == 3

    def test_run_simulation_stores_states(
        self, simulation_service, neo4j_driver, cleanup_simulations
    ):
        """Test that run_simulation creates ImaginedState nodes."""
        request = SimulationRequest(
            capability_id="test-integration-states",
            context={},
            k_steps=5,
        )

        result = simulation_service.run_simulation(request)
        process_uuid = result.process.uuid

        # Verify states in Neo4j
        with neo4j_driver.session() as session:
            states = list(
                session.run(
                    """
                MATCH (p:ImaginedProcess {uuid: $uuid})-[:PREDICTS]->(s:ImaginedState)
                RETURN s ORDER BY s.step
                """,
                    uuid=process_uuid,
                )
            )

            assert len(states) == 5
            for i, record in enumerate(states):
                state = record["s"]
                assert state["step"] == i
                assert "confidence" in state
                # Embedding is stored in Milvus, not Neo4j

    def test_run_simulation_confidence_degrades(
        self, simulation_service, neo4j_driver, cleanup_simulations
    ):
        """Test that confidence decreases over horizon in stored states."""
        request = SimulationRequest(
            capability_id="test-integration-confidence",
            context={},
            k_steps=5,
        )

        result = simulation_service.run_simulation(request)
        process_uuid = result.process.uuid

        with neo4j_driver.session() as session:
            states = list(
                session.run(
                    """
                MATCH (p:ImaginedProcess {uuid: $uuid})-[:PREDICTS]->(s:ImaginedState)
                RETURN s.step AS step, s.confidence AS confidence
                ORDER BY s.step
                """,
                    uuid=process_uuid,
                )
            )

            confidences = [s["confidence"] for s in states]

            # First state should have highest confidence
            assert confidences[0] == 1.0

            # Confidence should decrease
            for i in range(1, len(confidences)):
                assert confidences[i] <= confidences[i - 1]

    def test_get_simulation_results_returns_stored_data(
        self, simulation_service, neo4j_driver, cleanup_simulations
    ):
        """Test that get_simulation_results retrieves stored simulation."""
        request = SimulationRequest(
            capability_id="test-integration-retrieve",
            context={"entity_id": "test-entity"},
            k_steps=3,
        )

        result = simulation_service.run_simulation(request)
        process_uuid = result.process.uuid

        # Retrieve using the service
        retrieved = simulation_service.get_simulation_results(process_uuid)

        assert retrieved is not None
        assert retrieved["process"]["uuid"] == process_uuid
        assert retrieved["process"]["capability_id"] == "test-integration-retrieve"
        assert len(retrieved["states"]) == 3

    def test_get_simulation_results_not_found(self, simulation_service):
        """Test that get_simulation_results returns None for nonexistent UUID."""
        result = simulation_service.get_simulation_results("nonexistent-uuid-12345")
        assert result is None

    def test_run_simulation_with_custom_config(
        self, neo4j_driver, cleanup_simulations
    ):
        """Test simulation with custom JEPA configuration stores correct data."""
        config = JEPAConfig(
            model_version="jepa-v0.3-test",
            embedding_dim=512,
        )

        service = SimulationService(neo4j_driver, jepa_config=config)

        request = SimulationRequest(
            capability_id="test-integration-custom-config",
            context={},
            k_steps=2,
        )

        result = service.run_simulation(request)
        process_uuid = result.process.uuid

        with neo4j_driver.session() as session:
            record = session.run(
                """
                MATCH (p:ImaginedProcess {uuid: $uuid})
                RETURN p.model_version AS model_version
                """,
                uuid=process_uuid,
            ).single()

            assert record["model_version"] == "jepa-v0.3-test"

    def test_run_simulation_stores_assumptions(
        self, simulation_service, neo4j_driver, cleanup_simulations
    ):
        """Test that simulation context is stored as assumptions."""
        context = {
            "entity_id": "test-entity",
            "initial_position": [1.0, 2.0, 3.0],
            "sensor_data": {"temperature": 22.5},
        }

        request = SimulationRequest(
            capability_id="test-integration-assumptions",
            context=context,
            k_steps=2,
        )

        result = simulation_service.run_simulation(request)
        process_uuid = result.process.uuid

        with neo4j_driver.session() as session:
            record = session.run(
                """
                MATCH (p:ImaginedProcess {uuid: $uuid})
                RETURN p.assumptions AS assumptions
                """,
                uuid=process_uuid,
            ).single()

            # Assumptions should be stored (possibly as JSON string)
            assert record["assumptions"] is not None
