"""Docker helpers used across test suites."""

from __future__ import annotations

import json
import os
import subprocess
import time
from collections.abc import Mapping, MutableMapping
from typing import Any


def resolve_container_name(
    env_key: str,
    default: str,
    env_values: Mapping[str, str] | None = None,
) -> str:
    """Resolve a container name from env vars or fall back to a default."""

    if env_key in os.environ:
        return os.environ[env_key]
    if env_values and env_key in env_values:
        return env_values[env_key]
    return default


def is_container_running(container_name: str) -> bool:
    """Check whether the given Docker container name is currently running."""

    if not container_name:
        return False

    try:
        result = subprocess.run(
            [
                "docker",
                "ps",
                "--filter",
                f"name={container_name}",
                "--format",
                "{{.Names}}",
            ],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        names = {line.strip() for line in result.stdout.splitlines() if line.strip()}
        return container_name in names
    except Exception:
        return False


def inspect_container_state(container_name: str) -> MutableMapping[str, Any] | None:
    """Return Docker ``State`` metadata for the container, if available."""

    if not container_name:
        return None

    try:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{json .State}}", container_name],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None
        return json.loads(result.stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError):
        return None


def get_container_logs(container_name: str, tail: int = 80) -> str:
    """Return the last ``tail`` lines from ``docker logs`` for diagnostics."""

    if not container_name:
        return ""

    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", str(tail), container_name],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode != 0:
            return result.stderr.strip()
        return result.stdout.strip()
    except subprocess.SubprocessError:
        return ""


def wait_for_container_health(
    container_name: str,
    timeout: int = 90,
    poll_interval: float = 2.0,
) -> None:
    """Block until a container reports ``healthy`` or raise after ``timeout`` seconds."""

    deadline = time.monotonic() + timeout
    last_state: MutableMapping[str, Any] | None = None
    while time.monotonic() < deadline:
        state = inspect_container_state(container_name)
        last_state = state

        if not state:
            time.sleep(poll_interval)
            continue

        status = state.get("Status")
        health = (state.get("Health") or {}).get("Status")

        if health == "healthy" or (health is None and status == "running"):
            return

        if health == "unhealthy" or status in {"exited", "dead"}:
            break

        time.sleep(poll_interval)

    logs = get_container_logs(container_name)
    status_repr = (
        f"status={last_state.get('Status')} health="
        f"{(last_state.get('Health') or {}).get('Status')}"
        if last_state
        else "unknown"
    )
    raise RuntimeError(
        "Container did not become healthy within timeout: "
        f"{container_name} ({status_repr}). Recent logs:\n{logs}"
    )
