#!/usr/bin/env python3
"""
Generate dependency management issues for each LOGOS component repository.

This script creates GitHub issues for dependency management tasks in each of the
LOGOS ecosystem repositories: sophia, hermes, talos, and apollo.

Usage:
    python3 .github/scripts/generate_dependency_issues.py [--format json|markdown|gh-cli]
"""

import argparse
import json
from typing import Any

# Repository configurations with their dependency management details
REPOSITORIES = [
    {
        "name": "sophia",
        "full_name": "c-daly/sophia",
        "language": "Python",
        "description": "Sophia: non-linguistic cognitive core (Orchestrator, CWM-A, CWM-G, Planner, Executor)",
        "dependency_manager": "Poetry or pipenv",
        "labels": ["component:sophia", "priority:high", "type:infrastructure", "phase:1"],
        "milestone": "M1: HCG Store & Retrieve",
    },
    {
        "name": "hermes",
        "full_name": "c-daly/hermes",
        "language": "Python",
        "description": "Hermes: stateless language & embedding utility (stt, tts, simple_nlp, embed_text)",
        "dependency_manager": "Poetry or pipenv",
        "labels": ["component:hermes", "priority:high", "type:infrastructure", "phase:1"],
        "milestone": "M1: HCG Store & Retrieve",
    },
    {
        "name": "talos",
        "full_name": "c-daly/talos",
        "language": "Python",
        "description": "Talos: hardware abstraction layer (sensors/actuators, simulated interfaces)",
        "dependency_manager": "Poetry or pipenv",
        "labels": ["component:talos", "priority:high", "type:infrastructure", "phase:1"],
        "milestone": "M1: HCG Store & Retrieve",
    },
    {
        "name": "apollo",
        "full_name": "c-daly/apollo",
        "language": "JavaScript/TypeScript",
        "description": "Apollo: thin client UI & command layer",
        "dependency_manager": "npm or yarn",
        "labels": ["component:apollo", "priority:high", "type:infrastructure", "phase:1"],
        "milestone": "M1: HCG Store & Retrieve",
    },
]


def generate_dependency_issues() -> list[dict[str, Any]]:
    """Generate dependency management issues for all repositories."""
    issues = []

    for repo in REPOSITORIES:
        issue = {
            "repository": repo["full_name"],
            "title": f"Set up dependency management ({repo['dependency_manager']})",
            "body": _generate_issue_body(repo),
            "labels": repo["labels"],
            "milestone": repo["milestone"],
            "component": repo["name"],
        }
        issues.append(issue)

    return issues


def _generate_issue_body(repo: dict[str, str]) -> str:
    """Generate the issue body for a dependency management task."""
    body_parts = [
        f"## Set up Dependency Management for {repo['name'].capitalize()}",
        "",
        "### Description",
        f"Configure dependency management for the **{repo['name']}** repository using {repo['dependency_manager']}.",
        "",
        f"**Component:** {repo['description']}",
        "",
        "### Requirements",
    ]

    if repo["language"] == "Python":
        body_parts.extend(
            [
                "",
                "Choose and configure either **Poetry** or **pipenv** for Python dependency management:",
                "",
                "#### Option 1: Poetry (Recommended)",
                "- [ ] Initialize Poetry project: `poetry init`",
                "- [ ] Create `pyproject.toml` with project metadata",
                "- [ ] Define core dependencies (e.g., `neo4j`, `rdflib` if needed)",
                "- [ ] Define development dependencies (e.g., `pytest`, `pytest-cov`, `ruff`, `mypy`)",
                "- [ ] Add `poetry.lock` to ensure reproducible builds",
                "- [ ] Document Poetry usage in `README.md`",
                "",
                "#### Option 2: Pipenv",
                "- [ ] Initialize Pipenv: `pipenv --python 3.11`",
                "- [ ] Create `Pipfile` with dependencies",
                "- [ ] Create `Pipfile.lock` for version locking",
                "- [ ] Document Pipenv usage in `README.md`",
                "",
                "### Common Requirements (Both Options)",
                "- [ ] Set Python version requirement (>=3.11)",
                "- [ ] Configure virtual environment isolation",
                "- [ ] Add installation instructions to documentation",
                "- [ ] Set up pre-commit hooks (optional but recommended)",
                "- [ ] Ensure `.gitignore` excludes virtual environments and cache files",
            ]
        )
    else:  # JavaScript/TypeScript
        body_parts.extend(
            [
                "",
                "Choose and configure either **npm** or **yarn** for JavaScript/TypeScript dependency management:",
                "",
                "#### Option 1: npm",
                "- [ ] Initialize npm project: `npm init`",
                "- [ ] Create or update `package.json` with project metadata",
                "- [ ] Define dependencies (e.g., `react`, `react-dom`)",
                "- [ ] Define devDependencies (e.g., `typescript`, `eslint`, `prettier`, `jest`)",
                "- [ ] Use `package-lock.json` for version locking",
                "- [ ] Document npm usage in `README.md`",
                "",
                "#### Option 2: yarn",
                "- [ ] Initialize yarn project: `yarn init`",
                "- [ ] Create `package.json` with project metadata",
                "- [ ] Define dependencies and devDependencies",
                "- [ ] Use `yarn.lock` for version locking",
                "- [ ] Document yarn usage in `README.md`",
                "",
                "### Common Requirements (Both Options)",
                "- [ ] Set Node.js version requirement (>=18.x recommended)",
                "- [ ] Configure scripts for common tasks (`build`, `test`, `lint`, `dev`)",
                "- [ ] Add installation instructions to documentation",
                "- [ ] Set up pre-commit hooks with Husky (optional but recommended)",
                "- [ ] Ensure `.gitignore` excludes `node_modules` and build artifacts",
            ]
        )

    body_parts.extend(
        [
            "",
            "### Acceptance Criteria",
            "- [ ] Dependency manager is configured and documented",
            "- [ ] Dependencies can be installed with a single command",
            "- [ ] Lock file exists for reproducible builds",
            "- [ ] Documentation includes setup instructions",
            "- [ ] CI/CD configuration uses the chosen dependency manager",
            "",
            "### References",
            "- Project LOGOS specification: `docs/spec/project_logos_full.md`",
            "- Action items: `docs/action_items.md` (Section 1.1)",
            "- LOGOS foundry repository: https://github.com/c-daly/logos",
        ]
    )

    return "\n".join(body_parts)


