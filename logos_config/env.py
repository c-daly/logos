"""Environment helpers for LOGOS configuration.

This module provides utilities for resolving paths and loading environment
configuration, used consistently across all LOGOS repositories.

Priority for environment resolution:
1. OS environment variables
2. Provided env mapping (e.g., loaded from .env file)
3. Default value
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from functools import cache
from pathlib import Path


def get_env_value(
    key: str,
    env: Mapping[str, str] | None = None,
    default: str | None = None,
) -> str | None:
    """Resolve an env var by checking OS env, provided mapping, then default.

    Args:
        key: Environment variable name
        env: Optional mapping to check (e.g., loaded from .env file)
        default: Default value if not found

    Returns:
        The resolved value or default
    """
    if key in os.environ:
        return os.environ[key]
    if env and key in env:
        return env[key]
    return default


def get_repo_root(
    repo_name: str | None = None,
    env: Mapping[str, str] | None = None,
) -> Path:
    """Resolve a repository root directory.

    Priority:
    1. {REPO}_REPO_ROOT from OS env or provided mapping (e.g., HERMES_REPO_ROOT)
    2. GITHUB_WORKSPACE (set by GitHub Actions in CI)
    3. Walk up from $PWD to find .git directory
    4. Fall back to $PWD (works in containers where WORKDIR is set)

    Args:
        repo_name: Repository name (hermes, apollo, logos, sophia, talos).
                   If provided, checks {REPO}_REPO_ROOT env var first.
        env: Optional mapping to check for env vars

    Returns:
        Path to the repository root
    """
    # 1. Check repo-specific env var
    if repo_name:
        env_var = f"{repo_name.upper()}_REPO_ROOT"
        env_value = get_env_value(env_var, env)
        if env_value:
            candidate = Path(env_value).expanduser().resolve()
            if candidate.exists():
                return candidate

    # 2. GitHub Actions sets GITHUB_WORKSPACE to the repo checkout
    github_workspace = os.getenv("GITHUB_WORKSPACE")
    if github_workspace:
        candidate = Path(github_workspace).resolve()
        if candidate.exists():
            return candidate

    # 3. Walk up from $PWD to find .git directory
    cwd = Path.cwd().resolve()
    current = cwd
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent

    # 4. Fall back to $PWD
    return cwd


@cache
def load_env_file(env_path: str | Path | None = None) -> dict[str, str]:
    """Load environment variables from a .env file.

    This function is cached, so repeated calls with the same path return
    the same dictionary. Use load_env_file.cache_clear() to reset.

    Args:
        env_path: Path to .env file. If None, tries .env in current directory.

    Returns:
        Dictionary of environment variables. Empty dict if file doesn't exist.
    """
    if env_path is None:
        env_path = Path.cwd() / ".env"

    path = Path(env_path)
    env: dict[str, str] = {}

    if not path.exists():
        return env

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        # Strip quotes from values
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        env[key.strip()] = value

    return env
