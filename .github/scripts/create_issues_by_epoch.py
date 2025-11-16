#!/usr/bin/env python3
"""
Create GitHub issues organized by epochs (milestones) for Project LOGOS.

This script generates issues from action_items.md and organizes them into
appropriate epochs based on workstreams, milestones, and dependencies.

Epochs (Functionality-Based):
- Epoch 1: Infrastructure & Knowledge Foundation → M1
- Epoch 2: Language & Perception Services → M2  
- Epoch 3: Cognitive Core & Reasoning → M3
- Epoch 4: Integration & Demonstration → M4

Usage:
    python3 .github/scripts/create_issues_by_epoch.py [--dry-run] [--format json|markdown|gh-cli]
"""

import re
import json
import argparse
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class Epoch:
    """Represents a project epoch/milestone."""
    name: str
    description: str
    weeks: str
    milestone_name: str
    due_week: int


# Define epochs based on functionality
EPOCHS = [
    Epoch(
        name="Epoch 1: Infrastructure & Knowledge Foundation",
        description="Build foundational infrastructure, knowledge graph, and data storage capabilities",
        weeks="",
        milestone_name="M1: HCG Store & Retrieve",
        due_week=0
    ),
    Epoch(
        name="Epoch 2: Language & Perception Services", 
        description="Implement language processing, embeddings, and validation capabilities",
        weeks="",
        milestone_name="M2: SHACL Validation",
        due_week=0
    ),
    Epoch(
        name="Epoch 3: Cognitive Core & Reasoning",
        description="Build cognitive architecture with planning, world modeling, and reasoning",
        weeks="",
        milestone_name="M3: Simple Planning",
        due_week=0
    ),
    Epoch(
        name="Epoch 4: Integration & Demonstration",
        description="Integrate all systems and demonstrate end-to-end autonomous capabilities",
        weeks="",
        milestone_name="M4: Pick and Place",
        due_week=0
    ),
]


