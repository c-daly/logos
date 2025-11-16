# Quick Start: Project Board Setup

This is a quick guide to set up the Project LOGOS tracking infrastructure. For detailed instructions, see [.github/PROJECT_BOARD_SETUP.md](.github/PROJECT_BOARD_SETUP.md).

## Prerequisites

- GitHub account with admin access to the `c-daly/logos` repository
- [GitHub CLI](https://cli.github.com/) installed and authenticated (optional but recommended)

## 5-Minute Setup

### Zero-Config Option (Recommended)

If you want to recreate the entire tracking infrastructure (labels, milestones, project board, and all 65 issues) from the canonical Phase 1 action items/spec references in one shot, run the bootstrap script:

```bash
# From the repo root
chmod +x infra/bootstrap_phase1.sh

# Optionally override the target repo via REPO_SLUG
REPO_SLUG=c-daly/logos ./infra/bootstrap_phase1.sh
```

The script wraps every command from this quick start, emits references back to `docs/action_items.md` and `docs/spec/project_logos_full.md`, and mirrors the GitHub Actions workflow (`.github/workflows/create-phase1-issues.yml`). Keep reading if you prefer to run each step manually.

### Step 1: Prep GitHub CLI

- Ensure [`gh`](https://cli.github.com/) is installed and authenticated (`gh auth login`)
- Confirm you have `repo` scope access to the target repository

### Step 2: Sync Labels

Use the bootstrap helper in labels-only mode to create/update every label defined in `.github/labels.yml`:

```bash
REPO_SLUG=c-daly/logos ./infra/bootstrap_phase1.sh labels
```

**Option B: Manual**
- Go to https://github.com/c-daly/logos/labels
- Create/update each label from `.github/labels.yml`

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
