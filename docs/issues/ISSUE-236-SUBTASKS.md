# Issue #236 — Shared Sophia/Hermes SDKs

Tracking subtasks required to deliver the shared SDK effort.

| ID | Description | Owner | Status | Notes |
|----|-------------|-------|--------|-------|
| [236A](https://github.com/c-daly/logos/issues/253) | Author `sophia.openapi.yaml` describing `/health`, `/plan`, `/state`, `/simulate` per Phase 2 spec | LOGOS | In Progress | current PR |
| [236B](https://github.com/c-daly/logos/issues/254) | Set up OpenAPI codegen pipeline and commit generated SDKs under `sdk/` (Python) and `sdk-web/` (TypeScript) | LOGOS | In Progress | `scripts/generate-sdks.sh` uses openapi-generator CLI |
| [236C](https://github.com/c-daly/logos/issues/255) | Document SDK usage + versioning/publish steps (`docs/sdk/README.md`) | LOGOS | In Progress | README outlines install/version instructions |
| [236D](https://github.com/c-daly/logos/issues/256) | Add CI workflow to regenerate/verify SDKs when contracts change | LOGOS | TODO | e.g., `.github/workflows/sdk-regenerate.yml` |
| [236E](https://github.com/c-daly/logos/issues/257) | Refactor Apollo CLI/browser to consume the generated SDKs | Apollo | TODO | separate repo follow-up |
