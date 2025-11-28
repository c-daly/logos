"""
Shared fixtures for Phase 2 E2E tests.

Provides reusable fixtures for:
- Service health checks
- SDK client initialization
- Database cleanup
- Test data
"""

import os
from collections.abc import Generator
from typing import Any

import pytest
import requests

from logos_test_utils.env import load_stack_env
from logos_test_utils.milvus import get_milvus_config
from logos_test_utils.neo4j import get_neo4j_config

# Try to import Apollo SDK clients
try:
    from apollo.client.hermes_client import HermesClient
    from apollo.client.persona_client import PersonaClient
    from apollo.client.sophia_client import SophiaClient
    from apollo.config.settings import HermesConfig, PersonaApiConfig, SophiaConfig

    APOLLO_SDK_AVAILABLE = True
except ImportError:
    APOLLO_SDK_AVAILABLE = False

# Load stack environment and configs
STACK_ENV = load_stack_env()
NEO4J_CONFIG = get_neo4j_config(STACK_ENV)
MILVUS_CONFIG = get_milvus_config(STACK_ENV)

# Service URLs
SOPHIA_URL = os.getenv("SOPHIA_URL", "http://localhost:8001")
HERMES_URL = os.getenv("HERMES_URL", "http://localhost:8002")
APOLLO_URL = os.getenv("APOLLO_URL", "http://localhost:8003")

# Extract Neo4j/Milvus config from helpers
NEO4J_URI = NEO4J_CONFIG.uri
NEO4J_USER = NEO4J_CONFIG.user
NEO4J_PASSWORD = NEO4J_CONFIG.password
MILVUS_HOST = MILVUS_CONFIG.host
MILVUS_PORT = int(MILVUS_CONFIG.port)


# ============================================================================
# Service Health Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def services_running() -> dict[str, bool]:
    """Check that all required services are healthy before tests."""
    services = {
        "sophia": False,
        "hermes": False,
        "neo4j": False,
    }

    # Check Sophia
    try:
        response = requests.get(f"{SOPHIA_URL}/health", timeout=5)
        services["sophia"] = response.status_code == 200
    except Exception:
        pass

    # Check Hermes
    try:
        response = requests.get(f"{HERMES_URL}/health", timeout=5)
        services["hermes"] = response.status_code == 200
    except Exception:
        pass

    # Check Neo4j
    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            record = result.single()
            services["neo4j"] = record["test"] == 1 if record else False
        driver.close()
    except Exception:
        pass

    return services


@pytest.fixture(scope="session")
def require_services(services_running: dict[str, bool]):
    """Ensure all required services are running."""
    missing = [name for name, running in services_running.items() if not running]

    if missing:
        pytest.skip(
            f"Required services not available: {', '.join(missing)}. "
            f"Start services with: docker compose -f infra/docker-compose.hcg.dev.yml up -d"
        )


# ============================================================================
# SDK Client Fixtures
# ============================================================================


@pytest.fixture
def sophia_client() -> SophiaClient:
    """Create configured SophiaClient instance."""
    if not APOLLO_SDK_AVAILABLE:
        pytest.skip("Apollo SDK not available")

    # Parse URL to extract host and port
    url = SOPHIA_URL.replace("http://", "").replace("https://", "")
    parts = url.split(":")
    host = parts[0]
    port = int(parts[1]) if len(parts) > 1 else 8001

    config = SophiaConfig(host=host, port=port)
    return SophiaClient(config)


@pytest.fixture
def hermes_client() -> HermesClient:
    """Create configured HermesClient instance."""
    if not APOLLO_SDK_AVAILABLE:
        pytest.skip("Apollo SDK not available")

    # Parse URL to extract host and port
    url = HERMES_URL.replace("http://", "").replace("https://", "")
    parts = url.split(":")
    host = parts[0]
    port = int(parts[1]) if len(parts) > 1 else 8002

    config = HermesConfig(host=host, port=port)
    return HermesClient(config)


@pytest.fixture
def persona_client() -> PersonaClient:
    """Create configured PersonaClient instance."""
    if not APOLLO_SDK_AVAILABLE:
        pytest.skip("Apollo SDK not available")

    # PersonaClient connects to Sophia's persona endpoints
    url = SOPHIA_URL.replace("http://", "").replace("https://", "")
    parts = url.split(":")
    host = parts[0]
    port = int(parts[1]) if len(parts) > 1 else 8001

    config = PersonaApiConfig(host=host, port=port)
    return PersonaClient(config)


