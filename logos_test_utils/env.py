"""Environment helpers for the shared LOGOS test stack."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

from logos_config.env import get_repo_root as resolve_repo_root
from logos_config.env import load_env_file


def _default_env_path() -> Path:
    override = os.getenv("LOGOS_STACK_ENV")
    if override:
        return Path(override)
    repo_root = Path(__file__).resolve().parents[1]
    candidate = repo_root / "tests" / "e2e" / "stack" / "logos" / ".env.test"
    return candidate


def load_stack_env(env_path: str | Path | None = None) -> dict[str, str]:
    """Load the canonical stack environment (key/value pairs).

    Values are parsed from the generated ``.env.test`` file. Callers can
    override the location via ``env_path`` or the ``LOGOS_STACK_ENV``
    environment variable. Missing files simply yield an empty mapping so
    tests can still fall back to hard-coded defaults.
    """

    path = Path(env_path) if env_path else _default_env_path()
    return load_env_file(path)


def get_repo_root(env: Mapping[str, str] | None = None) -> Path:
    """Resolve the LOGOS repo root, honoring LOGOS_REPO_ROOT if set.

    Priority:
    1. LOGOS_REPO_ROOT from OS env or provided mapping (if path exists).
    2. GITHUB_WORKSPACE (set by GitHub Actions in CI).
    3. Fallback to parent of this package (works when running from source).
    """
    return resolve_repo_root("logos", env)
