# Documentation Manifest

What LOGOS documentation should look like after cleanup.

## Ecosystem Docs (live in `logos/docs/`)

These are the authoritative references for cross-repo concerns. Every repo links here instead of duplicating.

| Document | Status | Purpose |
|----------|--------|---------|
| `ARCHITECTURE.md` | **NEW** | System overview, dependency graph, local vs CI, port scheme, service APIs |
| `LOCAL_SETUP.md` | **NEW** | Fresh machine → running stack. Replaces stale `LOCAL_DEVELOPMENT.md` |
| `WHY.md` | **NEW** | FAQ for new developers: why 5 repos, why Docker, why two port schemes, etc. |
| `TESTING.md` | **REWRITE** | Testing strategy: unit/integration/e2e, what needs infra, test stack usage. Replace `operations/TESTING.md` |
| `CI_CD.md` | **NEW** | Reusable workflow, container publishing, how to debug CI. Currently undocumented |
| `OBSERVABILITY.md` | **KEEP** | OTel setup, traces, metrics. Existing `observability/` content is decent |
| `operations/PACKAGE_PUBLISHING.md` | **REWRITTEN** | Release checklist, version alignment, bump script, CI workflow versioning. Replaces stale original |

### To Delete from `logos/docs/`

| Path | Reason |
|------|--------|
| `architecture/ARCHITECTURE.md` | Replaced by `ARCHITECTURE.md` |
| `architecture/PHASE1_SPEC.md` | Archive to Obsidian |
| `architecture/PHASE2_SPEC.md` | Archive to Obsidian |
| `architecture/PHASE3_SPEC.md` | Archive to Obsidian |
| `operations/PORT_REFERENCE.md` | Replaced by port section in `ARCHITECTURE.md` |
| `operations/PHASE2_VERIFY.md` | Archive to Obsidian |
| `LOCAL_DEVELOPMENT.md` | Replaced by `LOCAL_SETUP.md` |
| `scratch/` | Move useful bits to Obsidian, delete rest |
| `plans/` | Move to Obsidian |
| `evidence/` | Move to Obsidian |
| `*.json` queue files | Runtime artifacts, not documentation |

### To Rename/Update

| Item | Change |
|------|--------|
| `logos_config/README.md` | Fix wrong port example (59530), clarify shared infra. Note: this file also has offset-port confusion — it shows CI test-stack ports without clarifying they differ from local dev shared ports. |
| `.github/workflows/phase1-gate.yml` | Rename to `gate-check.yml` or remove if unused |
| `.github/workflows/phase2-e2e.yml` | Rename to `e2e-integration.yml` |
| `.github/workflows/phase2-perception.yml` | Rename to `perception-tests.yml` |
| `.github/workflows/phase2-otel.yml` | Rename to `otel-smoke.yml` |
| `.github/labels.yml` | Remove `phase:1`, `phase:2` labels |
| Docker container names | `logos-phase2-test-*` → `logos-test-*` |

## Per-Repo Docs

Every repo should have exactly these files in its root:

### README.md (slim)
- 1-2 sentence description
- Prerequisites (link to `logos/docs/LOCAL_SETUP.md` for full setup)
- `poetry install && poetry run pytest` quick start
- Link to ecosystem docs for everything else
- NO port tables, NO architecture diagrams, NO phase references

### AGENTS.md (repo-specific)
- Directory structure
- Key modules and what they do
- Coding conventions specific to this repo
- Issue labels (remove phase labels)
- Testing expectations
- NO port values (link to `logos_config`)

### CLAUDE.md (pointer)
- Links to AGENTS.md and issue templates
- Already correct in most repos, just verify

### .env.example (auto-documented)
- Correct default values for local dev (shared infra ports)
- Comments on every line explaining the value
- NO test-stack offset ports

### Per-Repo Cleanup

**apollo:**
- Delete stale `.env.example` (has ports 8080/8082)
- Fix `.env.test`: `NEO4J_URI=bolt://neo4j:27687` → `bolt://neo4j:7687` (inside the Docker network, containers use service names and internal ports — not host-mapped offset ports)
- Slim README.md
- Remove phase references from `tests/e2e/test_e2e_flow.py` comment

**sophia:**
- Delete/archive root `docker-compose.yml` (stale, not used in CI)
- Move `docs/research/` to Obsidian
- Slim README.md (remove port table or link to ARCHITECTURE.md)
- Remove phase references from test comments

**hermes:**
- ~~Fix Dockerfile: base image~~ — done (now on foundry v0.4.2 via PR #80)
- Fix `.env.example`: `MILVUS_PORT=17530` → `19530`
- Fix `.env.test`: `MILVUS_PORT=29530` → `19530` (shared port) or `17530` (hermes test offset). `29530` is incorrect — hermes prefix is 1xxxx, not 2xxxx.
- Remove "Phase 2 Testing" from `tests/hermes/__init__.py` and `tests/README.md`
- Slim README.md

**talos:**
- Fix README.md: remove `docker run -p 8002:8002` (Talos is a Library / Service — it has a runtime for hardware abstraction, but the Docker example is stale)
- Remove "Phase 1 simplification" comments from source code
- Fix `docs/FIXTURES.md` circular reference

## What Should NOT Be Documentation

- Port values → read from `logos_config/ports.py`
- Phase specs → Obsidian vault
- Research notes → Obsidian vault
- PoC summaries → Obsidian vault
- Plans and design docs → Obsidian vault
- Anything that duplicates code behavior
