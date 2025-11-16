# Phase 1 Issue Management

This directory contains scripts to manage Phase 1 issues for Project LOGOS without using GitHub Actions workflows.

## Overview

The issue management system:
1. Closes all existing issues in the repository
2. Creates 4 milestones (M1, M2, M3, M4) with descriptions
3. Creates all 65 Phase 1 issues organized by functional epochs
4. Assigns proper labels, milestones, and enhanced descriptions to each issue

## Issue Organization

Issues are organized across 4 functional epochs:

- **Epoch 1: Infrastructure & Knowledge Foundation** (41 issues) → M1: HCG Store & Retrieve
- **Epoch 2: Language & Perception Services** (5 issues) → M2: SHACL Validation  
- **Epoch 3: Cognitive Core & Reasoning** (13 issues) → M3: Simple Planning
- **Epoch 4: Integration & Demonstration** (6 issues) → M4: Pick and Place

## Scripts

### `manage_issues.py` (Interactive)

Interactive script that prompts for confirmation before closing issues and creating new ones.

**Usage:**
```bash
# Set GitHub token
export GH_TOKEN=your_github_token_here

# Run interactive script
cd /home/runner/work/logos/logos
python3 .github/scripts/manage_issues.py
```

### `manage_issues_auto.py` (Automatic)

Non-interactive script that automatically performs all operations.

**Usage:**
```bash
# Set GitHub token
export GH_TOKEN=your_github_token_here

# Run automatic script
cd /home/runner/work/logos/logos
python3 .github/scripts/manage_issues_auto.py
```

## Requirements

- Python 3.x
- GitHub CLI (`gh`) installed
- GitHub personal access token with `repo` scope

## Getting a GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Select scopes: `repo` (Full control of private repositories)
4. Generate and copy the token
5. Set it in your environment: `export GH_TOKEN=your_token_here`

## Issue Format

Each created issue includes:

- **Title**: `[TASK_ID] Task description`
- **Body**:
  - Reference to specification section (if applicable)
  - Workstream assignment
  - Epoch and description
  - Component assignment
  - Acceptance criteria (subtasks)
  - Context based on workstream

- **Labels**: 
  - `phase:1`
  - `component:{sophia|hermes|talos|apollo|infrastructure}`
  - `workstream:{A|B|C}` (if applicable)
  - `priority:{high|medium|low}`
  - `type:{feature|testing|documentation|research|outreach}` (if applicable)

- **Milestone**: Assigned to appropriate milestone (M1, M2, M3, or M4)

## Dependencies

The scripts use the existing `create_issues_by_epoch.py` parser to extract task information from `docs/action_items.md`.

## Verification

After running the script, verify the results:

```bash
# Check milestone distribution
gh api repos/c-daly/logos/milestones | jq '.[] | {title: .title, open_issues: .open_issues}'

# List all Phase 1 issues
gh issue list --repo c-daly/logos --label "phase:1" --limit 100

# List by epoch (milestone)
gh issue list --repo c-daly/logos --milestone "M1: HCG Store & Retrieve"
gh issue list --repo c-daly/logos --milestone "M2: SHACL Validation"
gh issue list --repo c-daly/logos --milestone "M3: Simple Planning"
gh issue list --repo c-daly/logos --milestone "M4: Pick and Place"
```

## Notes

- This approach uses the GitHub REST API via `gh` CLI - **NO WORKFLOWS**
- All 63 existing issues will be closed before creating new ones
- The script provides progress output for each step
- Issues are created with enhanced descriptions including context and acceptance criteria
- Failed creations are reported but don't stop the script
