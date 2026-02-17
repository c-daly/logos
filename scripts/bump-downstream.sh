#!/usr/bin/env bash
# bump-downstream.sh — Update logos-foundry version across downstream repos
#
# Usage: ./scripts/bump-downstream.sh v0.4.3
#
# For each downstream repo (hermes, sophia, apollo, talos):
#   1. Updates pyproject.toml git tag reference
#   2. Updates Dockerfile FROM tag
#   3. Runs poetry lock
#   4. Creates a branch, commits, pushes, and opens a PR

set -euo pipefail

VERSION="${1:-}"
CI_TAG=""

# Parse arguments
shift || true
while [[ $# -gt 0 ]]; do
    case "$1" in
        --ci-tag)
            CI_TAG="${2:-}"
            if [[ -z "$CI_TAG" ]]; then
                echo "Error: --ci-tag requires a value (e.g. ci/v2)"
                exit 1
            fi
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ -z "$VERSION" ]]; then
    echo "Usage: $0 <version-tag> [--ci-tag <ci-tag>]"
    echo "  e.g. $0 v0.4.3"
    echo "  e.g. $0 v0.4.3 --ci-tag ci/v2"
    exit 1
fi

# Strip leading 'v' for Dockerfile tags (uses bare version)
BARE_VERSION="${VERSION#v}"

