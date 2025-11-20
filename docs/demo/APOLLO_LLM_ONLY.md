# Apollo LLM-Only Demo Guide

This guide captures the steps required to run the Apollo web experience in "LLM-only" mode—no Talos hardware or perception pipeline—so you can showcase the Phase 2 UI, shared SDKs, and Hermes integration while generating benchmark artifacts.

> **Scope:** Sophia + Hermes services running locally, Apollo webapp calling Hermes for all language/LLM needs via the generated TypeScript SDKs.

## 1. Prerequisites

1. **Latest repos**: pull `logos`, `sophia`, `hermes`, and `apollo` (main branches).
2. **Dev dependencies**: Node.js 18+, Python 3.11+, Poetry, Docker (for the HCG cluster).
3. **Shared SDKs**: from the `logos` repo run `./scripts/generate-sdks.sh` so `sdk-web/sophia` and `sdk-web/hermes` are up to date.
4. **Hermes LLM provider**: set env vars for the provider you want to call (e.g., `HERMES_LLM_PROVIDER=openai`, `HERMES_LLM_API_KEY=...`). Hermes will expose an `/llm` endpoint per ADR-0006.

## 2. Start Core Services

```bash
# From logos/
docker compose -f infra/docker-compose.hcg.dev.yml up -d  # Neo4j, Milvus, etc.

# Sophia API
gnome-terminal -- bash -lc "cd logos_sophia && poetry install && poetry run uvicorn logos_sophia.api:app --reload"

# Hermes API (with LLM config)
gnometerminal -- bash -lc "cd hermes && poetry install && HERMES_LLM_PROVIDER=openai HERMES_LLM_API_KEY=... poetry run uvicorn hermes.api:app --reload"
```

Verify:
```bash
curl http://localhost:8000/health   # Sophia
curl http://localhost:8080/health   # Hermes
```

## 3. Install Apollo Webapp

```bash
cd apollo/webapp
npm install
# Link SDKs (until published, use local paths)
npm install ../../logos/sdk-web/sophia ../../logos/sdk-web/hermes
```

Configure `.env.local` (example):
```
VITE_SOPHIA_BASE_URL=http://localhost:8000
VITE_HERMES_BASE_URL=http://localhost:8080
VITE_HERMES_LLM_ENABLED=true
```

## 4. Run the Webapp

```bash
npm run dev
# open http://localhost:5173
```

Workflow suggestions:
1. Submit a goal via the chat panel (Hermes `/llm` generates proposals, Sophia `/plan` executes).
2. View plan timeline + diagnostics.
3. Trigger persona diary entries via CLI or UI actions to populate CWM-E data.

## 5. Capture Benchmark Artifacts

After completing the demo, populate `logs/benchmarks/browser_llm/`:

1. Save the `/plan` and `/state` HTTP transcripts (e.g., rerun the requests via `curl` and pipe to `plan.log`, `state.log`).
2. Export CWM states via Cypher or an admin script (see issue #276 for upcoming helpers) and store as `cwm_state.jsonl`.
3. Dump persona entries via the `logos_persona` API (`curl http://localhost:8000/persona/entries`) and save as `personas.jsonl`.
4. Capture screenshots/video of the webapp and note paths in `README.md`.

Finally, edit `logs/benchmarks/browser_llm/README.md` + `replay.sh` with the exact steps/commands you ran so others can reproduce the bundle.

## 6. Troubleshooting

- **SDK mismatch**: rerun `./scripts/generate-sdks.sh` if Apollo complains about missing types or endpoints.
- **LLM auth errors**: confirm Hermes env vars are loaded in the shell running `uvicorn`.
- **CORS**: if the browser can’t reach Hermes/Sophia, check the FastAPI CORS settings (default allows localhost).
- **Persona logs missing**: ensure Hermes `/llm` responses include persona context and Sophia is wired to the persona diary (issues #264/#265).

With these steps, you have a repeatable LLM-only demo plus the artifacts required for scenario coverage and publication evidence. Track improvements and TODOs in issue #273.
