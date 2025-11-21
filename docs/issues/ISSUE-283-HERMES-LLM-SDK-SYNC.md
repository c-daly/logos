# Issue #283 — Sync Hermes `/llm` contract into LOGOS SDKs

## Summary
Hermes PR #13 (`feature/hermes-llm-gateway`) added the `/llm` endpoint + `LLM*` schemas to the Hermes OpenAPI contract. The LOGOS repo still carries the pre-LLM version of `contracts/hermes.openapi.yaml`, so every `./scripts/generate-sdks.sh` run wipes out the `LLMRequest/LLMResponse` artifacts in `sdk/` and `sdk-web/`. Apollo (and any other consumers) therefore cannot call `llmGenerate` even though Hermes itself supports the endpoint.

## Tasks
1. Copy/merge the updated Hermes OpenAPI spec (with `/llm`, `LLMRequest`, `LLMResponse`, etc.) into `contracts/hermes.openapi.yaml` in this repo.
2. Regenerate SDKs via `./scripts/generate-sdks.sh` so both Python and TypeScript packages include the new models + `llmGenerate`.
3. Rebuild the local `sdk-web/hermes` package (`npm install && npm run build`) and ensure Apollo’s `package-lock.json` is updated after reinstalling the dependency.
4. Add regression coverage (e.g., simple `rg`/test) that checks `contracts/hermes.openapi.yaml` contains `/llm` and that the generated SDK exports `llmGenerate`, preventing accidental regressions.
5. Document the update in the README/CHANGELOG so downstream repos know to pull the refreshed SDKs.

## Acceptance Criteria
- `contracts/hermes.openapi.yaml` in LOGOS contains the `/llm` path and `LLM*` schemas.
- Generated SDKs under `sdk/python/hermes` and `sdk-web/hermes` include the corresponding request/response models and `llmGenerate` client method.
- Apollo webapp can import the local SDK and compile without “`api.llmGenerate is not a function`” errors.
