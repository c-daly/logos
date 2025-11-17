"""
Contract validation tests for the FastAPI harness.

These tests verify that the minimal FastAPI app correctly implements
the canonical Hermes OpenAPI contract defined in contracts/hermes.openapi.yaml.

Tests include:
- Request/response validation against the contract schema
- Endpoint behavior verification
- Error handling validation
"""

from pathlib import Path

from app.main import app
from fastapi.testclient import TestClient
from openapi_spec_validator import validate
from openapi_spec_validator.readers import read_from_filename

# Test client for the FastAPI app
client = TestClient(app)

# Path to the canonical contract
CONTRACT_PATH = Path(__file__).parent.parent.parent.parent / "contracts" / "hermes.openapi.yaml"


def test_openapi_contract_is_valid():
    """Verify the canonical OpenAPI contract is valid."""
    spec_dict, spec_url = read_from_filename(str(CONTRACT_PATH))
    validate(spec_dict)
    assert spec_dict["openapi"] == "3.1.0"
    assert spec_dict["info"]["title"] == "Hermes API"


def test_root_endpoint():
    """Test the root endpoint returns harness information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data
    assert "/simple_nlp" in data["endpoints"]
    assert "/embed_text" in data["endpoints"]


def test_simple_nlp_tokenize():
    """Test /simple_nlp endpoint with tokenize operation."""
    request_data = {"text": "Hello world", "operations": ["tokenize"]}

    response = client.post("/simple_nlp", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert "tokens" in data
    assert isinstance(data["tokens"], list)
    assert len(data["tokens"]) == 2
    assert data["tokens"] == ["Hello", "world"]


def test_simple_nlp_multiple_operations():
    """Test /simple_nlp endpoint with multiple operations."""
    request_data = {
        "text": "The quick brown fox",
        "operations": ["tokenize", "pos_tag", "lemmatize"],
    }

    response = client.post("/simple_nlp", json=request_data)

    assert response.status_code == 200
    data = response.json()

    # Verify tokens
    assert "tokens" in data
    assert isinstance(data["tokens"], list)
    assert len(data["tokens"]) == 4

    # Verify POS tags
    assert "pos_tags" in data
    assert isinstance(data["pos_tags"], list)
    assert len(data["pos_tags"]) == 4
    assert all("token" in tag and "tag" in tag for tag in data["pos_tags"])

    # Verify lemmas
    assert "lemmas" in data
    assert isinstance(data["lemmas"], list)
    assert len(data["lemmas"]) == 4


def test_simple_nlp_ner_operation():
    """Test /simple_nlp endpoint with NER operation."""
    request_data = {"text": "John lives in New York", "operations": ["ner"]}

    response = client.post("/simple_nlp", json=request_data)

    assert response.status_code == 200
    data = response.json()

    # Verify entities field exists (may be empty in mock)
    assert "entities" in data
    assert isinstance(data["entities"], list)


def test_simple_nlp_default_operations():
    """Test /simple_nlp endpoint uses default operations when not specified."""
    request_data = {"text": "Default test"}

    response = client.post("/simple_nlp", json=request_data)

    assert response.status_code == 200
    data = response.json()
    # Default operation is tokenize
    assert "tokens" in data


def test_simple_nlp_invalid_operation():
    """Test /simple_nlp endpoint rejects invalid operations."""
    request_data = {"text": "Test text", "operations": ["invalid_op"]}

    response = client.post("/simple_nlp", json=request_data)

    assert response.status_code == 400
    assert "Invalid operation" in response.json()["detail"]


def test_simple_nlp_missing_required_field():
    """Test /simple_nlp endpoint requires text field."""
    request_data = {"operations": ["tokenize"]}

    response = client.post("/simple_nlp", json=request_data)

    assert response.status_code == 422  # Pydantic validation error


def test_embed_text_basic():
    """Test /embed_text endpoint with basic request."""
    request_data = {"text": "Sample text for embedding"}

    response = client.post("/embed_text", json=request_data)

    assert response.status_code == 200
    data = response.json()

    # Verify response structure matches contract
    assert "embedding" in data
    assert "dimension" in data
    assert "model" in data

    # Verify embedding is a list of floats
    assert isinstance(data["embedding"], list)
    assert all(isinstance(x, (int, float)) for x in data["embedding"])

    # Verify dimension matches embedding length
    assert data["dimension"] == len(data["embedding"])

    # Verify model is returned
    assert data["model"] == "default"


def test_embed_text_with_custom_model():
    """Test /embed_text endpoint with custom model parameter."""
    request_data = {"text": "Test embedding", "model": "custom-model-v1"}

    response = client.post("/embed_text", json=request_data)

    assert response.status_code == 200
    data = response.json()

    assert data["model"] == "custom-model-v1"
    assert isinstance(data["embedding"], list)
    assert data["dimension"] > 0


def test_embed_text_empty_text():
    """Test /embed_text endpoint handles empty text."""
    request_data = {"text": ""}

    response = client.post("/embed_text", json=request_data)

    assert response.status_code == 200
    data = response.json()

    # Even empty text should return a valid embedding structure
    assert "embedding" in data
    assert "dimension" in data


def test_embed_text_missing_required_field():
    """Test /embed_text endpoint requires text field."""
    request_data = {"model": "test-model"}

    response = client.post("/embed_text", json=request_data)

    assert response.status_code == 422  # Pydantic validation error


def test_response_model_validation():
    """Test that response models properly validate against the contract."""
    # Test simple_nlp response
    response = client.post(
        "/simple_nlp", json={"text": "Validation test", "operations": ["tokenize"]}
    )
    assert response.status_code == 200
    # FastAPI with response_model ensures the response matches the schema

    # Test embed_text response
    response = client.post("/embed_text", json={"text": "Validation test"})
    assert response.status_code == 200
    data = response.json()
    # Verify all required fields per contract are present
    assert "embedding" in data
    assert "dimension" in data
    assert "model" in data


def test_openapi_schema_endpoints():
    """Test that the app exposes OpenAPI schema."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema

    # Verify our endpoints are in the schema
    assert "/simple_nlp" in schema["paths"]
    assert "/embed_text" in schema["paths"]
