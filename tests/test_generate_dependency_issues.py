"""Tests for generate_dependency_issues.py script."""

import json

# Add parent directory to path to import the script
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / ".github" / "scripts"))

from generate_dependency_issues import (
    REPOSITORIES,
    format_as_gh_cli,
    format_as_json,
    format_as_markdown,
    generate_dependency_issues,
)


def test_generate_dependency_issues():
    """Test that issues are generated for all repositories."""
    issues = generate_dependency_issues()

    # Should have one issue per repository
    assert len(issues) == len(REPOSITORIES)

    # Check that all repositories are covered
    repos = [issue["repository"] for issue in issues]
    assert "c-daly/sophia" in repos
    assert "c-daly/hermes" in repos
    assert "c-daly/talos" in repos
    assert "c-daly/apollo" in repos


def test_issue_structure():
    """Test that each issue has the required fields."""
    issues = generate_dependency_issues()

    for issue in issues:
        assert "repository" in issue
        assert "title" in issue
        assert "body" in issue
        assert "labels" in issue
        assert "milestone" in issue
        assert "component" in issue

        # Check that title mentions dependency management
        assert "dependency" in issue["title"].lower()

        # Check that labels is a list
        assert isinstance(issue["labels"], list)
        assert len(issue["labels"]) > 0


def test_python_repos_content():
    """Test that Python repositories have correct dependency manager."""
    issues = generate_dependency_issues()

    python_repos = ["c-daly/sophia", "c-daly/hermes", "c-daly/talos"]

    for issue in issues:
        if issue["repository"] in python_repos:
            assert "Poetry or pipenv" in issue["title"]
            assert "Poetry" in issue["body"]
            assert "pipenv" in issue["body"]
            assert "pyproject.toml" in issue["body"] or "Pipfile" in issue["body"]
            assert "Python" in issue["body"] or "pytest" in issue["body"]


def test_javascript_repo_content():
    """Test that JavaScript repository has correct dependency manager."""
    issues = generate_dependency_issues()

    apollo_issue = next(i for i in issues if i["repository"] == "c-daly/apollo")

    assert "npm or yarn" in apollo_issue["title"]
    assert "npm" in apollo_issue["body"]
    assert "yarn" in apollo_issue["body"]
    assert "package.json" in apollo_issue["body"]
    assert "Node.js" in apollo_issue["body"] or "JavaScript" in apollo_issue["body"]


def test_format_as_json():
    """Test JSON formatting."""
    issues = generate_dependency_issues()
    json_output = format_as_json(issues)

    # Should be valid JSON
    parsed = json.loads(json_output)
    assert len(parsed) == len(REPOSITORIES)

    # Check first issue structure
    assert "repository" in parsed[0]
    assert "title" in parsed[0]
    assert "body" in parsed[0]


def test_format_as_markdown():
    """Test markdown formatting."""
    issues = generate_dependency_issues()
    md_output = format_as_markdown(issues)

    # Should contain all repository names
    assert "c-daly/sophia" in md_output
    assert "c-daly/hermes" in md_output
    assert "c-daly/talos" in md_output
    assert "c-daly/apollo" in md_output

    # Should have markdown headers
    assert "##" in md_output
    assert "###" in md_output

    # Should contain labels and milestone info
    assert "**Labels:**" in md_output
    assert "**Milestone:**" in md_output


def test_format_as_gh_cli():
    """Test GitHub CLI command formatting."""
    issues = generate_dependency_issues()
    cli_output = format_as_gh_cli(issues)

    # Should start with shebang
    assert cli_output.startswith("#!/bin/bash")

    # Should have gh issue create commands
    assert "gh issue create" in cli_output

    # Should reference all repositories
    assert "--repo c-daly/sophia" in cli_output
    assert "--repo c-daly/hermes" in cli_output
    assert "--repo c-daly/talos" in cli_output
    assert "--repo c-daly/apollo" in cli_output

    # Should include labels (even if commented)
    assert "--label" in cli_output

    # Should have success message
    assert "successfully" in cli_output.lower()

    # Should properly escape backticks
    assert "\\`" in cli_output

    # Should have warning about labels
    assert "IMPORTANT" in cli_output or "labels" in cli_output

    # Should have both commented and uncommented commands
    assert "# Without labels" in cli_output
    assert "# With labels" in cli_output


def test_labels_consistency():
    """Test that all issues have consistent label structure."""
    issues = generate_dependency_issues()

    for issue in issues:
        labels = issue["labels"]

        # All should have phase:1
        assert "phase:1" in labels

        # All should have type:infrastructure
        assert "type:infrastructure" in labels

        # All should have priority:high
        assert "priority:high" in labels

        # Each should have a component label matching the repo
        component = issue["component"]
        assert f"component:{component}" in labels


def test_milestone_consistency():
    """Test that all issues have the same milestone."""
    issues = generate_dependency_issues()

    expected_milestone = "M1: HCG Store & Retrieve"

    for issue in issues:
        assert issue["milestone"] == expected_milestone


def test_acceptance_criteria_present():
    """Test that all issues have acceptance criteria."""
    issues = generate_dependency_issues()

    for issue in issues:
        body = issue["body"]

        # Should have Acceptance Criteria section
        assert "Acceptance Criteria" in body

        # Should have checkboxes
        assert "- [ ]" in body

        # Should mention documentation
        assert "document" in body.lower() or "README" in body

        # Should mention lock files
        assert "lock" in body.lower()


def test_references_included():
    """Test that all issues include relevant references."""
    issues = generate_dependency_issues()

    for issue in issues:
        body = issue["body"]

        # Should reference specification
        assert "spec/project_logos_full.md" in body or "specification" in body.lower()

        # Should reference action items
        assert "action_items.md" in body

        # Should reference logos foundry repo
        assert "github.com/c-daly/logos" in body
