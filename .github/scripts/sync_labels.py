#!/usr/bin/env python3
"""Sync GitHub labels from .github/labels.yml without extra tooling."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

LABEL_PATTERN = re.compile(r'-\s+name:\s+"(?P<name>[^"]+)"')


def parse_labels_file(path: Path) -> list[dict[str, str]]:
    labels: list[dict[str, str]] = []
    current: dict[str, str] = {}

    with path.open("r", encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("- name:"):
                if current:
                    labels.append(current)
                    current = {}
                current["name"] = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("color:"):
                current["color"] = line.split(":", 1)[1].strip().strip('"').lstrip("#")
            elif line.startswith("description:"):
                current["description"] = line.split(":", 1)[1].strip().strip('"')

        if current:
            labels.append(current)

    return labels


def gh_json(args: list[str]) -> list[dict]:
    completed = subprocess.run(
        ["gh"] + args,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout or "[]")


def sync_labels(repo: str, labels: list[dict[str, str]]) -> None:
    existing = {
        label["name"]: label for label in gh_json(["api", f"repos/{repo}/labels?per_page=100"])
    }

    for label in labels:
        name = label["name"]
        color = label.get("color", "")
        description = label.get("description", "")

        if name in existing:
            subprocess.run(
                [
                    "gh",
                    "label",
                    "edit",
                    name,
                    "--repo",
                    repo,
                    "--color",
                    color,
                    "--description",
                    description,
                ],
                check=True,
            )
        else:
            subprocess.run(
                [
                    "gh",
                    "label",
                    "create",
                    name,
                    "--repo",
                    repo,
                    "--color",
                    color,
                    "--description",
                    description,
                ],
                check=True,
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync GitHub labels from YAML file.")
    parser.add_argument("--repo", required=True, help="Repository (e.g., c-daly/logos)")
    parser.add_argument(
        "--file",
        default=".github/labels.yml",
        help="Path to labels YAML file",
    )
    args = parser.parse_args()

    labels_file = Path(args.file)
    if not labels_file.exists():
        raise FileNotFoundError(f"Labels file not found: {labels_file}")

    labels = parse_labels_file(labels_file)
    sync_labels(args.repo, labels)


if __name__ == "__main__":
    main()
