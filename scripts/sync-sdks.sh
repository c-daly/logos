#!/bin/bash
# sync-sdks.sh - Sync generated SDKs from logos to downstream repos
#
# This script copies the generated SDK packages from logos/sdk/python/
# to their vendored locations in downstream repos (sophia, hermes, etc.)
#
# Usage:
#   ./scripts/sync-sdks.sh [--dry-run] [sophia|hermes|all]
#
# The SDKs are generated from OpenAPI contracts in logos/contracts/
# using the generate-sdks.sh script (or the regenerate-sdks.yml workflow).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGOS_ROOT="$(dirname "$SCRIPT_DIR")"
WORKSPACE_ROOT="$(dirname "$LOGOS_ROOT")"

# SDK source locations (in logos)
SOPHIA_SDK_SRC="$LOGOS_ROOT/sdk/python/sophia/logos_sophia_sdk"
HERMES_SDK_SRC="$LOGOS_ROOT/sdk/python/hermes/logos_hermes_sdk"

# SDK destination locations (in downstream repos)
SOPHIA_SDK_DEST="$WORKSPACE_ROOT/sophia/src/logos_sophia_sdk"
HERMES_SDK_DEST="$WORKSPACE_ROOT/hermes/src/logos_hermes_sdk"

DRY_RUN=false
TARGET="all"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        sophia|hermes|all)
            TARGET="$1"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--dry-run] [sophia|hermes|all]"
            echo ""
            echo "Sync generated SDKs from logos to downstream repos."
            echo ""
            echo "Options:"
            echo "  --dry-run    Show what would be copied without making changes"
            echo "  sophia       Sync only the Sophia SDK"
            echo "  hermes       Sync only the Hermes SDK"
            echo "  all          Sync all SDKs (default)"
            echo ""
            echo "Examples:"
            echo "  $0                    # Sync all SDKs"
            echo "  $0 sophia             # Sync only Sophia SDK"
            echo "  $0 --dry-run all      # Preview what would be synced"
            exit 0
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

sync_sdk() {
    local name="$1"
    local src="$2"
    local dest="$3"

    echo "=== Syncing $name SDK ==="
    echo "  Source: $src"
    echo "  Dest:   $dest"

    if [[ ! -d "$src" ]]; then
        echo "  ⚠️  Source directory does not exist, skipping"
        return 0
    fi

    if [[ ! -d "$(dirname "$dest")" ]]; then
        echo "  ⚠️  Destination parent directory does not exist, skipping"
        return 0
    fi

    if $DRY_RUN; then
        echo "  [DRY RUN] Would sync the following files:"
        # Show what would be copied (excluding __pycache__)
        find "$src" -type f ! -path "*/__pycache__/*" | while read -r f; do
            rel="${f#$src/}"
            echo "    $rel"
        done
    else
        # Remove existing destination (except __pycache__)
        if [[ -d "$dest" ]]; then
            echo "  Cleaning destination..."
            find "$dest" -type f ! -path "*/__pycache__/*" -delete
            # Remove empty directories except __pycache__
            find "$dest" -type d -empty ! -name "__pycache__" -delete 2>/dev/null || true
        fi

        # Copy new files (excluding __pycache__)
        echo "  Copying files..."
        mkdir -p "$dest"
        rsync -av --exclude='__pycache__' "$src/" "$dest/"
        
        echo "  ✅ $name SDK synced successfully"
    fi
    echo ""
}

echo "SDK Sync Tool"
echo "============="
echo "Logos root: $LOGOS_ROOT"
echo "Workspace:  $WORKSPACE_ROOT"
echo "Target:     $TARGET"
echo "Dry run:    $DRY_RUN"
echo ""

case $TARGET in
    sophia)
        sync_sdk "Sophia" "$SOPHIA_SDK_SRC" "$SOPHIA_SDK_DEST"
        ;;
    hermes)
        sync_sdk "Hermes" "$HERMES_SDK_SRC" "$HERMES_SDK_DEST"
        ;;
    all)
        sync_sdk "Sophia" "$SOPHIA_SDK_SRC" "$SOPHIA_SDK_DEST"
        sync_sdk "Hermes" "$HERMES_SDK_SRC" "$HERMES_SDK_DEST"
        ;;
esac

if $DRY_RUN; then
    echo "This was a dry run. No files were modified."
else
    echo "SDK sync complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Review the changes in the downstream repos"
    echo "  2. Commit the SDK updates to the downstream repos"
fi
