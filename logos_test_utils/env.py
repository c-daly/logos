"""Environment helpers for the shared LOGOS test stack."""

from __future__ import annotations

import os
from collections.abc import Mapping
from functools import cache
from pathlib import Path


def _default_env_path() -> Path:
    override = os.getenv("LOGOS_STACK_ENV")
    if override:
        return Path(override)
    repo_root = Path(__file__).resolve().parents[1]
    candidate = repo_root / "tests" / "e2e" / "stack" / "logos" / ".env.test"
    return candidate


@cache
def load_stack_env(env_path: str | Path | None = None) -> dict[str, str]:
    """Load the canonical stack environment (key/value pairs).

    Values are parsed from the generated ``.env.test`` file. Callers can
    override the location via ``env_path`` or the ``LOGOS_STACK_ENV``
    environment variable. Missing files simply yield an empty mapping so
    tests can still fall back to hard-coded defaults.
    """

    path = Path(env_path) if env_path else _default_env_path()
    env: dict[str, str] = {}
    if not path.exists():
        return env

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def get_env_value(
    key: str,
    env: Mapping[str, str] | None = None,
    default: str | None = None,
) -> str | None:
    """Resolve an env var by checking OS env, stack env, then default."""

    if key in os.environ:
        return os.environ[key]
    if env and key in env:
        return env[key]
    return default
