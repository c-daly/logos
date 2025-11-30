# Project LOGOS Documentation

This repository is the canonical source of architecture and process docs for the LOGOS ecosystem. The `docs/` tree is organized by concern rather than chronology.

---

## Directory Structure

| Directory | Purpose |
|-----------|----------|
| `architecture/` | System specs and phase specifications |
| `adr/` | Architecture Decision Records |
| `hcg/` | Hybrid Cognitive Graph ontology, CWM schemas |
| `operations/` | CI/CD, testing, verification, demos, observability |
| `sdk/` | SDK installation and usage guides |
| `api/` | Generated API docs (GitHub Pages) |
| `outreach/` | Blog posts, papers, marketing materials |
| `research/` | Academic research and paper drafts |

---

## Service Documentation

Each service maintains its own documentation in its repository:

| Service | Repository | Key Docs |
|---------|------------|----------|
| **Sophia** | [c-daly/sophia](https://github.com/c-daly/sophia) | `docs/API_SERVICE_SUMMARY.md`, `docs/JEPA_SIMULATION.md` |
| **Hermes** | [c-daly/hermes](https://github.com/c-daly/hermes) | `docs/MILVUS_INTEGRATION.md`, `DOCKER.md` |
| **Apollo** | [c-daly/apollo](https://github.com/c-daly/apollo) | `webapp/README.md`, `docs/WEBSOCKET_PROTOCOL.md`, `docs/PERSONA_DIARY.md` |
| **Talos** | [c-daly/talos](https://github.com/c-daly/talos) | `docs/FIXTURES.md`, `docs/INTEGRATION_TESTING.md` |

For implementation details, always refer to the service repository. This meta-repo contains:
- Cross-cutting architecture specs (`architecture/`)
- Operational procedures and verification (`operations/`)
- Shared contracts and SDKs (`contracts/`, `sdk/`)

---

## Key Documents

### Architecture
- [LOGOS Specification](architecture/LOGOS_SPEC.md) - Core architecture, philosophy, and phase roadmap
- [Phase 2 Specification](architecture/PHASE2_SPEC.md) - Services, Apollo UX, CWM State contract
- [Phase 3 Specification](architecture/PHASE3_SPEC.md) - Learning & Memory (planned)

### Operations
- [Developer Onboarding](operations/DEV_ONBOARDING.md) - Fast start for local dev and CI parity
- [Testing Documentation](operations/TESTING.md) - Standards and strategy
- [CI/CD Documentation](operations/ci/README.md) - Workflows and templates
- [Phase 2 Verification](operations/PHASE2_VERIFY.md) - Milestone checklists
- [Observability Queries](operations/OBSERVABILITY_QUERIES.md) - TraceQL examples

### HCG / Ontology
- [CWM State Specification](hcg/CWM_STATE.md) - Unified world model contract

### SDK
- [SDK Documentation](sdk/README.md) - Python & TypeScript client libraries

---

## Authoring Guidelines

1. **Single source of truth**: Keep substantive content here; service READMEs should summarize and link.
2. **No ticket-only docs**: If a document restates an issue, convert it to a checklist in the issue or delete it.
3. **Cross-repo documentation**: For service specifics, document in that repo's `docs/` folder.
4. **Metadata**: Include ownership, last verified date, and related issues in document headers.

---

## Contributing

When adding documentation:

1. Choose the appropriate directory based on content type
2. Follow existing formatting conventions
3. Update this README if adding a new key document
4. Link from related documents for discoverability

For questions about documentation structure, open an issue with the `documentation` label.
