# Testing and Using the GitHub Infrastructure

This guide explains how to test and use the updated GitHub issue/project infrastructure.

## What Was Fixed

The following issues were identified and resolved:

1. **Missing `component:logos` label** - Added to align with spec section 2.1 which lists LOGOS as the 5th component
2. **Missing `type:outreach` label** - Added to support outreach-related tasks
3. **Hardcoded repository references** - Scripts now use `$GITHUB_REPOSITORY` environment variable
4. **Poor error handling** - Workflows now gracefully handle existing labels/milestones
5. **No validation** - Created comprehensive validation script to test before deployment
6. **Label sync issues** - Created dedicated label sync workflow

## Validation Before Deployment

Before running any GitHub Actions workflows, you can validate the configuration locally:

```bash
# Run the validation script
bash .github/scripts/validate_infrastructure.sh
```

This script will:
- ✅ Validate YAML syntax in all configuration files
- ✅ Check for all required component labels (sophia, hermes, talos, apollo, logos, infrastructure)
- ✅ Verify workflow file syntax
- ✅ Test that Python scripts execute successfully
- ✅ Confirm scripts generate valid output
- ✅ Verify all labels referenced in scripts exist in labels.yml
- ✅ Check milestone references

**All tests must pass before proceeding to GitHub Actions.**

## Deployment Steps

### Step 1: Sync Labels (REQUIRED FIRST)

Labels must be created before issues can reference them.

**Option A: Using GitHub Actions UI**
1. Go to the "Actions" tab in your GitHub repository
2. Select "Sync Labels" from the workflow list
3. Click "Run workflow" button
4. Select the branch (usually `main` or your current branch)
5. Click "Run workflow" to execute
6. Wait for completion and check the workflow summary

**Option B: Using GitHub CLI**
```bash
gh workflow run sync-labels.yml
```

**Verify labels were created:**
```bash
gh label list --repo c-daly/logos
```

You should see all component labels including `component:logos`.

### Step 2: Create Project Board and Issues

After labels are synced, you can create the project board and issues.

**Using GitHub Actions UI:**
1. Go to the "Actions" tab
2. Select "Create Phase 1 Issues and Project Board"
3. Click "Run workflow"
4. Choose options:
   - ✅ Create milestones first: `true`
   - ✅ Create project board: `true`
5. Click "Run workflow"
6. Wait for completion (this may take several minutes)

**Using GitHub CLI:**
```bash
gh workflow run create-phase1-issues.yml \
  -f create_milestones=true \
  -f create_project=true
```

## What Gets Created

### Labels (31 total)
- **Component labels** (6): sophia, hermes, talos, apollo, logos, infrastructure
- **Priority labels** (3): high, medium, low
- **Type labels** (7): feature, bug, research, documentation, refactor, testing, outreach
- **Workstream labels** (3): A, B, C
- **Status labels** (4): blocked, in-progress, review, on-hold
- **Phase labels** (2): phase:1, phase:2
- **Special labels** (6): good-first-issue, help-wanted, question, duplicate, wontfix, dependencies

### Milestones (4)
- **M1: HCG Store & Retrieve** - Knowledge graph operational
- **M2: SHACL Validation** - Validation and language services operational
- **M3: Simple Planning** - Cognitive capabilities demonstrated
- **M4: Pick and Place** - End-to-end autonomous behavior

### Issues (65)
- **Epoch 1** (41 issues): Infrastructure & Knowledge Foundation
- **Epoch 2** (5 issues): Language & Perception Services
- **Epoch 3** (13 issues): Cognitive Core & Reasoning
- **Epoch 4** (6 issues): Integration & Demonstration

### Project Board
- GitHub Projects v2 board with custom fields
- Multiple views (by workstream, component, priority, etc.)
- Automated workflows

## Troubleshooting

### Workflow not visible in Actions tab
If you don't see the workflows in the Actions tab:
1. Make sure you're on the correct branch
2. Ensure workflow files are in `.github/workflows/`
3. Check that YAML syntax is valid
4. Verify you have appropriate repository permissions

### "Repository not available" in workflow dispatch
This was caused by hardcoded repository references. The fix:
- Scripts now use `$GITHUB_REPOSITORY` environment variable
- This is automatically set by GitHub Actions
- Works for any fork or repository

### Label already exists errors
The workflows now handle this gracefully:
- Labels are created OR updated (no error if they exist)
- Milestones are checked before creation
- Duplicate issues are not created

### Permission errors
Ensure the workflow has required permissions:
```yaml
permissions:
  issues: write
  contents: read
  repository-projects: write
```

### Script execution fails
Run the validation script first:
```bash
bash .github/scripts/validate_infrastructure.sh
```

If validation fails, check:
- Python 3.x is installed
- PyYAML is available (`pip install pyyaml`)
- File paths are correct
- YAML syntax is valid

## Verification After Deployment

### Verify Labels
```bash
# List all labels
gh label list --repo c-daly/logos

# Check specific label
gh label view "component:logos" --repo c-daly/logos
```

### Verify Milestones
```bash
# List milestones
gh milestone list --repo c-daly/logos
```

### Verify Issues
```bash
# List Phase 1 issues
gh issue list --label "phase:1" --repo c-daly/logos --limit 100

# Count issues by epoch
gh issue list --label "phase:1" --json title --jq 'length'
```

### Verify Project Board
1. Navigate to: https://github.com/c-daly/logos/projects
2. Click on "Project LOGOS - Phase 1"
3. Verify issues are added and organized

## Manual Testing (No GitHub Actions)

If you prefer not to use GitHub Actions, you can create everything manually:

### 1. Create labels manually
```bash
# Install gh-label extension
gh extension install heaths/gh-label

# Sync labels from file
gh label sync --repo c-daly/logos --file .github/labels.yml
```

### 2. Create milestones
```bash
gh milestone create "M1: HCG Store & Retrieve" \
  --repo c-daly/logos \
  --description "Knowledge graph operational. Neo4j + Milvus working, core ontology loaded, basic CRUD operations functional."

# Repeat for M2, M3, M4...
```

### 3. Generate and create issues
```bash
# Generate issue creation script
python3 .github/scripts/create_issues_by_epoch.py --format gh-cli --output /tmp/create_issues.sh
chmod +x /tmp/create_issues.sh

# Set repository environment variable
export GITHUB_REPOSITORY="c-daly/logos"

# Execute (creates all 65 issues)
bash /tmp/create_issues.sh
```

## Key Changes from Previous Versions

1. **Added `component:logos` label** - Now properly identifies LOGOS foundry tasks
2. **Added `type:outreach` label** - Supports community engagement tasks
3. **Repository references use environment variables** - No more hardcoded `c-daly/logos`
4. **Improved error handling** - Workflows continue even if resources exist
5. **Added validation script** - Test before deploying
6. **Dedicated label sync workflow** - Can be run independently
7. **Better documentation** - Clear steps and troubleshooting

## Support

If you encounter issues:
1. Run the validation script: `bash .github/scripts/validate_infrastructure.sh`
2. Check workflow logs in the Actions tab
3. Verify you have the required permissions
4. Create an issue with the `component:logos` label for help
