# Phase 1 Issues - Functional Epoch Organization

## Summary

This document provides the complete list of 65 Phase 1 issues organized by functional epochs.

## Epochs Overview

- **Epoch 1: Infrastructure & Knowledge Foundation** - 41 issues → M1: HCG Store & Retrieve
- **Epoch 2: Language & Perception Services** - 5 issues → M2: SHACL Validation  
- **Epoch 3: Cognitive Core & Reasoning** - 13 issues → M3: Simple Planning
- **Epoch 4: Integration & Demonstration** - 6 issues → M4: Pick and Place

## Creating Milestones and Issues

### Recommended: Use GitHub Actions Workflow

The easiest way to create all milestones, issues, and the project board is using the provided GitHub Actions workflow:

1. Go to **Actions** tab in the repository
2. Select **"Create Phase 1 Issues and Project Board"** workflow
3. Click **"Run workflow"**
4. Options:
   - **create_milestones**: Check to create M1, M2, M3, M4 (default: true)
   - **create_project**: Check to create the project board (default: true)
5. Click **"Run workflow"** button

The workflow will:
- Create GitHub Project board "Project LOGOS - Phase 1"
- Create 4 milestones (M1, M2, M3, M4)
- Create all 65 issues with proper labels and milestone assignments
- Add all issues to the project board automatically
- Organize issues by functional epoch
- Provide a summary with links

**Status:** Workflow available at `.github/workflows/create-phase1-issues.yml`

### Alternative: Manual Creation with GitHub CLI

If you prefer to run locally with GitHub CLI:

```bash
# Authenticate GitHub CLI first
gh auth login

# Generate the issue creation script
python3 .github/scripts/create_issues_by_epoch.py --format gh-cli > /tmp/create_issues.sh

# Review the script
less /tmp/create_issues.sh

# Execute it
chmod +x /tmp/create_issues.sh
bash /tmp/create_issues.sh
```

### Reset and Recreate All Phase 1 Issues

**⚠️ WARNING: This is a DESTRUCTIVE operation!**

If you need to reset all Phase 1 issues (close existing ones and recreate from `docs/action_items.md`), use the `--include-reset-phase1` flag:

```bash
# Authenticate GitHub CLI first
gh auth login

# Generate the reset script
python3 .github/scripts/create_issues_by_epoch.py \
  --format gh-cli \
  --include-reset-phase1 \
  > /tmp/reset_phase1_issues.sh

# Review the script to understand what it will do
less /tmp/reset_phase1_issues.sh

# Execute it (you will have 5 seconds to cancel with Ctrl+C)
chmod +x /tmp/reset_phase1_issues.sh
bash /tmp/reset_phase1_issues.sh
```

**What the reset script does:**
1. Displays a clear warning about the destructive operation
2. Waits 5 seconds to allow you to cancel (Ctrl+C)
3. Fetches all open issues with the `phase:1` label
4. Closes each issue with a comment: "Closing as part of Phase 1 reset (issues will be recreated from docs/action_items.md)."
5. Creates all Phase 1 issues fresh from `docs/action_items.md`

**Use cases for reset:**
- You've made significant changes to `docs/action_items.md` and want to sync all issues
- You want to clean up and start fresh with Phase 1 issues
- You're testing the issue creation process

**Note:** GitHub doesn't support hard deletion of issues, so closed issues will remain in the repository history but won't clutter your active issue list.

## Functional Epoch Breakdown

### Epoch 1: Infrastructure & Knowledge Foundation (41 issues)

**Functional Focus:** Build foundational infrastructure, knowledge graph, and data storage capabilities

**Key Components:**
- Repository initialization for all components (Sophia, Hermes, Talos, Apollo)
- Neo4j + Milvus development cluster
- Core HCG ontology
- Basic query utilities (A4)
- Development environments
- Project tracking infrastructure

**Major Tasks:**
- A1: Extend core ontology (Section 4.1, Appendix A)
- A4: HCG query utilities
- M1: HCG can store and retrieve entities
- D1: Architecture Decision Records (ADRs)
- All repository setup tasks
- All infrastructure setup tasks

**Milestone:** M1: HCG Store & Retrieve

---

### Epoch 2: Language & Perception Services (5 issues)

**Functional Focus:** Add language processing, embeddings, and validation capabilities

**Key Components:**
- SHACL validation layer
- Vector database integration
- Hermes language services (STT, TTS, NLP, embeddings)
- Extended ontology for pick-and-place domain

**Major Tasks:**
- A2: Implement SHACL validation (Section 4.3.1)
- A3: Vector integration (Section 4.2)
- C1: Implement Hermes endpoints (Section 3.4, Table 2)
- C2: Hermes deployment
- M2: SHACL validation catches errors

**Milestone:** M2: SHACL Validation

---

### Epoch 3: Cognitive Core & Reasoning (13 issues)

**Functional Focus:** Build cognitive architecture with planning, world modeling, and reasoning

**Key Components:**
- Orchestrator (subsystem coordination)
- CWM-A (Abstract World Model)
- Planner (causal reasoning)
- Executor stub
- Talos simulated interfaces
- Apollo command interface
- Research investigations
- Documentation infrastructure

**Major Tasks:**
- B1: Orchestrator implementation (Section 3.3)
- B2: CWM-A (Abstract World Model) (Section 3.3)
- B3: Planner (initial version) (Section 3.3)
- B4: Executor (stub) (Section 3.3)
- C3: Talos simulated interfaces
- C4: Apollo command interface (basic)
- R1: Survey of causal reasoning methods
- R2: Graph neural network integration
- R3: Multi-modal grounding
- D2: Developer onboarding guide
- D3: API documentation
- D4: Weekly progress reports
- M3: Sophia can plan simple actions

**Milestone:** M3: Simple Planning

---

### Epoch 4: Integration & Demonstration (6 issues)

**Functional Focus:** Integrate all systems and demonstrate end-to-end autonomous capabilities

**Key Components:**
- End-to-end integration pipeline
- Demonstration materials
- Open-source preparation
- Research community engagement

**Major Tasks:**
- B5: End-to-end integration
- O1: Publish blog post — "Non-linguistic Cognition: Why Graphs Matter"
- O2: Create demo video
- O3: Open-source release
- O4: Engage with research community
- M4: End-to-end "pick and place"

**Milestone:** M4: Pick and Place

---

## Issue Labels

Each issue should be tagged with appropriate labels:

- **Phase:** `phase:1`
- **Component:** `component:infrastructure`, `component:sophia`, `component:hermes`, `component:talos`, `component:apollo`
- **Workstream:** `workstream:A`, `workstream:B`, `workstream:C`
- **Priority:** `priority:high`, `priority:medium`, `priority:low`
- **Type:** `type:feature`, `type:testing`, `type:documentation`, `type:research`, `type:outreach`

## Functional Dependencies

```
Epoch 1: Infrastructure & Knowledge Foundation
    │
    ├──→ Epoch 2: Language & Perception Services
    │        │
    │        └──→ Epoch 3: Cognitive Core & Reasoning
    │                  │
    └──────────────────┴──→ Epoch 4: Integration & Demonstration
```

## Verification

After creating issues, verify the organization:

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

## Resources

- **Epoch Documentation:** `.github/EPOCHS.md`
- **Issue Generator:** `.github/scripts/create_issues_by_epoch.py`
- **Action Items Source:** `docs/action_items.md`
- **Full Specification:** `docs/spec/project_logos_full.md`

---

**Generated:** 2025-11-16  
**Total Issues:** 65  
**Organization:** Functional Epochs (Infrastructure → Language → Cognition → Integration)
