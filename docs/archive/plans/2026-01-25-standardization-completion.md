# LOGOS Standardization Completion Plan

**Created:** 2026-01-25
**Status:** Active
**Context:** Audit revealed closed tickets don't match code reality. This plan closes the gap.

---

## Phase 1: Structural Fixes (18 tasks)

These fix the actual broken standardization - mismatched dependencies, hardcoded values, missing adoption.

### 1. LOGOS Internal Fixes

#### 1.1 Fix e2e fixtures to use logos_config
- **File:** `logos/tests/e2e/fixtures.py`
- **Problem:** Hardcoded `8001`, `8002`, `8003` defaults
- **Fix:** Import from logos_config:
  ```python
  from logos_config.ports import get_repo_ports
  SOPHIA_PORT = os.getenv("SOPHIA_PORT", str(get_repo_ports("sophia").api))
  ```

#### 1.2 Fix e2e test file port references
- **File:** `logos/tests/e2e/test_phase2_end_to_end.py` (lines 74-76)
- **Problem:** Same hardcoded ports as fixtures
- **Fix:** Use fixtures properly or import from logos_config

---

### 2. HERMES Fixes

#### 2.1 Fix hardcoded ports in env.py
- **File:** `hermes/src/hermes/env.py`
- **Problem:** Hardcoded `"17530"` (Milvus) and `"17687"` (Neo4j bolt)
- **Fix:** Use `get_repo_ports("hermes")` from logos_config

#### 2.2 Fix hardcoded port in main.py
- **File:** `hermes/src/hermes/main.py` (line ~850)
- **Problem:** Default port `"8080"` hardcoded
- **Fix:** Use logos_config or document as intentional container-internal port

#### 2.3 Migrate test fixtures to logos_test_utils
- **File:** `hermes/tests/conftest.py` (301 lines)
- **Problem:** Local `neo4j_driver`, `milvus_connection` fixtures duplicate logos_test_utils
- **Fix:** Import from `logos_test_utils.fixtures`, remove duplicates, keep hermes-specific only

#### 2.4 Convert pyproject.toml to pure Poetry format
- **File:** `hermes/pyproject.toml`
- **Problem:** Hybrid `[project]` + `[tool.poetry]` sections (non-standard)
- **Fix:** Remove `[project]` section, use only `[tool.poetry]` format

#### 2.5 Declare logos_test_utils dependency
- **File:** `hermes/pyproject.toml`
- **Problem:** Uses logos_test_utils without declaring it
- **Fix:** Add explicit dependency or document that it comes via logos-foundry

---

### 3. SOPHIA Fixes

#### 3.1 Declare logos_test_utils dependency
- **File:** `sophia/pyproject.toml`
- **Problem:** Uses `setup_logging` but doesn't declare dependency
- **Fix:** Add explicit dependency or document inheritance from logos-foundry

#### 3.2 Pin logos-foundry to version tag
- **File:** `sophia/pyproject.toml`
- **Problem:** `branch = "main"` (floating, breaks silently)
- **Fix:** Pin to specific tag (e.g., `@v0.3.0`)

#### 3.3 Add setup-local-dev.sh script
- **File:** `sophia/scripts/setup-local-dev.sh` (create)
- **Problem:** Manual setup required, no script exists
- **Fix:** Create script:
  ```bash
  #!/bin/bash
  set -e
  poetry install --with dev
  pip install -e ../logos
  echo "Local dev setup complete. Verify: poetry run pip show logos-foundry"
  ```

---

### 4. APOLLO Fixes

#### 4.1 Actually adopt logos_test_utils
- **Files:** `apollo/src/apollo/*.py` (relevant files)
- **Problem:** Zero imports despite ticket #120 being closed
- **Fix:** Import `setup_logging` and other utilities where appropriate

#### 4.2 Declare logos_test_utils dependency
- **File:** `apollo/pyproject.toml`
- **Problem:** Not declared
- **Fix:** Add explicit dependency

#### 4.3 Pin logos-foundry and SDKs to version tags
- **File:** `apollo/pyproject.toml`
- **Problem:** All three deps use `branch = "main"` (floating)
- **Fix:** Pin all to specific tags

#### 4.4 Add setup-local-dev.sh script
- **File:** `apollo/scripts/setup-local-dev.sh` (create)
- **Problem:** Only has `pyproject.local.toml` template (manual)
- **Fix:** Create automated script matching hermes/sophia pattern

---

### 5. TALOS Fixes

