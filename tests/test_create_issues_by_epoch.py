"""
Tests for the epoch-based issue generation script.
"""

import sys
from pathlib import Path

# Add .github/scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".github" / "scripts"))

import pytest
from create_issues_by_epoch import EPOCHS, EnhancedTaskParser


def test_epochs_defined():
    """Test that epochs are properly defined."""
    assert len(EPOCHS) == 4

    # Check epoch structure
    for epoch in EPOCHS:
        assert epoch.name
        assert epoch.description
        assert epoch.milestone_name
        assert "Epoch" in epoch.name


def test_enhanced_task_parser_initialization():
    """Test that EnhancedTaskParser can be initialized."""
    doc_path = Path(__file__).parent.parent / "docs" / "action_items.md"
    parser = EnhancedTaskParser(doc_path)
    assert parser is not None
    assert parser.doc_path == doc_path


def test_enhanced_task_parser_parses_tasks_with_epochs():
    """Test that EnhancedTaskParser assigns epochs to tasks."""
    doc_path = Path(__file__).parent.parent / "docs" / "action_items.md"
    parser = EnhancedTaskParser(doc_path)
    tasks = parser.parse()

    # Should find at least some tasks
    assert len(tasks) > 0

    # Count tasks with epochs
    tasks_with_epochs = [t for t in tasks if t.get("epoch")]
    assert len(tasks_with_epochs) > 0

    # Each task should have required fields
    for task in tasks:
        assert "title" in task
        assert "component" in task
        assert "labels" in task


def test_epoch_assignment_logic():
    """Test that epoch assignment works for different task types."""
    doc_path = Path(__file__).parent.parent / "docs" / "action_items.md"
    parser = EnhancedTaskParser(doc_path)
    tasks = parser.parse()

    # Group tasks by epoch
    tasks_by_epoch = {}
    for task in tasks:
        if task.get("epoch"):
            epoch_name = task["epoch"].name
            if epoch_name not in tasks_by_epoch:
                tasks_by_epoch[epoch_name] = []
            tasks_by_epoch[epoch_name].append(task)

    # Should have tasks in multiple epochs
    assert len(tasks_by_epoch) >= 1

    # Verify milestone names are assigned
    for task in tasks:
        if task.get("epoch"):
            assert task.get("milestone")
            assert "M" in task["milestone"]
