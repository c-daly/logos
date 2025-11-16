# Phase 1 Issues - Functional Epoch Organization

## Summary

This document provides the complete list of 65 Phase 1 issues organized by functional epochs.

## Epochs Overview

- **Epoch 1: Infrastructure & Knowledge Foundation** - 41 issues → M1: HCG Store & Retrieve
- **Epoch 2: Language & Perception Services** - 5 issues → M2: SHACL Validation  
- **Epoch 3: Cognitive Core & Reasoning** - 13 issues → M3: Simple Planning
- **Epoch 4: Integration & Demonstration** - 6 issues → M4: Pick and Place

## Creating Milestones and Issues

### Step 1: Create Milestones

Run these commands to create the four functional milestones:

```bash
# M1: Infrastructure & Knowledge Foundation
gh api repos/c-daly/logos/milestones -X POST \
  -f title="M1: HCG Store & Retrieve" \
  -f description="Knowledge graph operational. Neo4j + Milvus working, core ontology loaded, basic CRUD operations functional."

# M2: Language & Perception Services  
gh api repos/c-daly/logos/milestones -X POST \
  -f title="M2: SHACL Validation" \
  -f description="Validation and language services operational. SHACL validation working, Hermes endpoints functional, embeddings integrated."

# M3: Cognitive Core & Reasoning
gh api repos/c-daly/logos/milestones -X POST \
  -f title="M3: Simple Planning" \
  -f description="Cognitive capabilities demonstrated. Sophia can generate valid plans using causal reasoning over the knowledge graph."

# M4: Integration & Demonstration
gh api repos/c-daly/logos/milestones -X POST \
  -f title="M4: Pick and Place" \
  -f description="End-to-end autonomous behavior. Full pipeline working from user command to execution with knowledge graph updates."
```

### Step 2: Generate Issue Creation Commands

Use the Python generator to create the exact GitHub CLI commands:

```bash
# Generate the issue creation script
python3 .github/scripts/create_issues_by_epoch.py --format gh-cli > /tmp/create_issues.sh

# Review the script
less /tmp/create_issues.sh

# Execute it (after reviewing)
chmod +x /tmp/create_issues.sh
GH_TOKEN=$YOUR_TOKEN /tmp/create_issues.sh
```

### Alternative: Manual Creation

You can also use the Python generator to output markdown or JSON for manual review:

```bash
# Generate markdown preview
python3 .github/scripts/create_issues_by_epoch.py --format markdown > /tmp/issues.md

# Generate JSON for programmatic use
python3 .github/scripts/create_issues_by_epoch.py --format json > /tmp/issues.json
```

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
