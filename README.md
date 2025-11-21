# Project LOGOS Documentation Guide

This repository is the canonical source of architecture and process docs for the LOGOS ecosystem. Recent work showed our content was scattered across `docs/phase2/*`, individual repo READMEs, and files that simply restated issue descriptions. This guide consolidates expectations for where documentation belongs and how new content should be organized.

## Canonical Layout

The `docs/` tree is organized by concern rather than chronology. Each folder should contain an `index.md` (or README) that links to child docs.

| Directory | Purpose | Typical Content |
| --- | --- | --- |
| `docs/architecture/` | End-to-end system overviews, diagrams, ADR summaries. | System maps, glossary, non-repo-specific ADRs. |
| `docs/hcg/` | Hybrid Cognitive Graph ontology, SHACL specs, CWM schemas, capability catalog. | Ontology diagrams, CWM-A/G/E schema (see issue #288), fact/capability definitions. |
| `docs/services/` | Service-specific behavior for Sophia, Hermes, Apollo, Talos. One subfolder per repo. | API surface summaries, deployment notes, SDK usage instructions. |
| `docs/operations/` | CI/CD, verification procedures, scenario scripts, observability/metrics guides. | Scenario tooling (#278–#276), verification checklists, Otel dashboards. |
| `docs/reference/` | Contracts, API docs, and generated artifacts that must live in the repo (`contracts/` can link here). | OpenAPI pointers, SDK regeneration how-tos. |

Existing directories (`phase1/`, `phase2/`, `spec/`, etc.) remain in place temporarily but should be migrated into this structure as we consolidate content.

## Inventory & Migration Tracker

| Current Location | Target Folder | Notes / Action |
| --- | --- | --- |
| `docs/phase2/PHASE2_SPEC.md`, `docs/spec/LOGOS_SPEC_FLEXIBLE.md` | ✔️ migrated to `docs/architecture/` | Highest-level specs now live under `docs/architecture/`. Update any remaining references to the new paths. |
| `docs/phase2/VERIFY.md`, `docs/phase2/METRICS_IDEAS.md` | ✔️ migrated to `docs/operations/` | Verification guides and metrics ideation now live in `docs/operations/`. |
| `docs/phase2/APOLLO_WEB_PROTOTYPE_SPRINT.md` | ✔️ migrated to `docs/services/apollo/` | Service-specific notes should live under the corresponding service folder. |
| `docs/phase2/CWM_STATE_CONTRACT_ROLLOUT.md` | ✔️ migrated to `docs/hcg/` | All CWM/HCG schema docs should consolidate here (see issue #288 for further work). |
| `docs/spec/*`, `docs/api/*`, `docs/sdk/*` | `docs/reference/` & `docs/services/*` | Move per-service parts into their folders; keep shared contracts under reference. |
| `docs/phase1/*` | `docs/history/phase1/` (optional) or archive | Retain for posterity but clearly mark as historical. |
| `docs/issues/*`, `docs/demo/*`, standalone ticket-description files | Remove or convert into proper guides in `operations/` or service folders. |

Use this checklist when migrating a document:

1. Decide the new home using the table above.
2. Move or rewrite the file into the destination folder.
3. Update inbound links (repo README, CONTRIBUTING, phase docs) to reference the new path.
4. Delete the obsolete stub or replace it with a pointer if historically relevant.
5. Add navigation links to the corresponding `index.md`.

## Authoring Guidelines

- **Single source of truth**: keep substantive content in the consolidated tree; repo READMEs should only summarize and link here.
- **No ticket-only docs**: if a document’s sole purpose is to restate an issue or milestone, convert it into a checklist inside the issue or delete it.
- **Cross-repo contributions**: when documenting Sophia/Hermes/Apollo specifics, create or update the matching `docs/services/<service>/` page—even if the implementation lives in another repo. Link back to that service’s README for code-level details.
- **Metadata**: include front matter or headings for ownership, last verified date, and related issues so future maintainers know who to ping.

## Next Steps

1. Migrate the remaining Phase 2 perception/demo docs (e.g., `docs/phase2/perception/*`, `docs/demo/*`) into the appropriate `architecture/`, `services/`, or `operations/` folders.
2. Draft the CWM-A/G/E schema in `docs/hcg/` (tracked by issue #288) and link it from the capability catalog (#284).
3. Convert scenario/benchmark docs to `docs/operations/scenarios/` and delete redundant issue-only files.
4. Update each service README to point to its `docs/services/<service>/` entry.
5. Add a doc-style linter (e.g., simple script or checklist) to CI so new docs are placed correctly.

Refer to this README when adding or relocating documentation. If a file does not clearly fit one of the sections above, open a doc issue so we can decide whether to create a new category or adjust the structure.
