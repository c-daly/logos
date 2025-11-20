"""
Integration tests for /simulate API endpoint.

Tests the FastAPI endpoint for imagination simulations.
"""

import pytest
from unittest.mock import Mock, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from logos_sophia import create_sophia_api
from logos_perception import JEPAConfig


@pytest.fixture
def mock_neo4j_driver():
    """Create a mock Neo4j driver."""
    driver = Mock()
    session = MagicMock()
    driver.session.return_value.__enter__ = Mock(return_value=session)
    driver.session.return_value.__exit__ = Mock(return_value=None)
    
    result = Mock()
    result.single.return_value = {"process_uuid": "test-uuid"}
    session.run.return_value = result
    
    return driver


@pytest.fixture
def test_client(mock_neo4j_driver):
    """Create a test client with Sophia API."""
    app = FastAPI()
    sophia_router = create_sophia_api(mock_neo4j_driver)
    app.include_router(sophia_router)
    
    return TestClient(app)


def test_health_endpoint(test_client):
    """Test the /sophia/health endpoint."""
    response = test_client.get("/sophia/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "sophia"


def test_simulate_endpoint_success(test_client):
    """Test successful simulation request."""
    payload = {
        "capability_id": "test-capability",
        "context": {"entity_id": "test-entity"},
        "k_steps": 5,
    }
    
    response = test_client.post("/sophia/simulate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "process_uuid" in data
    assert data["states_count"] == 5
    assert data["horizon"] == 5
    assert data["model_version"] == "jepa-v0.1"


def test_simulate_endpoint_with_frame_id(test_client):
    """Test simulation with frame_id."""
    payload = {
        "capability_id": "test-capability",
        "context": {"entity_id": "test-entity"},
        "k_steps": 3,
        "frame_id": "test-frame-123",
    }
    
    response = test_client.post("/sophia/simulate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["states_count"] == 3


def test_simulate_endpoint_minimal_steps(test_client):
    """Test simulation with minimum k_steps."""
    payload = {
        "capability_id": "test-capability",
        "context": {},
        "k_steps": 1,
    }
    
    response = test_client.post("/sophia/simulate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["states_count"] == 1
    assert data["horizon"] == 1


def test_simulate_endpoint_invalid_k_steps():
    """Test simulation with invalid k_steps."""
    # Test client needs to be created inline for validation test
    driver = Mock()
    session = MagicMock()
    driver.session.return_value.__enter__ = Mock(return_value=session)
    driver.session.return_value.__exit__ = Mock(return_value=None)
    
    app = FastAPI()
    sophia_router = create_sophia_api(driver)
    app.include_router(sophia_router)
    client = TestClient(app)
    
    # k_steps must be >= 1
    payload = {
        "capability_id": "test-capability",
        "context": {},
        "k_steps": 0,
    }
    
    response = client.post("/sophia/simulate", json=payload)
    assert response.status_code == 422  # Validation error


def test_simulate_endpoint_missing_capability_id():
    """Test simulation without capability_id."""
    driver = Mock()
    session = MagicMock()
    driver.session.return_value.__enter__ = Mock(return_value=session)
    driver.session.return_value.__exit__ = Mock(return_value=None)
    
    app = FastAPI()
    sophia_router = create_sophia_api(driver)
    app.include_router(sophia_router)
    client = TestClient(app)
    
    payload = {
        "context": {},
        "k_steps": 3,
    }
    
    response = client.post("/sophia/simulate", json=payload)
    assert response.status_code == 422  # Validation error


def test_get_simulation_endpoint(test_client, mock_neo4j_driver):
    """Test retrieving simulation results."""
    # First create a simulation
    create_payload = {
        "capability_id": "test-capability",
        "context": {"entity_id": "test-entity"},
        "k_steps": 3,
    }
    
    create_response = test_client.post("/sophia/simulate", json=create_payload)
    assert create_response.status_code == 200
    process_uuid = create_response.json()["process_uuid"]
    
    # Mock the retrieval to return proper result
    session = mock_neo4j_driver.session.return_value.__enter__.return_value
    result_mock = Mock()
    result_mock.single.return_value = {
        "p": {"uuid": process_uuid, "capability_id": "test-capability"},
        "states": [{"uuid": "state-1", "step": 0}],
    }
    session.run.return_value = result_mock
    
    # Now retrieve it
    response = test_client.get(f"/sophia/simulate/{process_uuid}")
    
    # Should now succeed with our mocked data
    assert response.status_code == 200
    data = response.json()
    assert data["process"]["uuid"] == process_uuid


def test_simulate_endpoint_complex_context(test_client):
    """Test simulation with complex context data."""
    payload = {
        "capability_id": "pick-and-place",
        "context": {
            "entity_id": "robot-arm-1",
            "target_position": {"x": 1.5, "y": 2.0, "z": 0.5},
            "sensor_readings": {
                "force": [0.1, 0.2, 0.3],
                "temperature": 22.5,
            },
            "constraints": ["avoid_collision", "minimize_energy"],
        },
        "k_steps": 10,
    }
    
    response = test_client.post("/sophia/simulate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["states_count"] == 10


def test_simulate_default_k_steps(test_client):
    """Test that k_steps defaults to 5."""
    payload = {
        "capability_id": "test-capability",
        "context": {},
    }
    
    response = test_client.post("/sophia/simulate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["horizon"] == 5  # default value
    assert data["states_count"] == 5
