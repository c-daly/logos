#!/usr/bin/env python3
"""
Non-interactive version of issue management script.
Automatically closes all issues and creates new ones when GH_TOKEN is set.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import manage_issues functions
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from manage_issues import (
    run_gh_command,
    close_all_issues,
    create_milestones,
    load_issues_from_parser,
    create_issues
)

def main():
    """Non-interactive main execution."""
    print("=" * 70)
    print("Project LOGOS - Phase 1 Issue Management (Auto Mode)")
    print("=" * 70)
    
    # Check if gh CLI is authenticated
    success, output, error = run_gh_command(['auth', 'status'])
    if not success:
        print("\n❌ ERROR: gh CLI is not authenticated")
        print("Set GH_TOKEN environment variable:")
        print("  export GH_TOKEN=your_token_here")
        print("  python3 .github/scripts/manage_issues_auto.py")
        sys.exit(1)
    
    print(f"✅ Authenticated with GitHub\n")
    
    # Step 1: Close all existing issues
    close_all_issues()
    
    # Step 2: Create milestones
    milestone_map = create_milestones()
    
    # Step 3: Load issues from parser
    print("\n=== Loading issues from action_items.md ===")
    tasks = load_issues_from_parser()
    print(f"Loaded {len(tasks)} tasks")
    
    # Group by epoch for summary
    epoch_counts = {}
    for task in tasks:
        epoch_name = task['epoch'].name if task.get('epoch') else 'No Epoch'
        epoch_counts[epoch_name] = epoch_counts.get(epoch_name, 0) + 1
    
    print("\nTasks by Epoch:")
    for epoch_name in sorted(epoch_counts.keys()):
        count = epoch_counts[epoch_name]
        print(f"  {epoch_name}: {count} tasks")
    
    # Step 4: Create all issues
    create_issues(tasks, milestone_map)
    
    print("\n" + "=" * 70)
    print("✅ Phase 1 issue management complete!")
    print(f"✅ Visit https://github.com/c-daly/logos/issues to see the new issues")
    print("=" * 70)

if __name__ == '__main__':
    main()
