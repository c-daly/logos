# Quick Start: Project Board Setup

This is a quick guide to set up the Project LOGOS tracking infrastructure. For detailed instructions, see [.github/PROJECT_BOARD_SETUP.md](.github/PROJECT_BOARD_SETUP.md).

## Prerequisites

- GitHub account with admin access to the `c-daly/logos` repository
- [GitHub CLI](https://cli.github.com/) installed and authenticated (optional but recommended)

## 5-Minute Setup

### Step 1: Install GitHub CLI Extensions (Optional)

```bash
# Install the label management extension
gh extension install heaths/gh-label
```

### Step 2: Sync Labels

Run the helper script (requires GitHub CLI authentication):
```bash
python .github/scripts/sync_labels.py --repo c-daly/logos
```

**Manual fallback**
- Go to https://github.com/c-daly/logos/labels
- Create each label from `.github/labels.yml`

### Step 3: Create Milestone

**Using GitHub CLI:**
```bash
gh milestone create "Phase 1 - HCG and Abstract Pipeline" \
  --repo c-daly/logos \
  --description "Phase 1 deliverables: Formalize HCG and Abstract Pipeline" \
  --due-date "2026-02-15"
```

**Using GitHub Web UI:**
- Go to https://github.com/c-daly/logos/milestones
- Click "New milestone"
- Fill in the details from above

### Step 4: Create Project Board

1. Navigate to https://github.com/c-daly/logos
2. Click "Projects" tab → "New project"
3. Choose "Board" template
4. Name: "Project LOGOS - Phase 1"
5. Click "Create"

#### Configure Columns/Views (New layout aligned with flexible spec)
- Add board columns (or workflow states) named:
  1. `Backlog`
  2. `HCG & Validation`
  3. `Sophia Planning & Execution`
  4. `Perception / Talos-Free`
  5. `Talos Capabilities` (optional—only for actuation-dependent tasks)
  6. `Apollo & UX (CLI + Browser + LLM)`
  7. `Diagnostics / Explainability`
  8. `Docs / Governance`
  9. `Ready for Demo`
  10. `Done`
- Create saved views:
  - **Surface View** grouped by the new `surface:*` labels (`cli`, `browser`, `llm`).
  - **Capability View** grouped by `capability:*` labels (`perception`, `actuation`, `explainability`).
  - **Phase View** filtered by `phase:1`, `phase:2`, etc.
  - **Demo Tracker** filtering issues tagged `Ready for Demo` column or label.

This layout keeps Talos-free, perception, and multimodal work visible alongside the embodied track.

### Step 5: Generate and Create Issues

```bash
# Generate shell script with all issue creation commands
python3 .github/scripts/generate_issues.py --format gh-cli --output create_issues.sh

# Make it executable
chmod +x create_issues.sh

# Review the script (optional)
less create_issues.sh

# Execute it to create all issues
./create_issues.sh
```

**Alternative: Generate JSON for review first**
```bash
python3 .github/scripts/generate_issues.py --format json --output issues.json
```

### Step 6: Link Issues to Project

After creating issues, add them to your project board:

**Using GitHub CLI:**
```bash
# Get your project number (usually 1 for first project)
gh project list --repo c-daly/logos

# Add all issues with phase:1 label to the project
# (This may need to be done manually or with a script)
```

**Using GitHub Web UI:**
- Open your project board
- Click "+ Add item"
- Search for issues and add them

## Weekly Maintenance

The GitHub Actions workflow will automatically run every Monday at 9:00 AM UTC to generate a progress report. You can also:

- **Trigger manually**: Go to Actions → Weekly Progress Report → Run workflow
- **View reports**: Check the Actions tab for workflow run summaries

## What's Included?

✅ **Issue Templates** - Standardized templates for all component types  
✅ **Labels** - Comprehensive labeling system (component, priority, type, workstream, status, phase)  
✅ **Milestone** - Phase 1 milestone configuration  
✅ **Project Board** - Configuration guide and automation  
✅ **Issue Generation** - Automated script to create issues from action items  
✅ **Weekly Reports** - Automated progress tracking via GitHub Actions  

## Need Help?

- **Detailed Setup**: See [.github/PROJECT_BOARD_SETUP.md](.github/PROJECT_BOARD_SETUP.md)
- **Tracking Infrastructure**: See [.github/README.md](.github/README.md)
- **Action Items**: See [docs/action_items.md](docs/action_items.md)
- **Create an Issue**: Use the `component:infrastructure` label

## Next Steps

After setup:
1. Review and organize issues on your project board
2. Assign issues to team members
3. Start working on Phase 1 tasks
4. Update issue statuses as work progresses
5. Check weekly progress reports every Monday

---

**Implements**: Section 1.2 of `docs/action_items.md` - Project Board and Issue Tracking
