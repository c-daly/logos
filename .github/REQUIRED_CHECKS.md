# Required GitHub Status Checks

To ensure code quality and prevent issues from reaching main, configure these workflows as **required status checks** in repository settings.

## Setup Instructions

1. Go to: **Settings → Branches → Branch protection rules → main**
2. Enable: **Require status checks to pass before merging**
3. Add these required checks:

## Required Checks

### SDK Regeneration Check
- **Workflow:** `SDK Regeneration Check` (sdk-regen.yml)
- **Purpose:** Ensures SDKs are up-to-date with contract changes
- **Blocks:** PRs with stale SDK outputs
- **Fix:** Run `./scripts/generate-sdks.sh` locally and commit changes

### Standard CI
- **Workflow:** `CI` (ci.yml via reusable-standard-ci.yml)
- **Purpose:** Linting, type checking, tests, coverage
- **Blocks:** PRs with failing tests or lint errors

## Auto-Regeneration Workflow

The `Regenerate SDKs on Contract Changes` workflow (regenerate-sdks.yml) runs automatically when contracts change, but is **not** a required check. It:
- Auto-commits SDK updates to main on push
- Creates SDK-only PRs when triggered from pull requests
- Creates GitHub issues on failure for visibility

This two-tier approach means:
1. SDK regen failures are visible (via issues)
2. PRs can't merge with stale SDKs (via required check)
3. Manual intervention is only needed if auto-regen fails
