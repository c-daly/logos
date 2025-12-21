"""Tests for logos_test_utils config helpers."""

from __future__ import annotations

from logos_test_utils.config import (
    ServiceConfig,
    get_env_value,
    normalize_host,
    resolve_service_config,
)


def test_get_env_value_prefers_os_env(monkeypatch) -> None:
    monkeypatch.setenv("TEST_KEY", "from_env")
    result = get_env_value("TEST_KEY", {"TEST_KEY": "from_mapping"}, "default")
    assert result == "from_env"


def test_get_env_value_uses_mapping_then_default(monkeypatch) -> None:
    monkeypatch.delenv("TEST_KEY", raising=False)
    assert (
        get_env_value("TEST_KEY", {"TEST_KEY": "from_mapping"}, "default")
        == "from_mapping"
    )
    assert (
        get_env_value("MISSING_KEY", {"TEST_KEY": "from_mapping"}, "default")
        == "default"
    )


def test_normalize_host() -> None:
    assert normalize_host("0.0.0.0") == "localhost"
    assert normalize_host("127.0.0.1") == "127.0.0.1"


def test_resolve_service_config_env_priority(monkeypatch) -> None:
    defaults = ServiceConfig(host="localhost", port=8080, url="http://localhost:8080")
    monkeypatch.setenv("SERVICE_HOST", "env-host")
    monkeypatch.setenv("SERVICE_PORT", "9090")
    resolved = resolve_service_config(
        "SERVICE_HOST",
        "SERVICE_PORT",
        defaults,
        {"SERVICE_PORT": "7070"},
    )
    assert resolved.host == "env-host"
    assert resolved.port == 9090
    assert resolved.url == "http://env-host:9090"


def test_resolve_service_config_normalizes_host(monkeypatch) -> None:
    defaults = ServiceConfig(host="localhost", port=8080, url="http://localhost:8080")
    monkeypatch.delenv("SERVICE_HOST", raising=False)
    monkeypatch.delenv("SERVICE_PORT", raising=False)
    resolved = resolve_service_config(
        "SERVICE_HOST",
        "SERVICE_PORT",
        defaults,
        {"SERVICE_HOST": "0.0.0.0", "SERVICE_PORT": "5050"},
    )
    assert resolved.host == "localhost"
    assert resolved.port == 5050
    assert resolved.url == "http://localhost:5050"
