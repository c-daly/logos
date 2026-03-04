# Git & Project Standards

Standards for branch naming, commits, and PR hygiene across all LOGOS repos.

---

## Branch Naming

### Format

```
<type>/<repo><ticket>-<short-description>
```

**With a ticket:**
```
feat/logos42-add-shacl-validation
fix/sophia131-memory-leak-in-planner
chore/hermes88-bump-foundry
```

**Without a ticket** (rare — most work should have an issue):
```
chore/update-deps
docs/fix-readme-links
```

### Types

| Type | Use for |
|------|---------|
| `feat` | New features or capabilities |
| `fix` | Bug fixes |
| `chore` | Maintenance, deps, tooling |
| `refactor` | Code restructuring (no behavior change) |
| `docs` | Documentation only |
| `test` | Test additions or fixes |
| `ci` | CI/CD pipeline changes |

### Rules

- All lowercase, kebab-case for description
- Repo prefix matches the GitHub repo name: `logos`, `sophia`, `hermes`, `talos`, `apollo`
- Ticket number directly follows repo name with no separator: `logos42`, not `logos-42`
- Description should be 2-5 words, descriptive enough to identify the work
- CI will warn on non-conforming branch names (enforced via `reusable-pr-checks.yml`)

---

## Commit Messages

### Format

```
<type>: <short summary>

<optional body — explain why, not what>
```

### Rules

- Imperative mood: "add validation" not "added validation"
- First line under 72 characters
- One logical change per commit
- No emoji in commit messages
- No attribution lines except `Co-Authored-By` when applicable

---

## Pull Requests

### Requirements

- Every PR must reference an issue (`Closes #N`, `Fixes #N`, `Resolves #N`, or `See #N`)
- Use the PR template (auto-populated from `.github/PULL_REQUEST_TEMPLATE.md`)
- PR title matches commit format: `<type>: <short summary>`
- CI must pass before merge

### Labels

| Label | Color | Use for |
|-------|-------|---------|
| `deferred` | gray | Work postponed to a future milestone |
| `needs-triage` | yellow | Needs prioritization and assignment |
| `blocked` | red | Blocked by external dependency or decision |
