"""Shared config helpers for LOGOS test utilities."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from logos_config import get_env_value as _get_env_value


def get_env_value(
    key: str,
    env: Mapping[str, str] | None = None,
    default: str | None = None,
) -> str | None:
    """Resolve an env var by checking OS env, provided mapping, then default."""

    return _get_env_value(key, env, default)


def normalize_host(host: str) -> str:
    """Convert 0.0.0.0 to localhost for client connections."""

    return "localhost" if host == "0.0.0.0" else host


@dataclass(frozen=True)
class ServiceConfig:
    host: str
    port: int
    url: str


def _coerce_port(value: str | int | None, fallback: int) -> int:
    if value is None:
        return fallback
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except ValueError:
        return fallback


def resolve_service_config(
    host_key: str,
    port_key: str,
    defaults: ServiceConfig,
    extra_env: Mapping[str, str] | None = None,
) -> ServiceConfig:
    """Build a service config from env with standard normalization."""

    raw_host = get_env_value(host_key, extra_env, defaults.host) or defaults.host
    raw_port = get_env_value(port_key, extra_env, str(defaults.port)) or str(defaults.port)
    host = normalize_host(raw_host)
    port = _coerce_port(raw_port, defaults.port)
    url = f"http://{host}:{port}"
    return ServiceConfig(host=host, port=port, url=url)
