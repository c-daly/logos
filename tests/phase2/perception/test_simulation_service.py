"""
Integration tests for simulation service and /simulate endpoint.

Tests the full flow from API request to Neo4j/Milvus storage.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from logos_perception import SimulationRequest
from logos_sophia import SimulationService
from logos_perception import JEPAConfig


@pytest.fixture
def mock_neo4j_driver():
    """Create a mock Neo4j driver."""
    driver = Mock()
    session = MagicMock()
    driver.session.return_value.__enter__ = Mock(return_value=session)
    driver.session.return_value.__exit__ = Mock(return_value=None)
    
    # Mock result with single() method
    result = Mock()
    result.single.return_value = {"process_uuid": "test-uuid"}
    session.run.return_value = result
    
    return driver


def test_simulation_service_initialization(mock_neo4j_driver):
    """Test simulation service can be initialized."""
    service = SimulationService(mock_neo4j_driver)
    assert service.neo4j_driver == mock_neo4j_driver
    assert service.jepa_runner is not None


def test_run_simulation_creates_imagined_process(mock_neo4j_driver):
    """Test that running simulation creates an ImaginedProcess."""
    service = SimulationService(mock_neo4j_driver)
    
    request = SimulationRequest(
        capability_id="test-capability",
        context={"entity_id": "test-entity"},
        k_steps=3,
    )
    
    result = service.run_simulation(request)
    
    assert result.process.capability_id == "test-capability"
    assert result.process.imagined is True
    assert result.process.horizon == 3
    assert len(result.states) == 3


def test_run_simulation_stores_in_neo4j(mock_neo4j_driver):
    """Test that simulation results are stored in Neo4j."""
    service = SimulationService(mock_neo4j_driver)
    
    request = SimulationRequest(
        capability_id="test-capability",
        context={"entity_id": "test-entity"},
        k_steps=2,
    )
    
    result = service.run_simulation(request)
    
    # Verify Neo4j session was used
    assert mock_neo4j_driver.session.called
    
    # Verify queries were executed
    session = mock_neo4j_driver.session.return_value.__enter__.return_value
    assert session.run.called
    
    # Check that process and states were stored
    calls = session.run.call_args_list
    assert len(calls) >= 2  # At least process creation and states creation


def test_run_simulation_with_frame_link(mock_neo4j_driver):
    """Test simulation with frame_id links frame to process."""
    service = SimulationService(mock_neo4j_driver)
    
    request = SimulationRequest(
        capability_id="test-capability",
        context={"entity_id": "test-entity"},
        k_steps=2,
        frame_id="test-frame-123",
    )
    
    result = service.run_simulation(request)
    
    # Verify frame linking was attempted
    session = mock_neo4j_driver.session.return_value.__enter__.return_value
    calls = session.run.call_args_list
    
    # Should have process, states, and frame link queries
    assert len(calls) >= 3


def test_get_simulation_results(mock_neo4j_driver):
    """Test retrieving simulation results from Neo4j."""
    service = SimulationService(mock_neo4j_driver)
    
    # Mock the query result
    session = mock_neo4j_driver.session.return_value.__enter__.return_value
    result = Mock()
    result.single.return_value = {
        "p": {
            "uuid": "process-123",
            "capability_id": "test-capability",
            "imagined": True,
        },
        "states": [
            {"uuid": "state-1", "step": 0, "confidence": 1.0},
            {"uuid": "state-2", "step": 1, "confidence": 0.9},
        ],
    }
    session.run.return_value = result
    
    results = service.get_simulation_results("process-123")
    
    assert results is not None
    assert results["process"]["uuid"] == "process-123"
    assert len(results["states"]) == 2


def test_get_simulation_results_not_found(mock_neo4j_driver):
    """Test retrieving non-existent simulation returns None."""
    service = SimulationService(mock_neo4j_driver)
    
    # Mock empty result
    session = mock_neo4j_driver.session.return_value.__enter__.return_value
    result = Mock()
    result.single.return_value = None
    session.run.return_value = result
    
    results = service.get_simulation_results("nonexistent-uuid")
    
    assert results is None


def test_simulation_service_with_custom_jepa_config(mock_neo4j_driver):
    """Test simulation service with custom JEPA configuration."""
    config = JEPAConfig(
        model_version="jepa-v0.3",
        embedding_dim=512,
    )
    
    service = SimulationService(mock_neo4j_driver, jepa_config=config)
    
    request = SimulationRequest(
        capability_id="test-capability",
        context={},
        k_steps=2,
    )
    
    result = service.run_simulation(request)
    
    assert result.process.model_version == "jepa-v0.3"
    # Embeddings should use custom dimension
    assert len(result.states[0].embedding) == 512


def test_simulation_preserves_context_assumptions(mock_neo4j_driver):
    """Test that simulation captures context as assumptions."""
    service = SimulationService(mock_neo4j_driver)
    
    context = {
        "entity_id": "test-entity",
        "initial_position": [1.0, 2.0, 3.0],
        "sensor_data": {"temperature": 22.5},
    }
    
    request = SimulationRequest(
        capability_id="test-capability",
        context=context,
        k_steps=2,
    )
    
    result = service.run_simulation(request)
    
    # Assumptions should match the context
    assert result.process.assumptions == context
