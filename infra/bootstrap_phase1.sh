#!/usr/bin/env bash
# Bootstrap the complete LOGOS Phase 1 tracking infrastructure from local CLI.
# Sources:
#   - docs/action_items.md (task inventory)
#   - docs/spec/project_logos_full.md (section references / milestones)
#   - .github/project_config.yml (board + milestone configuration)

set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)

REPO_SLUG=${REPO_SLUG:-c-daly/logos}
PROJECT_TITLE=${PROJECT_TITLE:-"Project LOGOS - Phase 1"}
PHASE_MILESTONE_TITLE=${PHASE_MILESTONE_TITLE:-"Phase 1 - HCG and Abstract Pipeline"}
PHASE_MILESTONE_DUE=${PHASE_MILESTONE_DUE:-"2026-02-15T00:00:00Z"}

OWNER_NAME=${REPO_SLUG%%/*}
REPO_NAME=${REPO_SLUG#*/}

TMP_SCRIPT=""
trap '[[ -n "$TMP_SCRIPT" && -f "$TMP_SCRIPT" ]] && rm -f "$TMP_SCRIPT"' EXIT

log() {
  printf '\n\033[1;34m[LOGOS]\033[0m %s\n' "$1"
}

die() {
  printf '\n\033[1;31m[LOGOS]\033[0m %s\n' "$1" >&2
  exit 1
}

require_cmd() {
  local cmd=$1
  command -v "$cmd" >/dev/null 2>&1 || die "Missing required command: $cmd"
}

log "Validating prerequisites"
for tool in gh jq python3; do
  require_cmd "$tool"
done

log "Repository target: $REPO_SLUG"

AVAILABLE_STEPS=(labels milestones project issues link)
REQUESTED_STEPS=()

usage() {
  cat <<USAGE
Usage: $(basename "$0") [step ...]

Steps:
  labels      Sync labels from .github/labels.yml
  milestones  Ensure milestones exist
  project     Create or locate the Project V2 board
  issues      Generate and create GitHub issues
  link        Add open phase:1 issues to the project board

If no steps are provided, the script runs all steps in the order above.
USAGE
}

if [[ $# -eq 0 ]]; then
  REQUESTED_STEPS=("${AVAILABLE_STEPS[@]}")
else
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h|--help)
        usage
        exit 0
        ;;
      labels|milestones|project|issues|link)
        REQUESTED_STEPS+=("$1")
        ;;
      *)
        usage
        die "Unknown step '$1'"
        ;;
    esac
    shift
  done
fi

urlencode() {
  python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$1"
}

sync_labels() {
  log "Syncing labels from .github/labels.yml"
  local labels_json
  labels_json=$(python3 - "$REPO_ROOT/.github/labels.yml" <<'PY'
import json
import sys

path = sys.argv[1]
labels = []
current = None

def flush():
    global current
    if current:
        if 'name' in current and 'color' in current:
            labels.append(current)
        current = None

with open(path, 'r', encoding='utf-8') as handle:
    for raw in handle:
        stripped = raw.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if stripped.startswith('- name:'):
            flush()
            value = stripped.split(':', 1)[1].strip().strip('"')
            current = {'name': value}
        elif current and stripped.startswith('color:'):
            value = stripped.split(':', 1)[1].strip().strip('"')
            current['color'] = value.lstrip('#')
        elif current and stripped.startswith('description:'):
            value = stripped.split(':', 1)[1].strip()
            if value.startswith('"') and value.endswith('"') and len(value) >= 2:
                value = value[1:-1]
            current['description'] = value
flush()

print(json.dumps(labels))
PY
)

  if [[ -z "$labels_json" || "$labels_json" == "[]" ]]; then
    die "No labels parsed from .github/labels.yml"
  fi

  echo "$labels_json" | jq -c '.[]' | while read -r label; do
    local name color description encoded
    name=$(echo "$label" | jq -r '.name')
    color=$(echo "$label" | jq -r '.color // "000000"')
    description=$(echo "$label" | jq -r '.description // ""')
    encoded=$(urlencode "$name")

    if gh api "repos/$REPO_SLUG/labels/$encoded" >/dev/null 2>&1; then
      gh api -X PATCH "repos/$REPO_SLUG/labels/$encoded" \
        -f new_name="$name" \
        -f color="$color" \
        -f description="$description" >/dev/null
      log "Updated label: $name"
    else
      gh api -X POST "repos/$REPO_SLUG/labels" \
        -f name="$name" \
        -f color="$color" \
        -f description="$description" >/dev/null
      log "Created label: $name"
    fi
  done
}