class EnhancedTaskParser:
    """Parse tasks from action_items.md with epoch organization."""
    
    def __init__(self, doc_path: str):
        self.doc_path = Path(doc_path)
        self.tasks = []
        
    def parse(self) -> List[Dict[str, Any]]:
        """Parse action items and extract tasks with epoch assignments."""
        with open(self.doc_path, 'r') as f:
            content = f.read()
        
        current_section = None
        current_subsection = None
        current_workstream = None
        
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Detect main sections
            if line.startswith('## '):
                current_section = line[3:].strip()
                current_subsection = None
                current_workstream = None
                
            # Detect subsections
            elif line.startswith('### '):
                current_subsection = line[4:].strip()
                
                # Check if this is a workstream
                if 'Workstream' in current_subsection:
                    current_workstream = current_subsection
                    
            # Detect tasks (unchecked items)
            elif line.startswith('- [ ] '):
                task_text = line[6:].strip()
                
                # Extract task ID if present (e.g., **A1:**, **B2:**, **M1:**)
                task_id_match = re.match(r'\*\*([A-Z]\d+):\s*(.+?)\*\*\s*(?:\((.+?)\))?', task_text)
                
                if task_id_match:
                    task_id = task_id_match.group(1)
                    task_title = task_id_match.group(2)
                    task_ref = task_id_match.group(3)  # Section reference
                    
                    # Collect sub-tasks (indented items)
                    sub_tasks = []
                    j = i + 1
                    while j < len(lines):
                        sub_line = lines[j].strip()
                        if sub_line.startswith('- [ ]') and not re.match(r'\*\*[A-Z]\d+:', sub_line[6:]):
                            sub_task = sub_line[6:].strip()
                            sub_tasks.append(sub_task)
                            j += 1
                        else:
                            break
                    
                    # Determine component, labels, and epoch
                    component = self._determine_component(task_id, task_title, current_subsection)
                    labels = self._determine_labels(task_id, task_title, current_section, 
                                                    current_subsection, current_workstream)
                    epoch = self._assign_epoch(task_id, task_title, current_workstream)
                    
                    task = {
                        'id': task_id,
                        'title': f"{task_title}",
                        'section': current_section,
                        'subsection': current_subsection,
                        'workstream': current_workstream,
                        'reference': task_ref,
                        'sub_tasks': sub_tasks,
                        'component': component,
                        'labels': labels,
                        'epoch': epoch,
                        'milestone': epoch.milestone_name if epoch else None,
                    }
                    
                    self.tasks.append(task)
                    i = j - 1  # Skip processed sub-tasks
                    
                else:
                    # Regular task without ID
                    component = self._infer_component(task_text, current_subsection)
                    labels = self._infer_labels(task_text, current_section, current_subsection)
                    epoch = self._assign_epoch_for_regular_task(task_text, current_section, 
                                                                current_subsection, current_workstream)
                    
                    task = {
                        'title': task_text,
                        'section': current_section,
                        'subsection': current_subsection,
                        'workstream': current_workstream,
                        'component': component,
                        'labels': labels,
                        'epoch': epoch,
                        'milestone': epoch.milestone_name if epoch else None,
                    }
                    self.tasks.append(task)
            
            i += 1
        
        return self.tasks
    
    def _assign_epoch(self, task_id: str, title: str, workstream: Optional[str]) -> Optional[Epoch]:
        """Assign epoch based on functionality (task ID and content)."""
        prefix = task_id[0] if task_id else ''
        title_lower = title.lower()
        
        # Milestone tasks map to their respective epochs
        if prefix == 'M':
            milestone_num = int(task_id[1]) if len(task_id) > 1 else 1
            if milestone_num <= len(EPOCHS):
                return EPOCHS[milestone_num - 1]
        
        # Workstream A: HCG Foundation - split by functionality
        if prefix == 'A':
            # A1: Extend core ontology → Epoch 1 (Knowledge Foundation)
            if task_id == 'A1':
                return EPOCHS[0]
            # A2: SHACL validation → Epoch 2 (Validation capabilities)
            elif task_id == 'A2':
                return EPOCHS[1]
            # A3: Vector integration → Epoch 2 (Embeddings/perception)
            elif task_id == 'A3':
                return EPOCHS[1]
            # A4: HCG query utilities → Epoch 1 (Infrastructure)
            else:
                return EPOCHS[0]
        
        # Workstream B: Sophia Cognitive Core → Epoch 3 (Cognitive & Reasoning)
        if prefix == 'B':
            # All cognitive tasks go to Epoch 3, except final integration
            task_num = int(task_id[1]) if len(task_id) > 1 else 1
            if task_num <= 4:
                return EPOCHS[2]  # Epoch 3: Cognitive Core
            else:
                return EPOCHS[3]  # Epoch 4: Integration (B5)
        
        # Workstream C: Support Services - split by functionality
        if prefix == 'C':
            # C1: Hermes endpoints → Epoch 2 (Language services)
            if task_id == 'C1':
                return EPOCHS[1]
            # C2: Hermes deployment → Epoch 2 (Language services)
            elif task_id == 'C2':
                return EPOCHS[1]
            # C3: Talos simulation → Epoch 3 (Needed for cognitive testing)
            elif task_id == 'C3':
                return EPOCHS[2]
            # C4: Apollo CLI → Epoch 3 (Needed for interaction)
            else:
                return EPOCHS[2]
        
        # Research tasks → Epoch 3 (Cognitive & Reasoning)
        if prefix == 'R':
            return EPOCHS[2]
        
        # Documentation tasks → Spread across epochs based on content
        if prefix == 'D':
            if 'adr' in title_lower or 'architecture' in title_lower:
                return EPOCHS[0]  # Infrastructure docs
            else:
                return EPOCHS[2]  # General docs
        
        # Outreach tasks → Epoch 4 (Demonstration)
        if prefix == 'O':
            return EPOCHS[3]
        
        return None
    
    def _assign_epoch_for_regular_task(self, task: str, section: str, 
                                       subsection: str, workstream: Optional[str]) -> Optional[Epoch]:
        """Assign epoch for tasks without IDs based on functionality."""
        task_lower = task.lower()
        
        # Infrastructure and repository setup → Epoch 1
        if 'Repository and Project Infrastructure Setup' in section:
            if 'Finalize Repository Structure' in subsection:
                return EPOCHS[0]
            elif 'Project Board' in subsection:
                return EPOCHS[0]
            elif 'Database and Infrastructure Setup' in subsection:
                # Neo4j/Milvus setup is knowledge foundation
                return EPOCHS[0]
        
        # Hermes-related tasks → Epoch 2 (Language Services)
        if 'hermes' in task_lower:
            return EPOCHS[1]
        
        # Sophia-related tasks → Epoch 3 (Cognitive Core)
        if 'sophia' in task_lower:
            return EPOCHS[2]
        
        # Apollo/Talos tasks → Epoch 3 (needed for cognitive testing)
        if 'apollo' in task_lower or 'talos' in task_lower:
            return EPOCHS[2]
        
        # Default to Epoch 1 for infrastructure
        return EPOCHS[0]
    
    def _determine_component(self, task_id: str, title: str, subsection: Optional[str]) -> str:
        """Determine component based on task ID and context."""
        if task_id.startswith('A') or task_id.startswith('M'):
            return 'infrastructure'
        elif task_id.startswith('B'):
            return 'sophia'
        elif task_id.startswith('C'):
            if 'Hermes' in title:
                return 'hermes'
            elif 'Talos' in title:
                return 'talos'
            elif 'Apollo' in title:
                return 'apollo'
            else:
                return 'infrastructure'
        elif task_id.startswith('R'):
            return 'research'
        elif task_id.startswith('D'):
            return 'documentation'
        elif task_id.startswith('O'):
            return 'outreach'
        
        return 'infrastructure'
    
    def _determine_labels(self, task_id: str, title: str, section: str,
                         subsection: str, workstream: Optional[str]) -> List[str]:
        """Determine labels for a task."""
        labels = ['phase:1']
        
        # Component label
        component = self._determine_component(task_id, title, subsection)
        if component in ['sophia', 'hermes', 'talos', 'apollo', 'infrastructure']:
            labels.append(f'component:{component}')
        
        # Workstream label
        if task_id.startswith('A'):
            labels.extend(['workstream:A', 'priority:high'])
        elif task_id.startswith('B'):
            labels.extend(['workstream:B', 'priority:high'])
        elif task_id.startswith('C'):
            labels.extend(['workstream:C', 'priority:medium'])
        elif task_id.startswith('M'):
            labels.append('priority:high')
        elif task_id.startswith('R'):
            labels.extend(['type:research', 'priority:low'])
        elif task_id.startswith('D'):
            labels.extend(['type:documentation', 'priority:medium'])
        elif task_id.startswith('O'):
            labels.extend(['type:outreach', 'priority:low'])
        
        # Type label based on content
        title_lower = title.lower()
        if 'test' in title_lower or 'validation' in title_lower:
            labels.append('type:testing')
        elif 'implement' in title_lower or 'create' in title_lower:
            labels.append('type:feature')
        elif 'document' in title_lower or 'write' in title_lower:
            labels.append('type:documentation')
        
        return list(set(labels))  # Remove duplicates
    
    def _infer_component(self, task: str, subsection: Optional[str]) -> str:
        """Infer component from task text."""
        task_lower = task.lower()
        
        if 'sophia' in task_lower:
            return 'sophia'
        elif 'hermes' in task_lower:
            return 'hermes'
        elif 'talos' in task_lower:
            return 'talos'
        elif 'apollo' in task_lower:
            return 'apollo'
        else:
            return 'infrastructure'
    
    def _infer_labels(self, task: str, section: str, subsection: str) -> List[str]:
        """Infer labels for regular tasks."""
        labels = ['phase:1']
        task_lower = task.lower()
        
        # Component labels
        if 'sophia' in task_lower:
            labels.append('component:sophia')
        if 'hermes' in task_lower:
            labels.append('component:hermes')
        if 'talos' in task_lower:
            labels.append('component:talos')
        if 'apollo' in task_lower:
            labels.append('component:apollo')
        
        # Infrastructure tasks → high priority
        if 'Repository and Project Infrastructure Setup' in section:
            labels.append('priority:high')
            labels.append('component:infrastructure')
        else:
            labels.append('priority:medium')
        
        return list(set(labels))


