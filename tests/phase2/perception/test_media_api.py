"""
Tests for media ingestion API endpoints.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from logos_perception import create_media_api


@pytest.fixture
def mock_neo4j_driver():
    """Create a mock Neo4j driver."""
    driver = Mock()
    session = MagicMock()
    driver.session.return_value.__enter__ = Mock(return_value=session)
    driver.session.return_value.__exit__ = Mock(return_value=None)

    # Mock successful query results
    result = Mock()
    result.single.return_value = {"frame_id": "test-frame-id"}
    session.run.return_value = result

    return driver


@pytest.fixture
def client(mock_neo4j_driver, tmp_path):
    """Create test client with media API."""
    from fastapi import FastAPI
    from slowapi import Limiter
    from slowapi.util import get_remote_address

    app = FastAPI()
    # Use a more permissive rate limiter for tests
    app.state.limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["1000/minute"]  # High limit for tests
    )

    media_router = create_media_api(mock_neo4j_driver, tmp_path)
    app.include_router(media_router)

    return TestClient(app)


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/media/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["service"] == "media-ingest"
    assert "neo4j_connected" in data
    assert "milvus_connected" in data


def test_upload_media_without_auth(client):
    """Test upload without authentication fails."""
    response = client.post(
        "/media/upload",
        files={"file": ("test.jpg", b"fake image data", "image/jpeg")},
    )

    assert response.status_code == 403  # Forbidden (no auth header)


def test_upload_media_with_invalid_token(client):
    """Test upload with invalid token fails."""
    response = client.post(
        "/media/upload",
        files={"file": ("test.jpg", b"fake image data", "image/jpeg")},
        headers={"Authorization": "Bearer short"},
    )

    assert response.status_code == 401  # Unauthorized


def test_upload_media_success(client):
    """Test successful media upload."""
    response = client.post(
        "/media/upload",
        files={"file": ("test.jpg", b"fake image data", "image/jpeg")},
        data={"metadata": '{"source": "test"}'},
        headers={"Authorization": "Bearer valid-test-token-12345"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "media_id" in data
    assert data["format"] == "image/jpeg"
    assert data["status"] == "uploaded"
    assert data["size_bytes"] == len(b"fake image data")


def test_upload_media_with_invalid_metadata(client):
    """Test upload with invalid JSON metadata fails."""
    response = client.post(
        "/media/upload",
        files={"file": ("test.jpg", b"fake image data", "image/jpeg")},
        data={"metadata": "invalid json"},
        headers={"Authorization": "Bearer valid-test-token-12345"},
    )

    # Should return 500 because the JSON parsing error is caught and wrapped
    assert response.status_code == 500
    assert "Upload failed" in response.json()["detail"]


def test_start_stream_success(client, mock_neo4j_driver):
    """Test starting a media stream."""
    response = client.post(
        "/media/stream/start",
        json={"source": "webcam", "fps": 10, "format": "image/jpeg"},
        headers={"Authorization": "Bearer valid-test-token-12345"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "stream_id" in data
    assert data["source"] == "webcam"
    assert data["status"] == "active"

    # Verify Neo4j was called to store stream metadata
    session = mock_neo4j_driver.session.return_value.__enter__.return_value
    assert session.run.called


def test_stop_stream_success(client, mock_neo4j_driver):
    """Test stopping a media stream."""
    # Mock successful stream stop
    session = mock_neo4j_driver.session.return_value.__enter__.return_value
    result = Mock()
    result.single.return_value = {"stream_id": "test-stream-123"}
    session.run.return_value = result

    response = client.post(
        "/media/stream/test-stream-123/stop",
        headers={"Authorization": "Bearer valid-test-token-12345"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["stream_id"] == "test-stream-123"
    assert data["status"] == "stopped"


def test_stop_stream_not_found(client, mock_neo4j_driver):
    """Test stopping a non-existent stream."""
    # Mock stream not found
    session = mock_neo4j_driver.session.return_value.__enter__.return_value
    result = Mock()
    result.single.return_value = None
    session.run.return_value = result

    response = client.post(
        "/media/stream/nonexistent-stream/stop",
        headers={"Authorization": "Bearer valid-test-token-12345"},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_get_frame_metadata_success(client, mock_neo4j_driver):
    """Test retrieving frame metadata."""
    # Mock frame metadata query
    session = mock_neo4j_driver.session.return_value.__enter__.return_value
    result = Mock()
    result.single.return_value = {
        "f": {
            "uuid": "frame-123",
            "format": "image/jpeg",
            "timestamp": "2025-11-20T00:00:00Z",
        }
    }
    session.run.return_value = result

    response = client.get(
        "/media/frames/frame-123",
        headers={"Authorization": "Bearer valid-test-token-12345"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["uuid"] == "frame-123"


def test_get_frame_metadata_not_found(client, mock_neo4j_driver):
    """Test retrieving non-existent frame metadata."""
    # Mock frame not found
    session = mock_neo4j_driver.session.return_value.__enter__.return_value
    result = Mock()
    result.single.return_value = None
    session.run.return_value = result

    response = client.get(
        "/media/frames/nonexistent-frame",
        headers={"Authorization": "Bearer valid-test-token-12345"},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_rate_limiting():
    """Test that rate limiting can be configured."""
    # Rate limiting is documented and can be added with slowapi decorators
    # For now, this is a placeholder test
    # In production, rate limiting would be enforced at the API gateway level
    pass
