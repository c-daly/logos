#!/usr/bin/env python3
"""
Generate GitHub issues from the action_items.md document.

This script parses the action items document and generates issue data
that can be used to create GitHub issues either manually or via GitHub CLI.

Usage:
    python .github/scripts/generate_issues.py [--format json|markdown|gh-cli]
"""

import re
import json
import argparse
from typing import List, Dict, Any
from pathlib import Path


class TaskParser:
    """Parse tasks from the action items markdown document."""
    
    def __init__(self, doc_path: str):
        self.doc_path = Path(doc_path)
        self.tasks = []
        
    def parse(self) -> List[Dict[str, Any]]:
        """Parse the action items document and extract tasks."""
        with open(self.doc_path, 'r') as f:
            content = f.read()
        
        # Parse sections and tasks
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
                    
            # Detect tasks (unchecked items in lists)
            elif line.startswith('- [ ] '):
                task_text = line[6:].strip()
                
                # Extract task ID if present (e.g., **A1:** or **B2:**)
                task_id_match = re.match(r'\*\*([A-Z]\d+):\s*(.+?)\*\*\s*(?:\((.+?)\))?', task_text)
                
                if task_id_match:
                    task_id = task_id_match.group(1)
                    task_title = task_id_match.group(2)
                    task_ref = task_id_match.group(3)  # Section reference if present
                    
                    # Collect sub-tasks (indented items)
                    sub_tasks = []
                    j = i + 1
                    while j < len(lines) and lines[j].strip().startswith('- [ ]'):
                        sub_task = lines[j].strip()[6:].strip()
                        sub_tasks.append(sub_task)
                        j += 1
                    
                    # Determine component and labels
                    component, labels = self._determine_component_and_labels(
                        task_id, task_title, current_section, current_subsection, current_workstream
                    )
                    
                    task = {
                        'id': task_id,
                        'title': f"[{component.title()}] {task_title}",
                        'section': current_section,
                        'subsection': current_subsection,
                        'workstream': current_workstream,
                        'reference': task_ref,
                        'sub_tasks': sub_tasks,
                        'component': component,
                        'labels': labels
                    }
                    
                    self.tasks.append(task)
                    i = j - 1  # Skip the sub-tasks we already processed
                    
                else:
                    # Regular task without ID
                    task = {
                        'title': task_text,
                        'section': current_section,
                        'subsection': current_subsection,
                        'workstream': current_workstream,
                        'component': self._infer_component(task_text, current_subsection),
                        'labels': self._infer_labels(task_text, current_section, current_subsection)
                    }
                    self.tasks.append(task)
            
            i += 1
        
        return self.tasks
    
    def _determine_component_and_labels(self, task_id: str, title: str, 
                                       section: str, subsection: str, 
                                       workstream: str) -> tuple:
        """Determine component and labels for a task."""
        component = "infrastructure"
        labels = ["phase:1"]
        
        # Determine component based on task ID prefix or workstream
        if task_id and task_id.startswith('A'):
            component = "infrastructure"
            labels.extend(["component:infrastructure", "workstream:A", "priority:high"])
        elif task_id and task_id.startswith('B'):
            component = "sophia"
            labels.extend(["component:sophia", "workstream:B", "priority:high"])
        elif task_id and task_id.startswith('C'):
            # C tasks could be Hermes, Talos, or Apollo
            if 'Hermes' in title:
                component = "hermes"
                labels.extend(["component:hermes", "workstream:C", "priority:medium"])
            elif 'Talos' in title:
                component = "talos"
                labels.extend(["component:talos", "workstream:C", "priority:medium"])
            elif 'Apollo' in title:
                component = "apollo"
                labels.extend(["component:apollo", "workstream:C", "priority:medium"])
            else:
                component = "infrastructure"
                labels.extend(["component:infrastructure", "workstream:C", "priority:medium"])
        elif task_id and task_id.startswith('R'):
            component = "research"
            labels.extend(["type:research", "priority:low"])
        elif task_id and task_id.startswith('D'):
            component = "docs"
            labels.extend(["type:documentation", "priority:medium"])
        elif task_id and task_id.startswith('M'):
            component = "infrastructure"
            labels.extend(["component:infrastructure", "priority:high"])
        
        # Add type based on content
        if 'test' in title.lower() or 'validation' in title.lower():
            labels.append("type:testing")
        elif 'implement' in title.lower() or 'create' in title.lower():
            labels.append("type:feature")
        elif 'document' in title.lower() or 'write' in title.lower():
            labels.append("type:documentation")
        
        return component, list(set(labels))  # Remove duplicates
    
    def _infer_component(self, task: str, subsection: str) -> str:
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
        """Infer labels from task content."""
        labels = ["phase:1"]
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
        
        # Priority (default to medium for non-workstream tasks)
        if 'Repository and Project Infrastructure Setup' in section:
            labels.append('priority:high')
        else:
            labels.append('priority:medium')
        
        return list(set(labels))