def format_as_json(tasks: List[Dict[str, Any]]) -> str:
    """Format tasks as JSON."""
    # Convert Epoch objects to dicts for JSON serialization
    serializable_tasks = []
    for task in tasks:
        task_copy = task.copy()
        if task_copy.get('epoch'):
            task_copy['epoch'] = {
                'name': task_copy['epoch'].name,
                'description': task_copy['epoch'].description,
                'weeks': task_copy['epoch'].weeks,
                'milestone_name': task_copy['epoch'].milestone_name,
                'due_week': task_copy['epoch'].due_week,
            }
        serializable_tasks.append(task_copy)
    
    return json.dumps(serializable_tasks, indent=2)


def format_as_markdown(tasks: List[Dict[str, Any]], group_by_epoch: bool = True) -> str:
    """Format tasks as markdown, optionally grouped by epoch."""
    output = []
    
    if group_by_epoch:
        # Group tasks by epoch
        tasks_by_epoch = {}
        for task in tasks:
            epoch_name = task['epoch'].name if task.get('epoch') else 'No Epoch'
            if epoch_name not in tasks_by_epoch:
                tasks_by_epoch[epoch_name] = []
            tasks_by_epoch[epoch_name].append(task)
        
        # Output by epoch
        for epoch_name in sorted(tasks_by_epoch.keys()):
            epoch_tasks = tasks_by_epoch[epoch_name]
            if epoch_tasks and epoch_tasks[0].get('epoch'):
                epoch = epoch_tasks[0]['epoch']
                output.append(f"# {epoch.name}\n")
                output.append(f"**Milestone:** {epoch.milestone_name}\n")
                output.append(f"{epoch.description}\n\n")
            else:
                output.append(f"# {epoch_name}\n\n")
            
            for task in epoch_tasks:
                output.append(f"## {task.get('id', 'TASK')}: {task['title']}\n")
                output.append(f"**Component:** {task['component']}\n")
                if task.get('reference'):
                    output.append(f"**Reference:** {task['reference']}\n")
                output.append(f"**Labels:** {', '.join(task.get('labels', []))}\n")
                output.append(f"**Milestone:** {task.get('milestone', 'TBD')}\n")
                
                if task.get('sub_tasks'):
                    output.append("\n**Acceptance Criteria:**\n")
                    for sub_task in task['sub_tasks']:
                        output.append(f"- [ ] {sub_task}\n")
                
                output.append("\n---\n\n")
    else:
        # Simple list
        for task in tasks:
            output.append(f"## {task.get('id', 'TASK')}: {task['title']}\n")
            if task.get('epoch'):
                output.append(f"**Epoch:** {task['epoch'].name}\n")
            output.append(f"**Milestone:** {task.get('milestone', 'TBD')}\n")
            output.append(f"**Labels:** {', '.join(task.get('labels', []))}\n")
            output.append("\n---\n\n")
    
    return ''.join(output)


