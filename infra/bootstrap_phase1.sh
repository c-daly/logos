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

if ! gh label --help >/dev/null 2>&1; then
  die "The gh-label extension is required. Install via: gh extension install heaths/gh-label"
fi

log "Repository target: $REPO_SLUG"

sync_labels() {
  log "Syncing labels from .github/labels.yml"
  gh label sync --repo "$REPO_SLUG" --file "$REPO_ROOT/.github/labels.yml"
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
  sync_labels
  ensure_milestones
  create_project_board
  create_issues
  add_issues_to_project

  log "Bootstrap complete!"
  cat <<SUMMARY
Next steps:
  • Review the '${PROJECT_TITLE}' board → https://github.com/${REPO_SLUG}/projects
  • Verify milestones in https://github.com/${REPO_SLUG}/milestones
  • Use docs/PHASE1_ISSUES.md for the epoch/acceptance criteria overview.
SUMMARY
}

main "$@"