create_milestone() {
  local title=$1
  local description=$2
  local due_on=${3:-}
  local args=(-f title="$title" -f description="$description")
  if [[ -n "$due_on" ]]; then
    args+=(-f due_on="$due_on")
  fi

  if gh api "repos/$REPO_SLUG/milestones" -X POST "${args[@]}" >/dev/null 2>&1; then
    log "Created milestone: $title"
  else
    log "Milestone '$title' already exists or could not be created (continuing)"
  fi
}

ensure_milestones() {
  log "Ensuring Phase 1 milestones exist"
  create_milestone "$PHASE_MILESTONE_TITLE" \
    "Phase 1 deliverables from docs/spec/project_logos_full.md Section 7.1" \
    "$PHASE_MILESTONE_DUE"

  create_milestone "M1: HCG Store & Retrieve" \
    "Neo4j + Milvus operational, core ontology loaded, CRUD ready."
  create_milestone "M2: SHACL Validation" \
    "Validation + Hermes endpoints online per docs/action_items.md A2/A3/C1."
  create_milestone "M3: Simple Planning" \
    "Sophia cognitive loop (B1-B4) produces valid plans."
  create_milestone "M4: Pick and Place" \
    "End-to-end integration demo (B5 + Outreach tasks)."
}

lookup_project() {
  local repo_info owner_login owner_type owner_id repo_id
  repo_info=$(gh api graphql \
    -f owner="$OWNER_NAME" \
    -f name="$REPO_NAME" \
    -f query='query($owner: String!, $name: String!) {\n      repository(owner: $owner, name: $name) {\n        id\n        owner {\n          id\n          login\n          __typename\n        }\n      }\n    }')

  owner_login=$(echo "$repo_info" | jq -r '.data.repository.owner.login')
  owner_type=$(echo "$repo_info" | jq -r '.data.repository.owner.__typename')
  owner_id=$(echo "$repo_info" | jq -r '.data.repository.owner.id')
  repo_id=$(echo "$repo_info" | jq -r '.data.repository.id')

  local existing_id existing_number
  if [[ "$owner_type" == "Organization" ]]; then
    local org_projects
    org_projects=$(gh api graphql \
      -f login="$owner_login" \
      -f query='query($login: String!) {\n        organization(login: $login) {\n          projectsV2(first: 100) {\n            nodes { id number title }\n          }\n        }\n      }')
    existing_id=$(echo "$org_projects" | jq -r --arg title "$PROJECT_TITLE" \
      '.data.organization.projectsV2.nodes[]? | select(.title == $title) | .id' | head -n1)
    existing_number=$(echo "$org_projects" | jq -r --arg title "$PROJECT_TITLE" \
      '.data.organization.projectsV2.nodes[]? | select(.title == $title) | .number' | head -n1)
  else
    local user_projects
    user_projects=$(gh api graphql \
      -f login="$owner_login" \
      -f query='query($login: String!) {\n        user(login: $login) {\n          projectsV2(first: 100) {\n            nodes { id number title }\n          }\n        }\n      }')
    existing_id=$(echo "$user_projects" | jq -r --arg title "$PROJECT_TITLE" \
      '.data.user.projectsV2.nodes[]? | select(.title == $title) | .id' | head -n1)
    existing_number=$(echo "$user_projects" | jq -r --arg title "$PROJECT_TITLE" \
      '.data.user.projectsV2.nodes[]? | select(.title == $title) | .number' | head -n1)
  fi

  if [[ -n "$existing_id" ]]; then
    PROJECT_ID="$existing_id"
    PROJECT_NUMBER="$existing_number"
    log "Using existing project '$PROJECT_TITLE' (#$PROJECT_NUMBER)"
    return
  fi

  local create_resp
  create_resp=$(gh api graphql \
    -f ownerId="$owner_id" \
    -f repositoryId="$repo_id" \
    -f title="$PROJECT_TITLE" \
    -f query='mutation($ownerId: ID!, $repositoryId: ID!, $title: String!) {\n      createProjectV2(input: {\n        ownerId: $ownerId\n        repositoryId: $repositoryId\n        title: $title\n      }) {\n        projectV2 { id number title }\n      }\n    }')
  PROJECT_ID=$(echo "$create_resp" | jq -r '.data.createProjectV2.projectV2.id')
  PROJECT_NUMBER=$(echo "$create_resp" | jq -r '.data.createProjectV2.projectV2.number')
  log "Created project '$PROJECT_TITLE' (#$PROJECT_NUMBER)"
}