def format_as_json(tasks: List[Dict[str, Any]]) -> str:
    """Format tasks as JSON."""
    return json.dumps(tasks, indent=2)


def format_as_markdown(tasks: List[Dict[str, Any]]) -> str:
    """Format tasks as markdown issue descriptions."""
    output = []
    
    for task in tasks:
        output.append(f"## {task['title']}\n")
        output.append(f"**Section:** {task.get('section', 'N/A')}\n")
        if task.get('subsection'):
            output.append(f"**Subsection:** {task['subsection']}\n")
        if task.get('workstream'):
            output.append(f"**Workstream:** {task['workstream']}\n")
        if task.get('reference'):
            output.append(f"**Reference:** {task['reference']}\n")
        
        output.append(f"\n**Labels:** {', '.join(task.get('labels', []))}\n")
        
        if task.get('sub_tasks'):
            output.append("\n**Sub-tasks:**\n")
            for sub_task in task['sub_tasks']:
                output.append(f"- [ ] {sub_task}\n")
        
        output.append("\n---\n\n")
    
    return ''.join(output)


def format_as_gh_cli(tasks: List[Dict[str, Any]], repo_slug: str) -> str:
    """Format tasks as GitHub CLI commands."""
    commands = []
    
    commands.append("#!/bin/bash\n")
    commands.append("# GitHub CLI commands to create issues for Project LOGOS\n")
    commands.append("# Make sure you have gh CLI installed and authenticated\n")
    commands.append("# Usage: bash create_issues.sh\n\n")
    
    for task in tasks:
        title = task['title'].replace('"', '\\"')
        
        # Build body
        body_parts = []
        body_parts.append(f"**Section:** {task.get('section', 'N/A')}")
        if task.get('subsection'):
            body_parts.append(f"**Subsection:** {task['subsection']}")
        if task.get('workstream'):
            body_parts.append(f"**Workstream:** {task['workstream']}")
        if task.get('reference'):
            body_parts.append(f"**Reference:** {task['reference']}")
        
        if task.get('sub_tasks'):
            body_parts.append("\n**Sub-tasks:**")
            for sub_task in task['sub_tasks']:
                body_parts.append(f"- [ ] {sub_task}")
        
        body = "\\n".join(body_parts).replace('"', '\\"')
        
        # Build labels
        labels = ','.join(task.get('labels', []))
        
        # Create gh issue create command
        cmd = f'gh issue create --repo {repo_slug} --title "{title}" --body "{body}" --label "{labels}"\n'
        commands.append(cmd)
    
    return ''.join(commands)


def main():
    parser = argparse.ArgumentParser(
        description='Generate GitHub issues from action_items.md'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'markdown', 'gh-cli'],
        default='json',
        help='Output format (default: json)'
    )
    parser.add_argument(
        '--repo',
        default='c-daly/logos',
        help='Repository slug to target when emitting gh commands (default: c-daly/logos)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file (default: stdout)'
    )
    
    args = parser.parse_args()
    
    # Parse tasks
    doc_path = Path(__file__).parent.parent.parent / 'docs' / 'action_items.md'
    parser_obj = TaskParser(doc_path)
    tasks = parser_obj.parse()
    
    # Format output
    if args.format == 'json':
        output = format_as_json(tasks)
    elif args.format == 'markdown':
        output = format_as_markdown(tasks)
    elif args.format == 'gh-cli':
        output = format_as_gh_cli(tasks, args.repo)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Output written to {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
