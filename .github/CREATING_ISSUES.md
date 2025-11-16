# Creating Issues for Project LOGOS Phase 1

This guide explains how to create GitHub issues organized by functional epochs for Project LOGOS Phase 1.

## Overview

Phase 1 issues are organized into **four functional epochs** that represent capability layers:

1. **Epoch 1: Infrastructure & Knowledge Foundation** (41 tasks)
   - Knowledge graph storage (Neo4j + Milvus)
   - Core ontology and data structures
   - Development infrastructure
   - → Milestone: **M1: HCG Store & Retrieve**

2. **Epoch 2: Language & Perception Services** (5 tasks)
   - Language I/O (STT, TTS, NLP)
   - Semantic embeddings
   - Knowledge validation (SHACL)
   - → Milestone: **M2: SHACL Validation**

3. **Epoch 3: Cognitive Core & Reasoning** (13 tasks)
   - Planning and reasoning
   - World modeling and state management
   - Orchestration and control flow
   - → Milestone: **M3: Simple Planning**

4. **Epoch 4: Integration & Demonstration** (6 tasks)
   - End-to-end autonomous behavior
   - User interaction → execution → feedback
   - Public demonstration and release
   - → Milestone: **M4: Pick and Place**

**Total:** 65 issues across all epochs

## Quick Start

### Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Admin access to the `c-daly/logos` repository
- Labels already synced (see `docs/QUICK_START_PROJECT_BOARD.md`)

### Three-Step Process

```bash
# Step 1: Create milestones
.github/scripts/create_milestones.sh

# Step 2: Create all issues
.github/scripts/create_issues.sh

# Step 3: Verify in GitHub
# Visit https://github.com/c-daly/logos/issues
# Visit https://github.com/c-daly/logos/milestones
```

## Detailed Instructions

### Step 1: Create Milestones

Create the four functional milestones that represent each epoch:

```bash
cd /home/runner/work/logos/logos
.github/scripts/create_milestones.sh
```

This creates:
- M1: HCG Store & Retrieve
- M2: SHACL Validation
- M3: Simple Planning
- M4: Pick and Place

**Verify milestones:**
```bash
gh milestone list --repo c-daly/logos
```

### Step 2: Create Issues

Generate and create all 65 issues organized by functional epoch:

```bash
.github/scripts/create_issues.sh
```

This will:
- Parse all tasks from `docs/action_items.md`
- Assign each task to the appropriate functional epoch/milestone
- Create GitHub issues with proper titles, labels, and descriptions
- Link issues to their milestones

**Expected output:**
```
# Epoch 1: Infrastructure & Knowledge Foundation
# M1: HCG Store & Retrieve
Creating issue: [TASK] Set up CI/CD for validation tests...
Creating issue: [A1] Extend core ontology...
...

# Epoch 2: Language & Perception Services
# M2: SHACL Validation
Creating issue: [A2] Implement SHACL validation...
...

Total: 65 issues created
```

### Step 3: Verify

Check that issues were created correctly:

```bash
# List all Phase 1 issues
gh issue list --repo c-daly/logos --label "phase:1"

# List issues by milestone
gh issue list --repo c-daly/logos --milestone "M1: HCG Store & Retrieve"
gh issue list --repo c-daly/logos --milestone "M2: SHACL Validation"
gh issue list --repo c-daly/logos --milestone "M3: Simple Planning"
gh issue list --repo c-daly/logos --milestone "M4: Pick and Place"

# List issues by epoch (via labels)
gh issue list --repo c-daly/logos --label "component:infrastructure"
gh issue list --repo c-daly/logos --label "component:hermes"
gh issue list --repo c-daly/logos --label "component:sophia"
```

**Web UI verification:**
- Issues: https://github.com/c-daly/logos/issues
- Milestones: https://github.com/c-daly/logos/milestones
- Project board: Add issues to board as needed

## Issue Organization

### Functional Epoch Breakdown

#### Epoch 1: Infrastructure & Knowledge Foundation (41 issues)
- Repository setup for all components
- Neo4j + Milvus infrastructure
- Core ontology (A1)
- Query utilities (A4)
- Database setup tasks
- Architecture documentation (D1)
- Milestone M1

#### Epoch 2: Language & Perception Services (5 issues)
- SHACL validation (A2)
- Vector integration (A3)
- Hermes endpoints (C1)
- Hermes deployment (C2)
- Milestone M2

#### Epoch 3: Cognitive Core & Reasoning (13 issues)
- Orchestrator (B1)
- CWM-A world model (B2)
- Planner (B3)
- Executor stub (B4)
- Talos simulation (C3)
- Apollo CLI (C4)
- Research tasks (R1, R2, R3)
- Documentation (D2, D3, D4)
- Milestone M3

