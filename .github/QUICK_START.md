# Quick Start: GitHub Infrastructure Setup

## 🚀 Quick Setup (3 Steps)

### Prerequisites
- Admin access to the `c-daly/logos` repository
- GitHub Actions enabled

### Step 1: Validate Configuration (Optional but Recommended)
```bash
# Run locally to verify everything is configured correctly
bash .github/scripts/validate_infrastructure.sh
```

You should see:
```
✅ All tests passed!
Infrastructure validation complete. The configuration is ready to use.
```

### Step 2: Sync Labels (REQUIRED - Do This First!)
Go to: **Actions → Sync Labels → Run workflow**

This creates all 31 labels including:
- ✅ `component:logos` (the missing label!)
- ✅ `component:sophia`, `component:hermes`, `component:talos`, `component:apollo`
- ✅ All priority, type, workstream, and status labels

### Step 3: Create Project Board & Issues
Go to: **Actions → Create Phase 1 Issues and Project Board → Run workflow**

Options:
- ✅ Create milestones first: `true`
- ✅ Create project board: `true`

This creates:
- ✅ 4 milestones (M1-M4)
- ✅ 65 issues organized by epochs
- ✅ GitHub Project board

## ✅ What's Fixed

| Issue | Status | Fix |
|-------|--------|-----|
| Missing `component:logos` label | ✅ Fixed | Added to labels.yml with color `7b68ee` |
| Missing `type:outreach` label | ✅ Fixed | Added to labels.yml |
| Repository not selectable in Actions | ✅ Fixed | Scripts now use `$GITHUB_REPOSITORY` |
| Scripts fail if labels missing | ✅ Fixed | Workflow syncs labels before creating issues |
| Can't test before deploying | ✅ Fixed | Created validation script |
| No dedicated label sync | ✅ Fixed | Created sync-labels.yml workflow |

## 📊 What Gets Created

### Labels (31 total)
```
component:sophia     component:hermes    component:talos
component:apollo     component:logos     component:infrastructure
priority:high        priority:medium     priority:low
type:feature         type:bug            type:research
type:documentation   type:refactor       type:testing
type:outreach        workstream:A        workstream:B
workstream:C         status:blocked      status:in-progress
status:review        status:on-hold      phase:1
phase:2              good-first-issue    help-wanted
question             duplicate           wontfix
dependencies
```

### Milestones (4)
- M1: HCG Store & Retrieve
- M2: SHACL Validation
- M3: Simple Planning
- M4: Pick and Place

### Issues (65)
- Epoch 1: Infrastructure & Knowledge Foundation (41)
- Epoch 2: Language & Perception Services (5)
- Epoch 3: Cognitive Core & Reasoning (13)
- Epoch 4: Integration & Demonstration (6)

## 🔧 Troubleshooting

### Problem: Workflow not showing in Actions tab
**Solution:** Make sure you're viewing the correct branch where the workflow files exist.

### Problem: "Repository not available" when running workflow
**Solution:** This was fixed! Scripts now use environment variables instead of hardcoded repo names.

### Problem: Labels already exist errors
**Solution:** Workflows now handle this gracefully - they update existing labels instead of failing.

### Problem: Want to test without creating real issues
**Solution:** Run the validation script locally:
```bash
bash .github/scripts/validate_infrastructure.sh
```

## 📚 Full Documentation

- **Detailed Guide:** See [TESTING_GUIDE.md](.github/TESTING_GUIDE.md)
- **Project Setup:** See [PROJECT_BOARD_SETUP.md](.github/PROJECT_BOARD_SETUP.md)
- **Infrastructure Overview:** See [README.md](.github/README.md)

## 🎯 Verification

After running the workflows, verify everything was created:

```bash
# Check labels (should show 31)
gh label list --repo c-daly/logos | wc -l

# Verify component:logos exists
gh label view "component:logos" --repo c-daly/logos

# Check milestones (should show 4)
gh milestone list --repo c-daly/logos

# Count Phase 1 issues (should show 65)
gh issue list --label "phase:1" --repo c-daly/logos --limit 100 | wc -l

# View project board
# Navigate to: https://github.com/c-daly/logos/projects
```

## 💡 Key Improvements

1. **Added missing labels** - Now includes `component:logos` and `type:outreach`
2. **No more hardcoded repos** - Works with any fork or repository
3. **Pre-deployment validation** - Test before creating resources
4. **Better error handling** - Gracefully handles existing resources
5. **Dedicated workflows** - Separate label sync for better control
6. **Comprehensive testing** - Validation script checks everything

## 🆘 Need Help?

1. Run validation: `bash .github/scripts/validate_infrastructure.sh`
2. Check workflow logs in the Actions tab
3. See [TESTING_GUIDE.md](.github/TESTING_GUIDE.md) for detailed troubleshooting
4. Create an issue with `component:logos` label