def format_as_gh_cli(tasks: List[Dict[str, Any]]) -> str:
    """Format tasks as GitHub CLI commands."""
    commands = []
    
    commands.append("#!/bin/bash\n")
    commands.append("# GitHub CLI commands to create issues for Project LOGOS\n")
    commands.append("# Organized by epochs (milestones)\n")
    commands.append("# Make sure you have gh CLI installed and authenticated\n\n")
    commands.append("set -e  # Exit on error\n\n")
    commands.append("# Use environment variable for repo or default to current repo\n")
    commands.append('REPO="${GITHUB_REPOSITORY:-c-daly/logos}"\n\n')
    
    # Group by epoch
    tasks_by_epoch = {}
    for task in tasks:
        epoch_name = task['epoch'].name if task.get('epoch') else 'No Epoch'
        if epoch_name not in tasks_by_epoch:
            tasks_by_epoch[epoch_name] = []
        tasks_by_epoch[epoch_name].append(task)
    
    # Generate commands by epoch
    for epoch_name in sorted(tasks_by_epoch.keys()):
        epoch_tasks = tasks_by_epoch[epoch_name]
        
        if epoch_tasks and epoch_tasks[0].get('epoch'):
            epoch = epoch_tasks[0]['epoch']
            commands.append(f"\n# {epoch.name}\n")
            commands.append(f"# {epoch.weeks} → {epoch.milestone_name}\n\n")
        else:
            commands.append(f"\n# {epoch_name}\n\n")
        
        for task in epoch_tasks:
            task_id = task.get('id', 'TASK')
            title = f"[{task_id}] {task['title']}".replace('"', '\\"')
            
            # Build body
            body_parts = []
            if task.get('reference'):
                body_parts.append(f"**Reference:** {task['reference']}")
            if task.get('workstream'):
                body_parts.append(f"**Workstream:** {task['workstream']}")
            if task.get('epoch'):
                body_parts.append(f"**Epoch:** {task['epoch'].name}")
            
            if task.get('sub_tasks'):
                body_parts.append("\n**Acceptance Criteria:**")
                for sub_task in task['sub_tasks']:
                    body_parts.append(f"- [ ] {sub_task}")
            
            body = "\\n".join(body_parts).replace('"', '\\"')
            
            # Build labels
            labels = ','.join(task.get('labels', []))
            
            # Build milestone (will need to be created first)
            milestone = task.get('milestone', '').replace('"', '\\"')
            
            # Create gh issue create command using $REPO variable
            cmd = f'gh issue create --repo "$REPO" --title "{title}" --body "{body}" --label "{labels}"'
            if milestone:
                cmd += f' --milestone "{milestone}"'
            cmd += '\n'
            commands.append(cmd)
    
    return ''.join(commands)