#### Epoch 4: Integration & Demonstration (6 issues)
- End-to-end integration (B5)
- Outreach tasks (O1, O2, O3, O4)
- Milestone M4

### Labels Applied

Each issue receives multiple labels:

- **Phase:** `phase:1` (all issues)
- **Component:** `component:infrastructure`, `component:sophia`, `component:hermes`, `component:talos`, `component:apollo`
- **Workstream:** `workstream:A`, `workstream:B`, `workstream:C`
- **Priority:** `priority:high`, `priority:medium`, `priority:low`
- **Type:** `type:feature`, `type:testing`, `type:documentation`, `type:research`, `type:outreach`

### Issue Format

Each issue includes:
- **Title:** `[TASK_ID] Task name` (e.g., `[A1] Extend core ontology`)
- **Body:**
  - Reference to specification section (if applicable)
  - Workstream assignment
  - Functional epoch assignment
  - Acceptance criteria (sub-tasks)
- **Labels:** Component, workstream, priority, type, phase
- **Milestone:** M1, M2, M3, or M4

## Customization

### Regenerate Issues

If you need to regenerate the issue creation script (e.g., after updating `action_items.md`):

```bash
# Regenerate with current settings
python3 .github/scripts/create_issues_by_epoch.py --format gh-cli --output .github/scripts/create_issues.sh

# Preview in markdown format
python3 .github/scripts/create_issues_by_epoch.py --format markdown --output issues_preview.md

# Export as JSON
python3 .github/scripts/create_issues_by_epoch.py --format json --output issues.json
```

### Modify Epoch Assignments

Edit `.github/scripts/create_issues_by_epoch.py`:
- Modify the `EPOCHS` array to change epoch definitions
- Edit `_assign_epoch()` method to change task→epoch mappings
- Edit `_assign_epoch_for_regular_task()` for non-ID tasks

## Functional Capability Stack

The epochs build on each other to create autonomous capabilities:

```
┌─────────────────────────────────────────────────────┐
│  Epoch 4: Integration & Demonstration               │
│  • End-to-end autonomous behavior                   │
└─────────────────────────────────────────────────────┘
                        ↑
┌─────────────────────────────────────────────────────┐
│  Epoch 3: Cognitive Core & Reasoning                │
│  • Planning, reasoning, world modeling              │
└─────────────────────────────────────────────────────┘
                        ↑
┌─────────────────────────────────────────────────────┐
│  Epoch 2: Language & Perception Services            │
│  • Language I/O, validation, embeddings             │
└─────────────────────────────────────────────────────┘
                        ↑
┌─────────────────────────────────────────────────────┐
│  Epoch 1: Infrastructure & Knowledge Foundation     │
│  • Knowledge graph, storage, infrastructure         │
└─────────────────────────────────────────────────────┘
```

## Dependencies

Each epoch depends on capabilities from previous epochs:
- **Epoch 2** requires Epoch 1 (knowledge storage must exist before validation)
- **Epoch 3** requires Epochs 1-2 (reasoning requires validated knowledge and language I/O)
- **Epoch 4** requires Epochs 1-3 (integration requires all capabilities)

## Next Steps After Creating Issues

1. **Add issues to project board:** Create a GitHub Project and add all issues
2. **Assign team members:** Distribute tasks based on expertise
3. **Set up automation:** Configure project board automation rules
4. **Start with Epoch 1:** Begin foundation work before moving to higher epochs
5. **Track progress:** Use weekly progress reports and milestone reviews

## Troubleshooting

### Issues not created
- Ensure GitHub CLI is authenticated: `gh auth status`
- Check repository permissions: `gh repo view c-daly/logos`
- Verify labels exist: `gh label list --repo c-daly/logos`

### Duplicate issues
- Issues are created fresh each time the script runs
- Delete duplicates manually: `gh issue delete <number> --repo c-daly/logos`
- Or close as duplicate: `gh issue close <number> --repo c-daly/logos --reason "duplicate"`

### Wrong epoch assignment
- Edit `.github/scripts/create_issues_by_epoch.py`
- Regenerate the creation script
- Delete incorrectly assigned issues
- Re-run the creation script

## Additional Resources

- **Functional Epoch Documentation:** `.github/EPOCHS.md`
- **Action Items Source:** `docs/action_items.md`
- **Project Board Setup:** `.github/PROJECT_BOARD_SETUP.md`
- **Quick Start Guide:** `docs/QUICK_START_PROJECT_BOARD.md`
- **Full Specification:** `docs/spec/project_logos_full.md`

---

**Last Updated:** 2025-11-16
**Issue Count:** 65 issues across 4 functional epochs
**Organization:** Functionality-based (Infrastructure → Language → Cognition → Integration)
