#!/usr/bin/env python3
"""
Manage Phase 1 issues for Project LOGOS.

This script:
1. Closes all existing issues in the repository
2. Creates 4 milestones (M1, M2, M3, M4)
3. Creates all 65 Phase 1 issues with proper descriptions, labels, and milestone assignments

Uses GitHub REST API directly - NO WORKFLOWS.
"""

import os
import sys
import json
import subprocess
from typing import List, Dict, Any
from pathlib import Path

# GitHub configuration
REPO_OWNER = "c-daly"
REPO_NAME = "logos"

def run_gh_command(args: List[str]) -> tuple:
    """Run gh CLI command and return (success, output)."""
    try:
        result = subprocess.run(
            ['gh'] + args,
            capture_output=True,
            text=True,
            check=False
        )
        return (result.returncode == 0, result.stdout, result.stderr)
    except Exception as e:
        return (False, "", str(e))

def close_all_issues():
    """Close all open issues in the repository."""
    print("\n=== Closing existing issues ===")
    
    # Get all open issues
    success, output, error = run_gh_command([
        'issue', 'list',
        '--repo', f'{REPO_OWNER}/{REPO_NAME}',
        '--state', 'open',
        '--limit', '1000',
        '--json', 'number,title'
    ])
    
    if not success:
        print(f"Error listing issues: {error}")
        return
    
    issues = json.loads(output) if output else []
    print(f"Found {len(issues)} open issues")
    
    for issue in issues:
        issue_number = issue['number']
        print(f"Closing issue #{issue_number}: {issue['title']}")
        success, _, error = run_gh_command([
            'issue', 'close',
            str(issue_number),
            '--repo', f'{REPO_OWNER}/{REPO_NAME}',
            '--comment', 'Closed to make way for reorganized Phase 1 issues.'
        ])
        if not success:
            print(f"  ❌ Error closing issue: {error}")
        else:
            print(f"  ✅ Closed")
    
    print(f"✅ Closed {len(issues)} issues")

def create_milestones() -> Dict[str, str]:
    """Create Phase 1 milestones and return mapping of title to title (for gh cli)."""
    print("\n=== Creating milestones ===")
    
    milestones = [
        {
            "title": "M1: HCG Store & Retrieve",
            "description": "Knowledge graph operational. Neo4j + Milvus working, core ontology loaded, basic CRUD operations functional."
        },
        {
            "title": "M2: SHACL Validation",
            "description": "Validation and language services operational. SHACL validation working, Hermes endpoints functional, embeddings integrated."
        },
        {
            "title": "M3: Simple Planning",
            "description": "Cognitive capabilities demonstrated. Sophia can generate valid plans using causal reasoning over the knowledge graph."
        },
        {
            "title": "M4: Pick and Place",
            "description": "End-to-end autonomous behavior. Full pipeline working from user command to execution with knowledge graph updates."
        }
    ]
    
    milestone_map = {}
    
    for milestone_data in milestones:
        title = milestone_data['title']
        description = milestone_data['description']
        
        print(f"Creating milestone: {title}")
        
        # Use gh api to create milestone
        success, output, error = run_gh_command([
            'api',
            f'/repos/{REPO_OWNER}/{REPO_NAME}/milestones',
            '-X', 'POST',
            '-f', f'title={title}',
            '-f', f'description={description}'
        ])
        
        if success:
            milestone_map[title] = title
            print(f"  ✅ Created milestone: {title}")
        else:
            # Milestone might already exist
            if 'already_exists' in error.lower() or 'already exists' in error.lower():
                milestone_map[title] = title
                print(f"  ℹ️ Milestone already exists: {title}")
            else:
                print(f"  ⚠️ Error creating milestone: {error}")
                milestone_map[title] = title  # Try to use it anyway
    
    return milestone_map

def load_issues_from_parser() -> List[Dict[str, Any]]:
    """Load issues from the existing parser script."""
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    
    from create_issues_by_epoch import EnhancedTaskParser
    
    doc_path = script_dir.parent.parent / 'docs' / 'action_items.md'
    parser = EnhancedTaskParser(doc_path)
    tasks = parser.parse()
    
    return tasks

