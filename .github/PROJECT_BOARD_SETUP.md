# Project Board and Issue Tracking Setup Guide

This guide provides instructions for setting up the GitHub Project Board and Issue Tracking system for Project LOGOS, as specified in section 1.2 of `docs/action_items.md`.

## Overview

The project tracking system consists of:
- **GitHub Project Board**: For visual task management and progress tracking
- **Milestones**: To group issues by project phase
- **Labels**: To categorize and filter issues by component, priority, type, and workstream
- **Issue Templates**: To standardize issue creation
- **Automated Issue Generation**: Script to create issues from action items

## Prerequisites

- GitHub account with admin access to the `c-daly/logos` repository
- GitHub CLI (`gh`) installed and authenticated (optional, for automation)

## Step 1: Create Labels

Labels are defined in `.github/labels.yml`. To apply them to the repository:

### Option A: Using GitHub CLI (Recommended)

```bash
# Install gh-label extension if not already installed
gh extension install heaths/gh-label

# Sync labels from the YAML file
gh label sync --repo c-daly/logos --file .github/labels.yml
```

### Option B: Manual Creation

Navigate to: `https://github.com/c-daly/logos/labels`

Create each label from `.github/labels.yml` with the specified name, color, and description.

## Step 2: Create Milestone

Create a milestone for Phase 1:

### Using GitHub CLI:

```bash
gh milestone create "Phase 1 - HCG and Abstract Pipeline" \
  --repo c-daly/logos \
  --description "Phase 1 deliverables: Formalize HCG and Abstract Pipeline. Includes Workstreams A, B, and C." \
  --due-date "2026-02-15"
```

### Using GitHub Web UI:

1. Navigate to: `https://github.com/c-daly/logos/milestones`
2. Click "New milestone"
3. Enter:
   - **Title**: Phase 1 - HCG and Abstract Pipeline
   - **Due date**: February 15, 2026 (or as appropriate)
   - **Description**: Phase 1 deliverables: Formalize HCG and Abstract Pipeline. Includes Workstreams A, B, and C.
4. Click "Create milestone"

## Step 3: Create GitHub Project Board

### Using GitHub Web UI:

1. Navigate to the repository: `https://github.com/c-daly/logos`
2. Click on the "Projects" tab
3. Click "New project"
4. Choose "Board" template
5. Name: "Project LOGOS - Phase 1"
6. Set visibility: Private or Public as appropriate
7. Click "Create"

### Configure Board Views:

Create the following views for the project board:

#### View 1: By Workstream
- Group by: Label (workstream:A, workstream:B, workstream:C)
- Sort by: Priority

#### View 2: By Component
- Group by: Label (component:sophia, component:hermes, component:talos, component:apollo, component:infrastructure)
- Sort by: Status

#### View 3: By Priority
- Filter: Priority labels
- Sort by: Created date

#### View 4: Weekly Progress (Table View)
- Columns: Title, Status, Assignees, Labels, Updated
- Filter: Updated in last 7 days

### Set Up Board Columns (if using Classic Project):

If using GitHub Projects (Classic):
1. Create columns: "To Do", "In Progress", "Blocked", "In Review", "Done"
2. Enable automation:
   - Newly added → To Do
   - Reopened → To Do
   - Closed → Done

## Step 4: Generate and Create Issues

Use the provided script to generate issues from the action items document:

### Generate GitHub CLI commands:

```bash
python .github/scripts/generate_issues.py --format gh-cli --output create_issues.sh
chmod +x create_issues.sh
./create_issues.sh
```

### Alternative: Generate JSON for review:

```bash
python .github/scripts/generate_issues.py --format json --output issues.json
```

Review `issues.json` and create issues manually or via API.

### Alternative: Generate Markdown summaries:

```bash
python .github/scripts/generate_issues.py --format markdown --output issues.md
```

## Step 5: Link Issues to Project Board

After creating issues:

### Using GitHub CLI:

