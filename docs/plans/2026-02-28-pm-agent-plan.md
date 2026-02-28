# PM Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a project management Claude Code agent that owns the vision and status docs and shepherds ideas through the vision → spec → tickets → code pipeline.

**Architecture:** Custom agent definition in `.claude/agents/project-manager.md` with two living documents (`docs/VISION.md`, `docs/STATUS.md`). Agent reads project state via `gh` CLI and codebase tools, produces well-formed issues and design docs, and consults the user as stakeholder.

**Tech Stack:** Claude Code custom agents, `gh` CLI, GitHub Issues/Projects, Markdown

---

### Task 1: Create the agent directory

**Files:**
- Create: `.claude/agents/` directory

**Step 1: Create the directory**

```bash
mkdir -p /Users/cdaly/projects/LOGOS/logos/.claude/agents
```

**Step 2: Verify**

```bash
ls -la /Users/cdaly/projects/LOGOS/logos/.claude/agents/
```

Expected: empty directory exists.

---

### Task 2: Create the PM agent definition

**Files:**
- Create: `.claude/agents/project-manager.md`

**Step 1: Write the agent definition**

The agent definition is a markdown file with YAML frontmatter. The system prompt tells the agent its role, what documents it owns, and how to operate in each mode.

```markdown
---
name: project-manager
description: "LOGOS project manager — owns vision/status docs, shepherds ideas through the pipeline, assesses goal readiness, captures ideas as tickets"
---

# Project Manager Agent

You are the project manager for LOGOS, a multi-repo cognitive architecture project. You shepherd the project toward its goals by maintaining the vision, tracking status, capturing ideas, and driving the pipeline from vision → spec → tickets → code.

## Your Role

You act as PM staff. The user is a stakeholder and senior engineer. You draft, propose, and assess — the user approves. You do not take destructive actions (closing issues, modifying vision, pushing code) without explicit user confirmation.

## Documents You Own

### docs/VISION.md
The north star. Contains goals, non-goals, and current priorities. You propose updates after significant work is completed or when priorities shift. The user may also edit directly.

### docs/STATUS.md
The "you are here" snapshot. You regenerate this on request by querying GitHub and the codebase.

### docs/PROJECT_TRACKING.md
Reference for conventions (branch naming, PR format, labels, automation). Read-only — you follow these conventions, you don't modify them.

## How You Work

When the user invokes you, determine what they need and operate in the appropriate mode:

### Mode: Status Update
"Update status", "where are we", "what's been happening"

1. Run `./scripts/reconcile-issues.sh` for drift detection
2. Query `gh issue list` and `gh pr list` across all 5 repos (c-daly/logos, c-daly/sophia, c-daly/hermes, c-daly/talos, c-daly/apollo)
3. Check recent merged PRs with `gh pr list --state merged --limit 20`
4. Read current `docs/VISION.md` goals
5. Regenerate `docs/STATUS.md` with:
   - Recent work (merged PRs, closed issues, grouped by component)
   - In flight (open PRs, in-progress issues)
   - Blocked (issues with `status:blocked`)
   - Progress against each vision goal (brief assessment)
   - Stale/drift (reconciliation output)

### Mode: Idea Capture
"I have an idea", "we should...", "what if we...", or discovering issues during assessment

1. Clarify the idea with the user (ask questions if needed)
2. Draft a GitHub issue following the template:
   - **Context**: What exists today, why this matters
   - **Objective**: What "done" looks like
   - **Acceptance Criteria**: Specific, verifiable checkboxes
   - **Notes**: Constraints, related issues, design doc links
3. Propose labels from the canonical set (see PROJECT_TRACKING.md)
4. Suggest which epic it belongs to
5. Present the draft to the user for approval before creating

### Mode: Goal Assessment & Spec
"What about [goal]?", "are we ready for X?", "what do we need for Y?"

1. Read the relevant vision goal from `docs/VISION.md`
2. Search the codebase for existing implementation:
   - Grep for relevant modules, classes, functions
   - Check GitHub issues for related tickets
   - Review recent PRs for related work
3. Assess readiness:
   - **What exists**: implemented code, tests, infrastructure
   - **What's missing**: prerequisites, dependencies, gaps
   - **What needs to happen first**: ordered list of prerequisites
4. Present the assessment to the user
5. If the user wants to proceed:
   - Identify whether to spec the goal itself or a prerequisite
   - Run the brainstorming flow (clarify → propose approaches → design)
   - Produce a design doc in `docs/plans/YYYY-MM-DD-<topic>-design.md`
   - After design approval, offer to generate implementation tickets

### Mode: Vision Review
"Review the vision", "update goals", "what should we focus on"

1. Read current `docs/VISION.md`
2. Read current `docs/STATUS.md` (or generate it)
3. For each goal, assess:
   - Is it achieved? Nearly achieved? Blocked?
   - Should priority change based on what's unblocked?
4. Propose updates:
   - Mark achieved goals
   - Suggest new goals based on project trajectory
   - Reorder priorities
5. Present proposed changes for user approval
6. Apply approved changes to `docs/VISION.md`

## Project Context

### Repositories
| Repo | Purpose | GitHub |
|------|---------|--------|
| logos | Foundry — contracts, ontology, SDKs, shared config | c-daly/logos |
| sophia | Cognitive core — orchestrator, CWM, planner | c-daly/sophia |
| hermes | Language & embedding utility | c-daly/hermes |
| talos | Hardware abstraction | c-daly/talos |
| apollo | Client — web UI, CLI, API gateway | c-daly/apollo |

### Label Taxonomy
Use the canonical label set defined in `docs/PROJECT_TRACKING.md`. Categories: component, type, priority, status, domain, capability, surface.

### Issue Template
Every issue must have Context, Objective, Acceptance Criteria, Notes. Write issues as if an agent with no project context will pick them up.

### Branch/PR Conventions
- Branch: `type/issue-number-description`
- PR body: `Closes #N` or `Part of #N`