def enhance_issue_description(task: Dict[str, Any]) -> str:
    """Create enhanced description for issue."""
    parts = []
    
    # Add reference if available
    if task.get('reference'):
        parts.append(f"**Reference:** {task['reference']}")
    
    # Add workstream if available
    if task.get('workstream'):
        parts.append(f"**Workstream:** {task['workstream']}")
    
    # Add epoch information
    if task.get('epoch'):
        parts.append(f"**Epoch:** {task['epoch']['name']}")
        parts.append(f"**Description:** {task['epoch']['description']}")
    
    # Add component
    if task.get('component'):
        parts.append(f"**Component:** {task['component']}")
    
    # Add acceptance criteria if available
    if task.get('sub_tasks'):
        parts.append("\n## Acceptance Criteria\n")
        for sub_task in task['sub_tasks']:
            parts.append(f"- [ ] {sub_task}")
    
    # Add context based on task ID
    task_id = task.get('id', '')
    if task_id:
        context = get_task_context(task_id)
        if context:
            parts.append(f"\n## Context\n\n{context}")
    
    return "\n\n".join(parts)

def get_task_context(task_id: str) -> str:
    """Get additional context for specific task types."""
    prefix = task_id[0] if task_id else ''
    
    contexts = {
        'A': 'This is an **HCG Foundation** task (Workstream A). Focus on building the foundational knowledge graph infrastructure, including Neo4j, Milvus, ontology, SHACL validation, and query utilities.',
        'B': 'This is a **Sophia Cognitive Core** task (Workstream B). Focus on implementing the cognitive architecture components: Orchestrator, CWM-A, CWM-G, Planner, and Executor.',
        'C': 'This is a **Support Services** task (Workstream C). Focus on implementing support services like Hermes (language utilities), Talos (hardware abstraction), and Apollo (UI/client).',
        'M': 'This is a **Milestone verification** task. Ensure all acceptance criteria are met and demonstrate the milestone functionality end-to-end.',
        'R': 'This is a **Research** task. Investigate, survey, and document findings. Produce a written report or documentation with recommendations.',
        'D': 'This is a **Documentation** task. Create clear, comprehensive documentation for developers and users following project documentation standards.',
        'O': 'This is an **Outreach** task. Create materials for community engagement, open-source preparation, and research community interaction.'
    }
    
    return contexts.get(prefix, '')

def create_issues(tasks: List[Dict[str, Any]], milestone_map: Dict[str, str]):
    """Create all Phase 1 issues."""
    print(f"\n=== Creating {len(tasks)} issues ===")
    
    created_count = 0
    failed_count = 0
    
    for i, task in enumerate(tasks, 1):
        task_id = task.get('id', '')
        title_prefix = f"[{task_id}] " if task_id else ""
        title = f"{title_prefix}{task['title']}"
        
        # Build body with enhanced description
        body = enhance_issue_description(task)
        
        # Prepare labels
        labels = task.get('labels', [])
        label_args = []
        for label in labels:
            label_args.extend(['-l', label])
        
        # Prepare milestone
        milestone_title = task.get('milestone')
        milestone_args = []
        if milestone_title and milestone_title in milestone_map:
            milestone_args = ['-m', milestone_title]
        
        print(f"[{i}/{len(tasks)}] Creating: {title}")
        
        # Create issue using gh CLI
        cmd_args = [
            'issue', 'create',
            '--repo', f'{REPO_OWNER}/{REPO_NAME}',
            '--title', title,
            '--body', body
        ] + label_args + milestone_args
        
        success, output, error = run_gh_command(cmd_args)
        
        if success:
            created_count += 1
            # Extract issue number from output
            issue_url = output.strip()
            print(f"  ✅ Created: {issue_url}")
        else:
            failed_count += 1
            print(f"  ❌ Failed: {error[:100]}")
    
    print(f"\n✅ Created {created_count} issues")
    if failed_count > 0:
        print(f"❌ Failed {failed_count} issues")

def main():
    """Main execution function."""
    print("=" * 70)
    print("Project LOGOS - Phase 1 Issue Management")
    print("=" * 70)
    
    # Check if gh CLI is authenticated
    success, output, error = run_gh_command(['auth', 'status'])
    if not success:
        print("\n❌ ERROR: gh CLI is not authenticated")
        print("Please set GH_TOKEN environment variable or run 'gh auth login'")
        print(f"Error: {error}")
        sys.exit(1)
    
    print(f"✅ Authenticated with GitHub")
    
    # Step 1: Close all existing issues
    response = input("\nClose all existing issues? (yes/no): ")
    if response.lower() == 'yes':
        close_all_issues()
    else:
        print("Skipping closing existing issues")
    
    # Step 2: Create milestones
    milestone_map = create_milestones()
    print(f"Milestone status: {len(milestone_map)} milestones ready")
    
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
    response = input(f"\nCreate {len(tasks)} issues? (yes/no): ")
    if response.lower() == 'yes':
        create_issues(tasks, milestone_map)
    else:
        print("Skipping issue creation")
    
    print("\n" + "=" * 70)
    print("✅ Phase 1 issue management complete!")
    print("=" * 70)

if __name__ == '__main__':
    main()
