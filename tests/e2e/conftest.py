"""
pytest configuration for Phase 2 E2E tests.

Configures:
- Test markers
- Logging
- Pytest options
- Plugin configuration
"""

import os

import pytest

DEFAULT_SOPHIA_PORT = os.getenv("SOPHIA_PORT", "8001")
DEFAULT_HERMES_PORT = os.getenv("HERMES_PORT", "8002")
DEFAULT_APOLLO_PORT = os.getenv("APOLLO_PORT", "8003")

DEFAULT_SOPHIA_URL = os.getenv("SOPHIA_URL", f"http://localhost:{DEFAULT_SOPHIA_PORT}")
DEFAULT_HERMES_URL = os.getenv("HERMES_URL", f"http://localhost:{DEFAULT_HERMES_PORT}")
DEFAULT_APOLLO_URL = os.getenv("APOLLO_URL", f"http://localhost:{DEFAULT_APOLLO_PORT}")


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    )
    config.addinivalue_line(
        "markers",
        "requires_services: marks tests that require all services running",
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests",
    )
    config.addinivalue_line(
        "markers",
        "e2e: marks tests as end-to-end tests",
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add e2e marker to all tests in this directory
        if "phase2" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
            item.add_marker(pytest.mark.integration)


# ============================================================================
# Pytest Options
# ============================================================================


def pytest_addoption(parser):
    """Add custom command-line options."""
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests",
    )
    parser.addoption(
        "--sophia-url",
        action="store",
        default=DEFAULT_SOPHIA_URL,
        help="Sophia service URL",
    )
    parser.addoption(
        "--hermes-url",
        action="store",
        default=DEFAULT_HERMES_URL,
        help="Hermes service URL",
    )
    parser.addoption(
        "--apollo-url",
        action="store",
        default=DEFAULT_APOLLO_URL,
        help="Apollo service URL",
    )


def pytest_runtest_setup(item):
    """Skip slow tests unless --run-slow is given."""
    if "slow" in item.keywords and not item.config.getoption("--run-slow"):
        pytest.skip("need --run-slow option to run")
