"""Test configuration for logos-hcg."""

import pytest


@pytest.fixture
def sample_entity_data() -> dict:
    """Sample entity data for tests."""
    return {
        "id": "entity_test_123",
        "type": "manipulator",
        "properties": {
            "name": "test_gripper",
            "status": "ready",
        },
    }


@pytest.fixture
def sample_edge_data() -> dict:
    """Sample edge data for tests."""
    return {
        "id": "edge_test_123",
        "source": "entity_a",
        "target": "entity_b",
        "relation": "HAS_STATE",
        "properties": {},
    }
