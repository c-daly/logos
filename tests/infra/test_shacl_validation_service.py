#!/usr/bin/env python3
"""
Tests for SHACL Validation Service API

Tests the HTTP endpoints of the SHACL validation service.

FLEXIBLE ONTOLOGY:
All nodes use logos:Node with required properties:
- uuid, name, is_type_definition, type, ancestors

Reference: docs/plans/2025-12-30-flexible-ontology-design.md
"""

# Import the app
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add infra to path so we can import the service
infra_path = Path(__file__).parent.parent.parent / "infra"
sys.path.insert(0, str(infra_path))

from shacl_validation_service import app, load_shacl_shapes  # noqa: E402


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI app."""
    # Manually trigger startup since TestClient doesn't always call lifespan
    load_shacl_shapes()
    return TestClient(app)


def test_root_endpoint(client):
    """Test that root endpoint returns service information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "LOGOS SHACL Validation Service"
    assert data["version"] == "1.0.0"
    assert "docs" in data
    assert "health" in data


def test_health_endpoint(client):
    """Test that health endpoint returns status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert data["shapes_loaded"] is True
    assert data["shapes_count"] > 0


def test_shapes_info_endpoint(client):
    """Test that shapes info endpoint returns shape statistics."""
    response = client.get("/shapes")
    assert response.status_code == 200
    data = response.json()
    assert "total_triples" in data
    assert "node_shapes" in data
    assert "property_shapes" in data
    assert data["total_triples"] > 0
    assert data["shapes_file"] == "shacl_shapes.ttl"


def test_validate_valid_node(client):
    """Test validation of valid Node data (flexible ontology)."""
    valid_data = """
@prefix logos: <http://logos.ai/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

logos:instance-test-001 a logos:Node ;
    logos:uuid "instance-test-001" ;
    logos:name "Test Entity" ;
    logos:is_type_definition false ;
    logos:type "entity" ;
    logos:ancestors ("entity" "thing") ;
    logos:description "A valid test entity" .
"""

    response = client.post(
        "/validate", json={"data": valid_data, "format": "turtle", "inference": "none"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["conforms"] is True
    assert data["violations_count"] == 0


def test_validate_node_missing_uuid(client):
    """Test validation of Node missing required UUID."""
    invalid_data = """
@prefix logos: <http://logos.ai/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

logos:node-test-001 a logos:Node ;
    logos:name "Test Node" ;
    logos:is_type_definition false ;
    logos:type "entity" ;
    logos:ancestors ("entity" "thing") .
"""

    response = client.post(
        "/validate",
        json={"data": invalid_data, "format": "turtle", "inference": "none"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["conforms"] is False
    assert data["violations_count"] > 0


def test_validate_node_missing_name(client):
    """Test validation of Node missing required name."""
    invalid_data = """
@prefix logos: <http://logos.ai/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

logos:node-test-001 a logos:Node ;
    logos:uuid "node-test-001" ;
    logos:is_type_definition false ;
    logos:type "entity" ;
    logos:ancestors ("entity" "thing") .
"""

    response = client.post("/validate", json={"data": invalid_data, "format": "turtle"})

    assert response.status_code == 200
    data = response.json()
    assert data["conforms"] is False
    assert data["violations_count"] > 0


def test_validate_node_missing_type(client):
    """Test validation of Node missing required type."""
    invalid_data = """
@prefix logos: <http://logos.ai/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

logos:node-test-001 a logos:Node ;
    logos:uuid "node-test-001" ;
    logos:name "Test Node" ;
    logos:is_type_definition false ;
    logos:ancestors ("entity" "thing") .
"""

    response = client.post("/validate", json={"data": invalid_data, "format": "turtle"})

    assert response.status_code == 200
    data = response.json()
    assert data["conforms"] is False
    assert data["violations_count"] > 0


def test_validate_malformed_rdf(client):
    """Test validation with malformed RDF data."""
    malformed_data = """
This is not valid RDF data at all!
"""

    response = client.post(
        "/validate", json={"data": malformed_data, "format": "turtle"}
    )

    assert response.status_code == 400
    assert "Validation failed" in response.json()["detail"]


def test_validate_with_rdfs_inference(client):
    """Test validation with RDFS inference enabled."""
    valid_data = """
@prefix logos: <http://logos.ai/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

logos:instance-test-001 a logos:Node ;
    logos:uuid "instance-test-001" ;
    logos:name "Test Entity" ;
    logos:is_type_definition false ;
    logos:type "entity" ;
    logos:ancestors ("entity" "thing") .
"""

    response = client.post(
        "/validate", json={"data": valid_data, "format": "turtle", "inference": "rdfs"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "conforms" in data


def test_validate_abort_on_first(client):
    """Test validation with abort_on_first option."""
    invalid_data = """
@prefix logos: <http://logos.ai/ontology#> .

logos:node-1 a logos:Node ;
    logos:uuid "node-1" ;
    logos:name "Node1" .

logos:node-2 a logos:Node ;
    logos:uuid "node-2" ;
    logos:name "Node2" .
"""

    response = client.post(
        "/validate",
        json={"data": invalid_data, "format": "turtle", "abort_on_first": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["conforms"] is False


def test_validate_valid_type_definition(client):
    """Test validation of valid type definition node."""
    valid_data = """
@prefix logos: <http://logos.ai/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

logos:type-robot a logos:Node ;
    logos:uuid "5e6f7a8b-9c0d-5e1f-2a3b-4c5d6e7f8a9b" ;
    logos:name "robot" ;
    logos:is_type_definition true ;
    logos:type "robot" ;
    logos:ancestors ("entity" "thing") .
"""

    response = client.post("/validate", json={"data": valid_data, "format": "turtle"})

    assert response.status_code == 200
    data = response.json()
    assert data["conforms"] is True
    assert data["violations_count"] == 0


def test_validate_bootstrap_type(client):
    """Test validation of bootstrap type with empty ancestors."""
    valid_data = """
@prefix logos: <http://logos.ai/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

logos:type-concept a logos:Node ;
    logos:uuid "f8b89a6c-9c3e-5e4d-b2f1-83a4d7e4c5f2" ;
    logos:name "concept" ;
    logos:is_type_definition true ;
    logos:type "concept" ;
    logos:ancestors () .
"""

    response = client.post("/validate", json={"data": valid_data, "format": "turtle"})

    assert response.status_code == 200
    data = response.json()
    assert data["conforms"] is True
    assert data["violations_count"] == 0


def test_validate_node_with_domain_properties(client):
    """Test validation of Node with optional domain properties."""
    valid_data = """
@prefix logos: <http://logos.ai/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

logos:instance-cube-001 a logos:Node ;
    logos:uuid "instance-cube-001" ;
    logos:name "Test Cube" ;
    logos:is_type_definition false ;
    logos:type "entity" ;
    logos:ancestors ("entity" "thing") ;
    logos:width "0.1"^^xsd:decimal ;
    logos:height "0.1"^^xsd:decimal ;
    logos:depth "0.1"^^xsd:decimal ;
    logos:mass "0.5"^^xsd:decimal .
"""

    response = client.post("/validate", json={"data": valid_data, "format": "turtle"})

    assert response.status_code == 200
    data = response.json()
    assert data["conforms"] is True
    assert data["violations_count"] == 0