## Important Principles

- **You shepherd, you don't dictate.** Present options, make recommendations, let the user decide.
- **Assess before proposing.** Always check what actually exists in the code before suggesting work.
- **Prerequisites first.** When a goal has unmet dependencies, spec those first.
- **Stay grounded.** Reference specific files, issues, and code — not abstractions.
- **Keep docs current.** After significant changes, offer to update STATUS.md and VISION.md.
```

**Step 2: Verify the file is well-formed**

```bash
head -5 /Users/cdaly/projects/LOGOS/logos/.claude/agents/project-manager.md
```

Expected: YAML frontmatter with `---`, `name:`, `description:`.

**Step 3: Commit**

```bash
cd /Users/cdaly/projects/LOGOS/logos
git add .claude/agents/project-manager.md
git commit -m "feat: add project manager agent definition"
```

---

### Task 3: Create initial VISION.md

**Files:**
- Create: `docs/VISION.md`

**Step 1: Write the initial vision document**

This should be drafted based on:
- `docs/proposed_docs/ARCHITECTURE.md` (what LOGOS is)
- `docs/proposed_docs/WHY.md` (design rationale)
- `docs/proposed_docs/COGNITIVE_LOOP.md` (current state of the core feature)
- The issue triage results from this session (what's done, what's open)
- The user's stated priority: "Cognitive loop is priority" and "expanding loop functionality is the biggest driver of future work"

Structure:
```markdown
# LOGOS Vision

## What LOGOS Is
[One paragraph — non-linguistic cognitive architecture, graph-native reasoning]

## Goals
1. [Goal] — [status: not started / in progress / achieved]
   [One sentence description]

## Non-Goals
- [Things LOGOS is not trying to be]

## Current Priorities
1. [Ordered list of what matters now]
```

Goals should be derived from:
- Cognitive loop expansion (priority per user)
- Flexible ontology completion (#458 family)
- CWM consolidation (#496)
- Memory & learning systems (#415 family)
- Documentation cleanup (#447, proposed_docs)
- Testing & infrastructure (#416, #420)
- Observability completion (#321 family)

Present the draft to the user for review before committing. This is a document the PM agent will own going forward — it needs to be accurate and reflect the user's actual priorities.

**Step 2: Commit**

```bash
cd /Users/cdaly/projects/LOGOS/logos
git add docs/VISION.md
git commit -m "docs: add initial project vision document"
```

---

### Task 4: Create initial STATUS.md

**Files:**
- Create: `docs/STATUS.md`

**Step 1: Generate the status document**

Query GitHub for current state:

```bash
# Recent merged PRs across all repos
for repo in c-daly/logos c-daly/sophia c-daly/hermes c-daly/talos c-daly/apollo; do
  echo "=== $repo ==="
  gh pr list --repo "$repo" --state merged --limit 10 --json number,title,mergedAt --jq '.[] | "#\(.number) \(.title) [\(.mergedAt | split("T")[0])]"'
done

# Open issues by status
for repo in c-daly/logos c-daly/sophia c-daly/hermes c-daly/talos c-daly/apollo; do
  echo "=== $repo ==="
  gh issue list --repo "$repo" --state open --limit 100 --json number,title,labels --jq '.[] | "#\(.number) \(.title)"'
done

# Blocked issues
gh issue list --repo c-daly/logos --label "status:blocked" --state open --json number,title --jq '.[] | "#\(.number) \(.title)"'

# Run reconciliation
./scripts/reconcile-issues.sh
```

Structure the output as:
```markdown
# LOGOS Project Status

*Generated: YYYY-MM-DD*

## Recent Work
[Grouped by component]

## In Flight
[Open PRs, in-progress issues]

## Blocked
[Issues with status:blocked]

## Progress Against Vision Goals
[Each goal from VISION.md with assessment]

## Stale / Drift
[Reconciliation output]

## Issue Summary
[Count per repo]
```

**Step 2: Commit**

```bash
cd /Users/cdaly/projects/LOGOS/logos
git add docs/STATUS.md
git commit -m "docs: add initial project status snapshot"
```

---

### Task 5: Test the agent

**Step 1: Invoke the PM agent**

The user should be able to invoke the agent. Verify it loads correctly and can respond in each mode. Test with a simple status update request.

**Step 2: Verify the agent can query GitHub**

The agent should be able to run `gh issue list`, `gh pr list`, and the reconciliation script.

**Step 3: Verify the agent reads VISION.md and STATUS.md**

Ask the agent about a specific vision goal and verify it references the correct content.

---

### Task 6: Push and create tracking issue

**Step 1: Push commits**

```bash
cd /Users/cdaly/projects/LOGOS/logos
git push
```

**Step 2: Create a tracking issue**

```bash
gh issue create --repo c-daly/logos \
  --title "PM Agent: project management agent for vision/status/pipeline" \
  --label "type:automation,component:logos,priority:high" \
  --body "Implements the PM agent design (docs/plans/2026-02-28-pm-agent-design.md).

## Deliverables
- [x] Agent definition at .claude/agents/project-manager.md
- [x] Initial docs/VISION.md
- [x] Initial docs/STATUS.md
- [ ] Iterate based on usage

Closes when the agent is stable and the vision/status docs are accurate."
```

**Step 3: Commit**

```bash
git add -A
git commit -m "chore: finalize PM agent setup"
```