create_project_board() {
  lookup_project
}

create_issues() {
  log "Generating GitHub CLI issue commands from docs/action_items.md"
  TMP_SCRIPT=$(mktemp)
  python3 "$REPO_ROOT/.github/scripts/create_issues_by_epoch.py" \
    --format gh-cli \
    --repo "$REPO_SLUG" \
    > "$TMP_SCRIPT"
  chmod +x "$TMP_SCRIPT"

  log "Creating issues (this may take a while)"
  bash "$TMP_SCRIPT"
}

add_issues_to_project() {
  [[ -z "${PROJECT_ID:-}" ]] && die "Project ID missing"

  log "Linking phase:1 issues to project board"
  local issue_ids
  issue_ids=$(gh api graphql \
    -f owner="$OWNER_NAME" \
    -f name="$REPO_NAME" \
    -f query='query($owner: String!, $name: String!) {\n      repository(owner: $owner, name: $name) {\n        issues(first: 100, labels: ["phase:1"], states: OPEN) {\n          nodes { id number title }\n        }\n      }\n    }' --jq '.data.repository.issues.nodes[]?.id')

  if [[ -z "$issue_ids" ]]; then
    log "No open phase:1 issues detected; skipping project linking"
    return
  fi

  while IFS= read -r issue_id; do
    [[ -z "$issue_id" ]] && continue
    gh api graphql \
      -f projectId="$PROJECT_ID" \
      -f contentId="$issue_id" \
      -f query='mutation($projectId: ID!, $contentId: ID!) {\n        addProjectV2ItemById(input: { projectId: $projectId, contentId: $contentId }) {\n          item { id }\n        }\n      }' >/dev/null 2>&1 || echo "Issue $issue_id already linked or could not be added"
  done <<< "$issue_ids"

  log "All phase:1 issues linked to project"
}

main() {
  for step in "${REQUESTED_STEPS[@]}"; do
    case "$step" in
      labels)
        sync_labels
        ;;
      milestones)
        ensure_milestones
        ;;
      project)
        create_project_board
        ;;
      issues)
        create_issues
        ;;
      link)
        add_issues_to_project
        ;;
    esac
  done

  log "Bootstrap complete!"
  cat <<SUMMARY
Next steps:
  • Review the '${PROJECT_TITLE}' board → https://github.com/${REPO_SLUG}/projects
  • Verify milestones in https://github.com/${REPO_SLUG}/milestones
  • Use docs/PHASE1_ISSUES.md for the epoch/acceptance criteria overview.
SUMMARY
}

main "$@"