@pytest.fixture
def all_clients(
    sophia_client: SophiaClient,
    hermes_client: HermesClient,
    persona_client: PersonaClient,
) -> dict[str, Any]:
    """Provide all SDK clients in one fixture."""
    return {
        "sophia": sophia_client,
        "hermes": hermes_client,
        "persona": persona_client,
    }


# ============================================================================
# Database Cleanup Fixtures
# ============================================================================


@pytest.fixture
def clean_neo4j() -> Generator[None, None, None]:
    """Reset Neo4j test data between tests."""
    # Setup: clean before test
    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

        with driver.session() as session:
            # Delete test nodes (those with test_ prefix in uuid or name)
            session.run(
                """
                MATCH (n)
                WHERE n.uuid STARTS WITH 'test_'
                   OR n.uuid STARTS WITH 'test-'
                   OR n.name STARTS WITH 'Test'
                   OR n.name STARTS WITH 'test_'
                DETACH DELETE n
                """
            )

        driver.close()
    except Exception:
        pass  # Neo4j cleanup is best-effort

    yield

    # Teardown: clean after test
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

        with driver.session() as session:
            session.run(
                """
                MATCH (n)
                WHERE n.uuid STARTS WITH 'test_'
                   OR n.uuid STARTS WITH 'test-'
                   OR n.name STARTS WITH 'Test'
                   OR n.name STARTS WITH 'test_'
                DETACH DELETE n
                """
            )

        driver.close()
    except Exception:
        pass


@pytest.fixture
def clean_milvus() -> Generator[None, None, None]:
    """Reset Milvus test collections between tests.

    Retries connection to handle Milvus initialization delays.
    """
    import time

    # Setup: clean before test
    max_retries = 5
    retry_delay = 2
    alias = "test_cleanup"

    for attempt in range(max_retries):
        try:
            from pymilvus import Collection, connections, utility

            connections.connect(
                alias=alias,
                host=MILVUS_HOST,
                port=MILVUS_PORT,
            )

            # Delete test data from collections
            collections = utility.list_collections(using=alias)
            for coll_name in collections:
                if "test" in coll_name.lower():
                    collection = Collection(coll_name)
                    collection.drop()

            connections.disconnect(alias)
            break  # Success
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            # Last attempt failed - this is best-effort, so pass
            pass

    yield

    # Teardown: clean after test
    try:
        connections.connect(
            alias=alias,
            host=MILVUS_HOST,
            port=MILVUS_PORT,
        )

        collections = utility.list_collections(using=alias)
        for coll_name in collections:
            if "test" in coll_name.lower():
                collection = Collection(coll_name)
                collection.drop()

        connections.disconnect(alias)
    except Exception:
        pass


# ============================================================================
# Test Data Fixtures
# ============================================================================


@pytest.fixture
def sample_embeddings() -> dict[str, Any]:
    """Provide sample embedding data for tests."""
    return {
        "text": "This is a test embedding",
        "model": "default",
        "vector": [0.1] * 384,  # Mock 384-dimensional embedding
        "metadata": {
            "source": "test",
            "timestamp": "2025-11-24T00:00:00Z",
        },
    }


@pytest.fixture
def sample_cwmstate() -> dict[str, Any]:
    """Provide sample CWMState envelope for tests."""
    return {
        "state_id": "test-state-001",
        "model_type": "plan",
        "source": "sophia",
        "timestamp": "2025-11-24T00:00:00Z",
        "confidence": 0.95,
        "status": "active",
        "links": [],
        "tags": ["test"],
        "data": {
            "goal": "Test goal",
            "plan_steps": [
                {"name": "step1", "description": "First step"},
                {"name": "step2", "description": "Second step"},
            ],
        },
    }


@pytest.fixture
def sample_persona_entry() -> dict[str, Any]:
    """Provide sample persona entry for tests."""
    return {
        "entry_type": "reflection",
        "content": "Test reflection content",
        "summary": "Test summary",
        "sentiment": "neutral",
        "confidence": 0.8,
        "related_process_ids": [],
        "related_goal_ids": [],
        "emotion_tags": ["curious"],
        "metadata": {
            "test": True,
        },
    }


@pytest.fixture
def sample_simulation_request() -> dict[str, Any]:
    """Provide sample simulation request for tests."""
    return {
        "capability_id": "test_simulation",
        "context": {
            "horizon_steps": 3,
            "confidence_decay": 0.1,
        },
        "metadata": {
            "test": True,
        },
    }
