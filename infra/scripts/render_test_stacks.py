"""Render self-contained docker-compose.test.yml files for every LOGOS repo.

This script reads the canonical test-stack template defined under
`infra/test_stack/` and emits staged outputs for each repo into
`tests/e2e/stack/<repo>/`.

Future automation can copy those outputs into the downstream repos or
compare them against committed files to detect drift.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Iterable, Mapping
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
TEST_STACK_DIR = ROOT / "infra" / "test_stack"
SERVICES_FILE = TEST_STACK_DIR / "services.yaml"
REPOS_FILE = TEST_STACK_DIR / "repos.yaml"
OVERLAYS_DIR = TEST_STACK_DIR / "overlays"
DEFAULT_OUTPUT_ROOT = ROOT / "tests" / "e2e" / "stack"


class RenderError(RuntimeError):
    """Raised when configuration or template issues block rendering."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render repo-specific docker-compose.test.yml files from the shared template.",
    )
    parser.add_argument(
        "--repo",
        action="append",
        dest="repos",
        help="Render only the specified repo (may supply multiple). Default renders all repos.",
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Where to stage generated files (default: tests/e2e/stack).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write files; instead verify existing outputs match the template.",
    )
    return parser.parse_args()


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RenderError(f"Expected file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise RenderError(f"YAML root in {path} must be a mapping")
    return data


def deep_format(value: Any, context: Mapping[str, Any]) -> Any:
    if isinstance(value, str):
        try:
            return value.format(**context)
        except KeyError as exc:  # pragma: no cover - configuration error path
            missing = exc.args[0]
            raise RenderError(f"Missing template variable '{missing}' in context") from exc
    if isinstance(value, list):
        return [deep_format(item, context) for item in value]
    if isinstance(value, dict):
        formatted: dict[Any, Any] = {}
        for key, item in value.items():
            if isinstance(key, str):
                try:
                    formatted_key = key.format(**context)
                except KeyError as exc:  # pragma: no cover - configuration error path
                    missing = exc.args[0]
                    raise RenderError(f"Missing template variable '{missing}' in context") from exc
            else:
                formatted_key = key
            formatted[formatted_key] = deep_format(item, context)
        return formatted
    return value


def deep_merge(target: dict[str, Any], addition: dict[str, Any]) -> dict[str, Any]:
    for key, value in addition.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            deep_merge(target[key], value)
        else:
            target[key] = value
    return target


def normalize_context(
    raw_defaults: Mapping[str, Any], overrides: Mapping[str, Any]
) -> dict[str, Any]:
    context = {str(key): str(value) for key, value in raw_defaults.items()}
    for key, value in overrides.items():
        context[str(key)] = str(value)
    return context


def resolve_repo_configs(
    config: dict[str, Any], selected: Iterable[str] | None
) -> dict[str, dict[str, Any]]:
    defaults = config.get("defaults", {})
    default_context = defaults.get("context", {})
    default_env = defaults.get("env", {})
    repos = config.get("repos", {})
    if not repos:
        raise RenderError("No repos defined in repos.yaml")

    if selected:
        missing = [name for name in selected if name not in repos]
        if missing:
            raise RenderError(f"Unknown repos requested: {', '.join(missing)}")
        repo_names = list(dict.fromkeys(selected))
    else:
        repo_names = list(repos.keys())

    resolved: dict[str, dict[str, Any]] = {}
    for name in repo_names:
        repo_entry = repos[name] or {}
        repo_context_overrides = repo_entry.get("context", {})
        context = normalize_context(
            default_context,
            {
                **repo_context_overrides,
                **{
                    "service_prefix": repo_entry.get(
                        "service_prefix", default_context.get("service_prefix", name)
                    ),
                    "volume_prefix": repo_entry.get(
                        "volume_prefix", default_context.get("volume_prefix", name)
                    ),
                    "network_name": repo_entry.get(
                        "network_name",
                        default_context.get("network_name", f"{name}-test-network"),
                    ),
                },
            },
        )

        resolved[name] = {
            "path": Path(repo_entry.get("path", defaults.get("path", "."))),
            "compose_filename": repo_entry.get(
                "compose_filename",
                defaults.get("compose_filename", "docker-compose.test.yml"),
            ),
            "env_filename": repo_entry.get(
                "env_filename", defaults.get("env_filename", ".env.test")
            ),
            "services": repo_entry.get("services", []),
            "overlays": repo_entry.get("overlays", []),
            "context": context,
            "env": {
                **default_env,
                **(repo_entry.get("env", {}) or {}),
            },
        }
        if not resolved[name]["services"]:
            raise RenderError(f"Repo '{name}' must declare at least one service in repos.yaml")
    return resolved


def load_overlay(name: str, context: Mapping[str, Any]) -> dict[str, Any]:
    overlay_path = OVERLAYS_DIR / name
    overlay_data = load_yaml(overlay_path)
    formatted = deep_format(overlay_data, context)
    if not isinstance(formatted, dict):
        raise RenderError(f"Overlay '{name}' must produce a mapping")
    return formatted


def build_compose_doc(
    template: dict[str, Any],
    context: Mapping[str, Any],
    services: list[str],
    overlays: list[str],
) -> dict[str, Any]:
    formatted = deep_format(deepcopy(template), context)
    template_services = formatted.get("services", {})
    missing = [svc for svc in services if svc not in template_services]
    if missing:
        raise RenderError(f"Template missing services: {', '.join(missing)}")

    compose_doc: dict[str, Any] = {
        key: value for key, value in formatted.items() if key in {"version", "networks", "volumes"}
    }
    compose_doc["services"] = {svc: template_services[svc] for svc in services}

    for overlay_name in overlays:
        overlay_doc = load_overlay(overlay_name, context)
        for section in ("services", "volumes", "networks"):
            if section in overlay_doc:
                compose_doc.setdefault(section, {})
                deep_merge(compose_doc[section], overlay_doc[section])

    return compose_doc


def render_env(env_map: Mapping[str, Any], context: Mapping[str, Any]) -> str:
    rendered = {
        key: str(value).format(**context) for key, value in env_map.items() if value is not None
    }
    lines = [f"{key}={value}" for key, value in sorted(rendered.items()) if value]
    return "\n".join(lines) + ("\n" if lines else "")


def compute_stack_version(repo_name: str, compose_doc: dict[str, Any], env_content: str) -> str:
    payload = {
        "repo": repo_name,
        "compose": compose_doc,
        "env": env_content,
        "services_file": SERVICES_FILE.read_text(encoding="utf-8"),
        "repos_file": REPOS_FILE.read_text(encoding="utf-8"),
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()
    return digest[:12]


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def files_match(path: Path, content: str) -> bool:
    return path.exists() and path.read_text(encoding="utf-8") == content


def render_repo(
    repo_name: str,
    repo_cfg: Mapping[str, Any],
    template: dict[str, Any],
    output_root: Path,
    check_only: bool,
) -> bool:
    context = repo_cfg["context"]
    compose_doc = build_compose_doc(
        template=template,
        context=context,
        services=repo_cfg["services"],
        overlays=repo_cfg["overlays"],
    )
    compose_yaml = yaml.safe_dump(compose_doc, sort_keys=False)
    env_content = render_env(repo_cfg["env"], context)
    stack_version = compute_stack_version(repo_name, compose_doc, env_content)

    repo_output_dir = output_root / repo_name
    compose_path = repo_output_dir / repo_cfg["compose_filename"]
    env_path = repo_output_dir / repo_cfg["env_filename"]
    version_path = repo_output_dir / "STACK_VERSION"

    compose_matches = files_match(compose_path, compose_yaml)
    env_matches = files_match(env_path, env_content)
    version_matches = files_match(version_path, stack_version + "\n")

    if check_only:
        return compose_matches and env_matches and version_matches

    write_file(compose_path, compose_yaml)
    write_file(env_path, env_content)
    write_file(version_path, stack_version + "\n")
    return True


def main() -> int:
    args = parse_args()
    template = load_yaml(SERVICES_FILE)
    repo_config_data = load_yaml(REPOS_FILE)
    resolved_repos = resolve_repo_configs(repo_config_data, args.repos)
    output_root = Path(args.output_root).resolve()

    all_ok = True
    for repo_name, repo_cfg in resolved_repos.items():
        try:
            ok = render_repo(repo_name, repo_cfg, template, output_root, args.check)
        except RenderError as exc:
            print(f"[error] {repo_name}: {exc}", file=sys.stderr)
            return 1
        status = "ok" if ok else "stale"
        prefix = "CHECK" if args.check else "WRITE"
        print(f"[{prefix}] {repo_name}: {status}")
        all_ok = all_ok and ok

    if args.check and not all_ok:
        print("At least one repo has stale generated files.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