#### 5.1 Add CLAUDE.md
- **File:** `talos/CLAUDE.md` (create)
- **Problem:** Only repo without CLAUDE.md
- **Fix:** Create from template matching other repos

#### 5.2 Add logos-foundry dependency
- **File:** `talos/pyproject.toml`
- **Problem:** Standalone, inconsistent with other repos
- **Fix:** Add logos-foundry dependency for logos_config and logos_test_utils access

#### 5.3 Add CI trigger for develop branch
- **File:** `talos/.github/workflows/ci.yml`
- **Problem:** Only triggers on `main`, others trigger on `main` + `develop`
- **Fix:** Add `develop` to branch triggers

---

## Phase 2: Polish (7 tasks)

These improve consistency but aren't structurally broken. Do after Phase 1.

### 6. Code Style Standardization

#### 6.1 Standardize line length to 88
- **File:** `logos/pyproject.toml`
- **Change:** `line-length = 100` → `88`
- **Impact:** Requires reformatting logos codebase with black/ruff

#### 6.2 Standardize mypy strictness
- **File:** `logos/pyproject.toml`
- **Change:** `disallow_untyped_defs = false` → `true`
- **Impact:** Requires adding type hints to untyped functions

#### 6.3 Standardize coverage thresholds
- **Files:** All `pyproject.toml` files
- **Current:** talos=95%, hermes=60%, apollo=50%, logos/sophia=none
- **Change:** Pick consistent threshold (60-70%) for all

---

### 7. CI/Infrastructure Polish

#### 7.1 Migrate logos publish workflow to reusable template
- **File:** `logos/.github/workflows/publish-package.yml`
- **Problem:** Custom implementation while others use reusable-publish.yml
- **Fix:** Migrate to reusable workflow

#### 7.2 Add .dockerignore to all repos
- **Files:** Create in logos, sophia, apollo, talos
- **Problem:** Only hermes has .dockerignore
- **Fix:** Create matching files

---

### 8. Documentation

#### 8.1 Update TESTING_STANDARDS.md
- **File:** `logos/docs/TESTING_STANDARDS.md`
- **Add:**
  - logos_test_utils as canonical fixture source
  - How to import shared fixtures
  - Port scheme explanation (container-internal vs host-mapped)

#### 8.2 Document local dev architecture
- **File:** `logos/docs/LOCAL_DEVELOPMENT.md` (create or update)
- **Add:**
  - Git deps for local dev, containers for CI
  - setup-local-dev.sh workflow for each repo
  - Port schemes and when to use which

---

## Execution Order

```
Phase 1 (Structural):
  1. Logos e2e fixtures (1.1, 1.2) - unblocks cross-repo testing
  2. Hermes (2.1-2.5) - most broken, 5 tasks
  3. Apollo (4.1-4.4) - ticket was false, 4 tasks
  4. Sophia (3.1-3.3) - 3 tasks
  5. Talos (5.1-5.3) - 3 tasks

Phase 2 (Polish):
  6. Code style (6.1-6.3)
  7. CI polish (7.1-7.2)
  8. Documentation (8.1-8.2)
```

---

## Verification Checklist

After completion, verify:

```bash
# All repos import logos_test_utils (not just setup_logging)
grep -r "from logos_test_utils" */src/

# All repos declare dependency
grep -l "logos.test" */pyproject.toml

# All repos pinned to tags (no branch = "main")
grep -r 'branch = "main"' */pyproject.toml  # Should return nothing

# No hardcoded ports in hermes
grep -n "17530\|17687\|8080" hermes/src/hermes/*.py  # Should return nothing or documented

# All repos have CLAUDE.md
ls */CLAUDE.md

# All repos have setup-local-dev.sh
ls */scripts/setup-local-dev.sh
```

---

## Related Tickets

These open tickets should be reviewed after Phase 1:
- logos#420 - Standardize testing infrastructure
- logos#433 - Standardize config/env helpers
- logos#436 - Standardize pytest configuration

Either close as completed by this work, or update scope.

---

## Audit Trail

This plan was created based on a comprehensive audit that compared:
- 93 standardization-related GitHub issues (14 open, 79 closed)
- Actual code state across all 5 repos (logos, sophia, hermes, apollo, talos)

Key finding: Multiple closed tickets (hermes#50, apollo#120, hermes#55/56/60) do not match code reality. The infrastructure was built but adoption was incomplete, then partially scrambled by an agent intervention during a conda/poetry conflict.
