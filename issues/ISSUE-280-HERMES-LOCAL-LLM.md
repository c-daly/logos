# Issue #280 — Default OSS LLM provider for Hermes

## Summary
Ensure a freshly cloned Hermes repo can exercise the `/llm` endpoint without any cloud API keys by bundling an open-source model/provider into the default configuration. The goal is a “batteries-included” developer experience: install the `ml` extras, run `poetry run hermes`, and get real completions (not just the current `echo` stub).

## Tasks
1. **Pick lightweight provider**  
   Evaluate llama.cpp, text-generation-inference, or mistral.rs backends that can run a 7B-class model on CPU. Document hardware requirements and decide which binary/weights to ship (or script to download).

2. **Integrate provider module**  
   Add a new provider implementation in `hermes/llm.py` (e.g., `LocalLLMProvider`) that shell-executes or HTTP-calls the local backend. Register it under `provider=local` and make it the automatic fallback when no API key is detected.

3. **Extend packaging/runtime**  
   Update Dockerfiles, optional extras, and the README to explain how the OSS model is installed/cached. Provide scripts (or compose services) to download weights so CI/dev boxes stay reproducible.

4. **Update docs + SDK demos**  
   - Refresh `docs/demo/APOLLO_LLM_ONLY.md` to mention the local-default option.  
   - Add guidance to `hermes/examples/README.md` on switching between local/OpenAI providers.  
   - Note hardware limits in `DEVELOPMENT.md` and ADR-0006 if needed.

5. **Testing**  
   Create smoke tests (perhaps flagged with `@pytest.mark.local_llm`) that hit the new provider in CI using a dummy/shim model, ensuring `/llm` works when no env vars are set.

## Acceptance Criteria
- Running Hermes with no `HERMES_LLM_PROVIDER` and no API keys automatically starts using the bundled OSS LLM and returns coherent completions.  
- Documentation clearly describes the fallback logic and how to toggle between local/OpenAI providers.  
- CI or a tagged workflow validates the local provider path so regressions are caught early.
