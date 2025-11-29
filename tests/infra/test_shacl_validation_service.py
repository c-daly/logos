#!/usr/bin/env python3
"""
Tests for SHACL Validation Service API

Tests the HTTP endpoints of the SHACL validation service.
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


def test_validate_valid_entity(client):
    """Test validation of valid entity data."""
    valid_data = """
@prefix logos: <http://logos.ontology/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

logos:entity-test-001 a logos:Entity ;
    logos:uuid "entity-test-001" ;
    logos:name "Test Entity" ;
    logos:description "A valid test entity" .
"""

    response = client.post(
        "/validate", json={"data": valid_data, "format": "turtle", "inference": "none"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["conforms"] is True
    assert data["violations_count"] == 0


def test_validate_invalid_entity_wrong_uuid_pattern(client):
    """Test validation of entity with wrong UUID pattern."""
    invalid_data = """
@prefix logos: <http://logos.ontology/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

logos:entity-test-001 a logos:Entity ;
    logos:uuid "wrong-prefix-001" ;
    logos:name "Test Entity" .
"""

    response = client.post(
        "/validate",
        json={"data": invalid_data, "format": "turtle", "inference": "none"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["conforms"] is False
    assert data["violations_count"] > 0
    assert "entity-" in data["report_text"]


def test_validate_invalid_entity_missing_uuid(client):
    """Test validation of entity missing required UUID."""
    invalid_data = """
@prefix logos: <http://logos.ontology/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

logos:entity-test-001 a logos:Entity ;
    logos:name "Test Entity" .
"""

    response = client.post(
        "/validate",
        json={"data": invalid_data, "format": "turtle", "inference": "none"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["conforms"] is False
    assert data["violations_count"] > 0


def test_validate_valid_concept(client):
    """Test validation of valid concept data."""
    valid_data = """
@prefix logos: <http://logos.ontology/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

logos:concept-test-001 a logos:Concept ;
    logos:uuid "concept-test-001" ;
    logos:name "TestConcept" ;
    logos:description "A valid test concept" .
"""

    response = client.post("/validate", json={"data": valid_data, "format": "turtle"})

    assert response.status_code == 200
    data = response.json()
    assert data["conforms"] is True
    assert data["violations_count"] == 0


def test_validate_invalid_concept_missing_name(client):
    """Test validation of concept missing required name."""
    invalid_data = """
@prefix logos: <http://logos.ontology/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

logos:concept-test-001 a logos:Concept ;
    logos:uuid "concept-test-001" .
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

    response = client.post("/validate", json={"data": malformed_data, "format": "turtle"})

    assert response.status_code == 400
    assert "Validation failed" in response.json()["detail"]


def test_validate_with_rdfs_inference(client):
    """Test validation with RDFS inference enabled."""
    valid_data = """
@prefix logos: <http://logos.ontology/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

logos:entity-test-001 a logos:Entity ;
    logos:uuid "entity-test-001" ;
    logos:name "Test Entity" .
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
@prefix logos: <http://logos.ontology/> .

logos:entity-1 a logos:Entity ;
    logos:uuid "wrong-001" .

logos:entity-2 a logos:Entity ;
    logos:uuid "wrong-002" .
"""

    response = client.post(
        "/validate",
        json={"data": invalid_data, "format": "turtle", "abort_on_first": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["conforms"] is False


def test_validate_spatial_properties(client):
    """Test validation of entity with spatial properties."""
    valid_data = """
@prefix logos: <http://logos.ontology/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

logos:entity-cube-001 a logos:Entity ;
    logos:uuid "entity-cube-001" ;
    logos:name "Test Cube" ;
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


def test_validate_negative_spatial_property(client):
    """Test validation rejects negative spatial property values."""
    invalid_data = """
@prefix logos: <http://logos.ontology/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

logos:entity-cube-001 a logos:Entity ;
    logos:uuid "entity-cube-001" ;
    logos:name "Invalid Cube" ;
    logos:width "-0.1"^^xsd:decimal ;
    logos:height "0.1"^^xsd:decimal .
"""

    response = client.post("/validate", json={"data": invalid_data, "format": "turtle"})

    assert response.status_code == 200
    data = response.json()
    assert data["conforms"] is False
    assert data["violations_count"] > 0
