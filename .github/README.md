# Project Tracking Infrastructure

This directory contains all the infrastructure for project management, issue tracking, and progress monitoring for Project LOGOS.

## Contents

### Issue Templates (`ISSUE_TEMPLATE/`)

Pre-configured templates for creating different types of issues:

- **sophia-task.yml** - Tasks for Sophia cognitive core (Orchestrator, CWM-A, CWM-G, Planner, Executor)
- **hermes-task.yml** - Tasks for Hermes language utility (STT, TTS, NLP, embeddings)
- **talos-task.yml** - Tasks for Talos hardware abstraction (sensors, actuators)
- **apollo-task.yml** - Tasks for Apollo UI/client (dashboard, visualization)
- **infrastructure-task.yml** - Tasks for HCG, ontology, CI/CD, repository setup
- **research-task.yml** - Research sprints and investigations
- **documentation-task.yml** - Documentation and knowledge management tasks

### Labels Configuration (`labels.yml`)

Comprehensive labeling system with categories:

- **Component Labels**: `component:sophia`, `component:hermes`, `component:talos`, `component:apollo`, `component:infrastructure`
- **Priority Labels**: `priority:high`, `priority:medium`, `priority:low`
- **Type Labels**: `type:feature`, `type:bug`, `type:research`, `type:documentation`, etc.
- **Workstream Labels**: `workstream:A`, `workstream:B`, `workstream:C`
- **Status Labels**: `status:blocked`, `status:in-progress`, `status:review`, `status:on-hold`
- **Phase Labels**: `phase:1`, `phase:2`

### Project Configuration (`project_config.yml`)

Documents the desired structure for the GitHub Project Board:

- Board views (By Workstream, By Component, By Priority, etc.)
- Custom fields (Status, Priority, Workstream, Component, Estimated Effort, Phase)
- Automation workflows
- Milestone configuration
- Weekly progress tracking configuration

### Scripts (`scripts/`)

**generate_issues.py** - Automated issue generation from action items

```bash
# Generate GitHub CLI commands to create all issues
python .github/scripts/generate_issues.py --format gh-cli --output create_issues.sh
chmod +x create_issues.sh
./create_issues.sh

# Generate JSON for review
python .github/scripts/generate_issues.py --format json --output issues.json

# Generate Markdown summaries
python .github/scripts/generate_issues.py --format markdown --output issues.md
```

### Workflows (`workflows/`)

**validate-artifacts.yml** - CI/CD validation for LOGOS artifacts

- Runs on push to main/develop branches (when artifacts change)
- Runs on pull requests (when artifacts change)
- Can be triggered manually via workflow_dispatch
- Validates three core artifacts:
  - **Cypher Ontology** (`ontology/core_ontology.cypher`) - Syntax validation using Neo4j 5.13.0
  - **SHACL Shapes** (`ontology/shacl_shapes.ttl`) - RDF/Turtle syntax validation using rdflib
  - **OpenAPI Contract** (`contracts/hermes.openapi.yaml`) - OpenAPI 3.1.0 spec validation using swagger-cli
- Provides aggregated pass/fail summary in GitHub Actions
- Ensures canonical LOGOS artifacts remain syntactically valid

**weekly-progress.yml** - Automated weekly progress reporting

- Runs every Monday at 9:00 AM UTC
- Can be triggered manually via workflow_dispatch
- Generates summary of:
  - Issues in progress
  - Issues completed in the last week
  - Blocked issues
  - Breakdown by component
- Output appears in GitHub Actions summary

**create-phase1-issues.yml** - Project board and issue setup

- Manual workflow for creating Phase 1 project infrastructure
- Creates milestones (M1-M4)
- Generates and creates 65 Phase 1 issues organized by functional epochs
- Sets up GitHub Project board
- Links issues to project board

### Documentation

**PROJECT_BOARD_SETUP.md** - Complete setup guide

Step-by-step instructions for:
1. Creating and syncing labels
2. Creating milestones
3. Setting up the GitHub Project Board
4. Generating and creating issues
5. Setting up weekly progress tracking
6. Maintenance best practices

## Quick Start

### 1. Set Up Labels

```bash
# Install gh-label extension
gh extension install heaths/gh-label

# Sync labels
gh label sync --repo c-daly/logos --file .github/labels.yml
```

### 2. Create Milestone

```bash
gh milestone create "Phase 1 - HCG and Abstract Pipeline" \
  --repo c-daly/logos \
  --description "Phase 1 deliverables: Formalize HCG and Abstract Pipeline" \
  --due-date "2026-02-15"
```

### 3. Create Project Board

1. Go to https://github.com/c-daly/logos/projects
2. Click "New project"
3. Choose "Board" template
4. Name it "Project LOGOS - Phase 1"
5. Configure views as documented in `PROJECT_BOARD_SETUP.md`

### 4. Generate Issues

```bash
# Generate and execute issue creation commands
python .github/scripts/generate_issues.py --format gh-cli --output create_issues.sh
chmod +x create_issues.sh
./create_issues.sh
```

### 5. Link Issues to Project

```bash
# Get project number
gh project list --repo c-daly/logos

# Add issues to project (example)
gh project item-add <PROJECT_NUMBER> --repo c-daly/logos --issue <ISSUE_NUMBER>
```

## Reference

This tracking infrastructure implements section 1.2 of `docs/action_items.md`:

- ✅ Create GitHub Project board for LOGOS
- ✅ Set up milestone: "Phase 1 — HCG and Abstract Pipeline"
- ✅ Create issues for all Phase 1 tasks
- ✅ Establish labeling system
- ✅ Set up weekly progress tracking

## Maintenance

- **Daily**: Update issue statuses as work progresses
- **Weekly**: Review progress report from GitHub Actions
- **Weekly**: Update `docs/action_items.md` with completed items
- **As Needed**: Create new issues using templates
- **As Needed**: Adjust priorities based on project needs

## Additional Resources

- [GitHub Projects Documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub CLI Documentation](https://cli.github.com/manual/)

## Support

For issues with the tracking infrastructure, create an issue with the `component:infrastructure` label.
