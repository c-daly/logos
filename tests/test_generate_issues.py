"""
Tests for the issue generation scripts.
"""

from pathlib import Path

from logos_tools.generate_issues import TaskParser


def test_task_parser_initialization():
    """Test that TaskParser can be initialized."""
    # action_items.md has been moved to docs/old/ (archived)
    doc_path = Path(__file__).parent.parent / "docs" / "old" / "action_items.md"
    parser = TaskParser(doc_path)
    assert parser is not None
    assert parser.doc_path == doc_path


def test_task_parser_parses_tasks():
    """Test that TaskParser can parse tasks from action_items.md (archived)."""
    # action_items.md has been moved to docs/old/ (archived)
    doc_path = Path(__file__).parent.parent / "docs" / "old" / "action_items.md"
    parser = TaskParser(doc_path)
    tasks = parser.parse()

    # Should find at least some tasks
    assert len(tasks) > 0

    # Each task should have required fields
    for task in tasks:
        assert "title" in task
        assert "section" in task
        assert "component" in task
        assert "labels" in task


def test_task_parser_identifies_components():
    """Test that TaskParser correctly identifies components."""
    # action_items.md has been moved to docs/old/ (archived)
    doc_path = Path(__file__).parent.parent / "docs" / "old" / "action_items.md"
    parser = TaskParser(doc_path)
    tasks = parser.parse()

    # Find tasks with different components
    components = {task['component'] for task in tasks}

    # Should have various components
    assert len(components) > 0
    # Common components that should appear
    expected_components = {"infrastructure", "sophia", "hermes", "talos", "apollo"}
    assert components.intersection(expected_components)