def main():
    parser = argparse.ArgumentParser(
        description='Generate GitHub issues organized by epochs from action_items.md',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--format',
        choices=['json', 'markdown', 'gh-cli'],
        default='gh-cli',
        help='Output format (default: gh-cli)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file (default: stdout)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be created without executing'
    )
    
    args = parser.parse_args()
    
    # Parse tasks
    doc_path = Path(__file__).parent.parent.parent / 'docs' / 'action_items.md'
    parser_obj = EnhancedTaskParser(doc_path)
    tasks = parser_obj.parse()
    
    print(f"Parsed {len(tasks)} tasks from {doc_path}", file=__import__('sys').stderr)
    
    # Count by epoch
    epoch_counts = {}
    for task in tasks:
        epoch_name = task['epoch'].name if task.get('epoch') else 'No Epoch'
        epoch_counts[epoch_name] = epoch_counts.get(epoch_name, 0) + 1
    
    print("\nTasks by Epoch:", file=__import__('sys').stderr)
    for epoch_name, count in sorted(epoch_counts.items()):
        print(f"  {epoch_name}: {count} tasks", file=__import__('sys').stderr)
    print("", file=__import__('sys').stderr)
    
    # Format output
    if args.format == 'json':
        output = format_as_json(tasks)
    elif args.format == 'markdown':
        output = format_as_markdown(tasks, group_by_epoch=True)
    elif args.format == 'gh-cli':
        output = format_as_gh_cli(tasks)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Output written to {args.output}", file=__import__('sys').stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