```bash
# Get the project number (e.g., 1)
gh project list --repo c-daly/logos

# Add issues to project
gh project item-add <PROJECT_NUMBER> --repo c-daly/logos --issue <ISSUE_NUMBER>
```

### Using GitHub Web UI:

1. Open the Project Board
2. Click "+ Add item"
3. Search for and add each issue
4. Organize issues into appropriate columns/statuses

## Step 6: Set Up Weekly Progress Tracking

Create a recurring task or calendar reminder to:

1. Review all issues in "In Progress" status
2. Update issue status and labels
3. Comment on blocked issues with updates
4. Close completed issues
5. Create a weekly progress summary in Discussions or as a project note

### Optional: Create a GitHub Action for Weekly Reports

Create `.github/workflows/weekly-progress.yml`:

```yaml
name: Weekly Progress Report

on:
  schedule:
    # Run every Monday at 9:00 AM UTC
    - cron: '0 9 * * 1'
  workflow_dispatch:

jobs:
  weekly-report:
    runs-on: ubuntu-latest
    steps:
      - name: Generate Weekly Report
        uses: actions/github-script@v7
        with:
          script: |
            const { data: issues } = await github.rest.issues.listForRepo({
              owner: context.repo.owner,
              repo: context.repo.repo,
              state: 'open',
              labels: 'status:in-progress',
              sort: 'updated',
              direction: 'desc'
            });
            
            let report = '# Weekly Progress Report\n\n';
            report += `**Generated:** ${new Date().toISOString()}\n\n`;
            report += `## In Progress (${issues.length} issues)\n\n`;
            
            for (const issue of issues) {
              report += `- #${issue.number}: ${issue.title}\n`;
              report += `  - Assignees: ${issue.assignees.map(a => a.login).join(', ') || 'None'}\n`;
              report += `  - Labels: ${issue.labels.map(l => l.name).join(', ')}\n\n`;
            }
            
            console.log(report);
            
            // Optionally: Create a discussion post or issue comment with the report
```

## Step 7: Configure Issue Templates

Issue templates are already created in `.github/ISSUE_TEMPLATE/`. They will automatically appear when users create new issues.

Available templates:
- **Sophia Task** - For Sophia cognitive core tasks
- **Hermes Task** - For Hermes language utility tasks
- **Talos Task** - For Talos hardware abstraction tasks
- **Apollo Task** - For Apollo UI/client tasks
- **Infrastructure Task** - For infrastructure, HCG, and CI/CD tasks
- **Research Task** - For research sprints and investigations
- **Documentation Task** - For documentation tasks

## Maintenance and Best Practices

### Issue Management:
- Always assign issues to team members
- Use labels consistently
- Update issue status regularly
- Link related issues using keywords (fixes #, relates to #)
- Close issues only when acceptance criteria are met

### Project Board Management:
- Review board daily
- Update issue statuses as work progresses
- Use comments to track blockers and dependencies
- Archive completed sprints/phases

### Weekly Progress Tracking:
- Schedule a weekly sync meeting (e.g., Monday mornings)
- Review project board before the meeting
- Update `docs/action_items.md` to reflect completed tasks
- Adjust priorities based on current needs
- Document decisions in meeting notes

## Additional Resources

- [GitHub Projects Documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [GitHub Labels Documentation](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels)
- [GitHub Milestones Documentation](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/about-milestones)
- [GitHub Issue Templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/about-issue-and-pull-request-templates)

## Troubleshooting

### Labels not syncing
- Ensure you have admin permissions on the repository
- Verify the YAML syntax in `.github/labels.yml`
- Try using the GitHub web UI to create labels manually

### Script errors
- Ensure Python 3.6+ is installed
- Verify the path to `docs/action_items.md` is correct
- Check that the markdown syntax in action_items.md is valid

### Issues not appearing in project
- Verify the project is linked to the repository
- Check that issues have the correct labels
- Ensure automation rules are configured correctly

## Support

For questions or issues with the tracking system setup, please:
1. Check this documentation
2. Review existing issues and discussions
3. Create a new issue with the `component:infrastructure` label