def format_as_json(issues: list[dict[str, Any]]) -> str:
    """Format issues as JSON."""
    return json.dumps(issues, indent=2)


def format_as_markdown(issues: list[dict[str, Any]]) -> str:
    """Format issues as markdown."""
    output = []
    output.append("# Dependency Management Issues for LOGOS Components\n\n")

    for issue in issues:
        output.append(f"## {issue['repository']}: {issue['title']}\n\n")
        output.append(f"**Labels:** {', '.join(issue['labels'])}\n")
        output.append(f"**Milestone:** {issue['milestone']}\n\n")
        output.append(issue["body"])
        output.append("\n\n---\n\n")

    return "".join(output)


def format_as_gh_cli(issues: list[dict[str, Any]]) -> str:
    """Format issues as GitHub CLI commands."""
    commands = []

    commands.append("#!/bin/bash\n")
    commands.append("# GitHub CLI commands to create dependency management issues\n")
    commands.append("# for LOGOS component repositories\n")
    commands.append("# Make sure you have gh CLI installed and authenticated\n")
    commands.append("# Usage: bash create_dependency_issues.sh\n\n")
    commands.append("set -e  # Exit on error\n\n")

    for issue in issues:
        repo = issue["repository"]
        title = issue["title"].replace('"', '\\"')
        body = issue["body"].replace('"', '\\"').replace("\n", "\\n")
        labels = ",".join(issue["labels"])
        milestone = issue["milestone"].replace('"', '\\"')

        commands.append(f"echo 'Creating issue in {repo}...'\n")
        cmd = f'gh issue create --repo {repo} --title "{title}" --body "{body}" --label "{labels}"'

        # Note: Only add milestone if it exists in the target repo
        # The milestone may need to be created first
        commands.append(
            f'# Note: Ensure milestone "{milestone}" exists in {repo} before uncommenting\n'
        )
        commands.append(f'# {cmd} --milestone "{milestone}"\n')
        commands.append(f"{cmd}\n\n")

    commands.append("echo 'All dependency management issues created successfully!'\n")

    return "".join(commands)


def main():
    parser = argparse.ArgumentParser(
        description="Generate dependency management issues for LOGOS component repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown", "gh-cli"],
        default="gh-cli",
        help="Output format (default: gh-cli)",
    )
    parser.add_argument("--output", type=str, help="Output file (default: stdout)")

    args = parser.parse_args()

    # Generate issues
    issues = generate_dependency_issues()

    print(f"Generated {len(issues)} dependency management issues", file=__import__("sys").stderr)

    # Format output
    if args.format == "json":
        output = format_as_json(issues)
    elif args.format == "markdown":
        output = format_as_markdown(issues)
    elif args.format == "gh-cli":
        output = format_as_gh_cli(issues)

    # Write output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Output written to {args.output}", file=__import__("sys").stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