# Validate format
if ! [[ "$BARE_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: version must be semver (e.g. v0.4.3), got: $VERSION"
    exit 1
fi

# Verify the tag exists on the remote
if ! git ls-remote --tags https://github.com/c-daly/logos.git "refs/tags/$VERSION" | grep -q "$VERSION"; then
    echo "Error: tag $VERSION does not exist on c-daly/logos"
    echo "Create it first: git tag $VERSION && git push origin $VERSION"
    exit 1
fi

# Verify gh CLI is available
if ! command -v gh &>/dev/null; then
    echo "Error: gh CLI is required. Install with: brew install gh"
    exit 1
fi

WORKSPACE="$(cd "$(dirname "$0")/../.." && pwd)"
LOGOS_DIR="$WORKSPACE/logos"
BRANCH="chore/bump-foundry-${BARE_VERSION}"
REPOS=(hermes sophia apollo talos)

# Generate changelog from previous tag to this one
CHANGELOG=""
if [[ -d "$LOGOS_DIR" ]]; then
    cd "$LOGOS_DIR"
    PREV_TAG=$(git tag --sort=-version:refname | grep -E '^v[0-9]' | grep -v "^${VERSION}$" | head -1)
    if [[ -n "$PREV_TAG" ]]; then
        echo "=== Changelog: $PREV_TAG → $VERSION ==="
        # Group commits by type
        FEATS=$(git log "${PREV_TAG}..${VERSION}" --oneline --format='%s' 2>/dev/null | grep -E '^feat' | sed 's/^/- /' || true)
        FIXES=$(git log "${PREV_TAG}..${VERSION}" --oneline --format='%s' 2>/dev/null | grep -E '^fix' | sed 's/^/- /' || true)
        OTHERS=$(git log "${PREV_TAG}..${VERSION}" --oneline --format='%s' 2>/dev/null | grep -vE '^(feat|fix)' | sed 's/^/- /' || true)

        if [[ -n "$FEATS" ]]; then
            CHANGELOG+=$'\n'"### Features"$'\n'"$FEATS"$'\n'
            echo "$FEATS"
        fi
        if [[ -n "$FIXES" ]]; then
            CHANGELOG+=$'\n'"### Fixes"$'\n'"$FIXES"$'\n'
            echo "$FIXES"
        fi
        if [[ -n "$OTHERS" ]]; then
            CHANGELOG+=$'\n'"### Other"$'\n'"$OTHERS"$'\n'
            echo "$OTHERS"
        fi
        if [[ -z "$CHANGELOG" ]]; then
            CHANGELOG=$'\n'"No commits between $PREV_TAG and $VERSION."$'\n'
        fi
        echo ""
    fi
fi

echo "=== Pre-bump checklist ==="
echo "  1. Was $VERSION created via PR (not direct to main)?"
echo "  2. Has CI passed on the logos $VERSION tag?"
echo "  3. Have you checked downstream compatibility (torch, spacy, etc.)?"
if [[ -n "$CI_TAG" ]]; then
    echo "  4. Does the $CI_TAG tag exist on logos? (Will also update workflow refs)"
fi
echo ""
read -rp "Continue? [y/N] " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted."
    exit 0
fi

for REPO in "${REPOS[@]}"; do
    REPO_DIR="$WORKSPACE/$REPO"
    if [[ ! -d "$REPO_DIR" ]]; then
        echo "[$REPO] SKIP — directory not found at $REPO_DIR"
        continue
    fi

    echo ""
    echo "=== [$REPO] Bumping to $VERSION ==="
    cd "$REPO_DIR"

    # Ensure we're on a clean main
    if [[ -n "$(git status --porcelain)" ]]; then
        echo "[$REPO] SKIP — working tree is dirty"
        continue
    fi

    git checkout main
    git pull --ff-only

    # Create branch
    git checkout -b "$BRANCH"

    # Update pyproject.toml — logos-foundry tag reference
    CHANGED=false
    if grep -q 'c-daly/logos.git' pyproject.toml; then
        sed -i.bak -E "s|(c-daly/logos\.git.*tag\s*=\s*\")v[0-9]+\.[0-9]+\.[0-9]+\"|\1${VERSION}\"|g" pyproject.toml
        rm -f pyproject.toml.bak
        CHANGED=true
    fi

    # Update Dockerfile — FROM tag
    if [[ -f Dockerfile ]] && grep -q 'logos-foundry:' Dockerfile; then
        sed -i.bak -E "s|logos-foundry:[0-9]+\.[0-9]+\.[0-9]+|logos-foundry:${BARE_VERSION}|g" Dockerfile
        rm -f Dockerfile.bak
        CHANGED=true
    fi

    # Update workflow refs if --ci-tag provided
    if [[ -n "$CI_TAG" ]]; then
        for WF in .github/workflows/*.yml; do
            [[ -f "$WF" ]] || continue
            if grep -q 'c-daly/logos/.github/workflows/' "$WF"; then
                sed -i.bak -E "s|(c-daly/logos/\.github/workflows/[^@]+@)[^ ]+|\1${CI_TAG}|g" "$WF"
                rm -f "${WF}.bak"
                CHANGED=true
            fi
        done
    fi

    if [[ "$CHANGED" != "true" ]]; then
        echo "[$REPO] SKIP — no logos-foundry references found"
        git checkout main
        git branch -D "$BRANCH"
        continue
    fi

    # Regenerate lockfile
    echo "[$REPO] Running poetry lock..."
    poetry lock --no-update 2>/dev/null || poetry lock

    # Commit and push
    git add pyproject.toml poetry.lock Dockerfile
    if [[ -n "$CI_TAG" ]]; then
        git add .github/workflows/*.yml
    fi
    COMMIT_MSG="chore: bump logos-foundry to $VERSION"
    if [[ -n "$CI_TAG" ]]; then
        COMMIT_MSG="chore: bump logos-foundry to $VERSION, workflows to $CI_TAG"
    fi
    git commit -m "$COMMIT_MSG"
    git push -u origin "$BRANCH"

    # Open PR with changelog
    PR_BODY="Automated bump of logos-foundry dependency to $VERSION.

## Updates
- \`pyproject.toml\` git tag reference
- \`Dockerfile\` FROM tag
- \`poetry.lock\` regenerated"

    if [[ -n "$CI_TAG" ]]; then
        PR_BODY+=$'\n'"- Workflow refs updated to \`$CI_TAG\`"
    fi

    if [[ -n "$CHANGELOG" ]]; then
        PR_BODY+=$'\n\n'"## What changed in logos ($PREV_TAG → $VERSION)"
        PR_BODY+="$CHANGELOG"
    fi

    PR_BODY+=$'\n\n'"Created by \`scripts/bump-downstream.sh\`."

    PR_URL=$(gh pr create \
        --title "chore: bump logos-foundry to $VERSION" \
        --body "$PR_BODY" 2>&1)

    echo "[$REPO] PR: $PR_URL"
    git checkout main
done

echo ""
echo "=== Done ==="
echo "Review and merge the PRs above."
