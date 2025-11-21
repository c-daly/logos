# [ADR-0006] Hermes as LLM Gateway

**Status:** Proposed

**Date:** 2025-11-20

**Decision Makers:** Project LOGOS maintainers

**Related Issues:** #236, #255, c-daly/apollo#17, c-daly/apollo#18

## Context and Problem Statement

The Phase 2 spec requires Apollo (CLI + web) to act as a thin interaction layer while Hermes handles all language/LLM utilities. Today Apollo’s browser chat panel can call an external LLM provider directly, bypassing Hermes. We need a consistent, documented path so every language-related feature (chat proposals, persona reflections, embeddings) flows through Hermes. The question: how should we expose LLM capabilities so Apollo, CLI, and future surfaces consume one contract without hard-coding providers?

## Decision Drivers

* Keep Apollo UI thin and reusable; no bespoke LLM logic per surface.
* Allow multiple provider backends (OpenAI, Anthropic, local models like spaCy/sentence-transformers) without changing clients.
* Preserve persona/gullibility telemetry by passing interactions through Hermes instrumentation.
* Support SDK generation so both Python and TypeScript clients can call the endpoint easily.

## Considered Options

* Apollo continues calling external LLMs directly (status quo).
* Hermes exposes an `/llm` endpoint with pluggable providers and Apollo migrates to it.
* Introduce a new microservice dedicated to LLM orchestration (separate from Hermes).

## Decision Outcome

Chosen option: "Hermes exposes an `/llm` endpoint with pluggable providers". Hermes already owns STT/TTS, embeddings, and persona-aware language utilities, so extending it to broker LLM calls keeps the spec clean and enables SDK generation. A separate service would add unnecessary coordination overhead, while the status quo violates the architecture principle of Hermes as the single language interface.

### Positive Consequences

* Apollo CLI/web call the same SDK functions (no duplicate HTTP code).
* Persona, gullibility, and diagnostics instrumentation stay centralized in Hermes.
* Switching providers (OpenAI → local model) becomes a config change, not a refactor.

### Negative Consequences

* Hermes must manage API keys, rate limits, and cost tracking for any external LLM provider.
* Need to implement provider abstraction + health checks inside Hermes.
* Requires updating the Hermes OpenAPI spec and regenerating SDKs again.

## Pros and Cons of the Options

### Apollo calls external LLMs directly (status quo)

* Good: quickest to prototype, no Hermes changes.
* Bad: duplicates logic across CLI/web, bypasses Hermes telemetry, harder to swap providers, violates spec philosophy.

### Hermes exposes `/llm` endpoint (chosen)

* Good: single API surface, easier SDK generation, instrumentation lives in Hermes.
* Good: provider abstraction allows OpenAI now and smaller/local models later.
* Bad: increases Hermes scope; must handle streaming, auth, retries.

### New LLM microservice

* Good: decouples heavy compute from Hermes.
* Bad: adds another service + deployment path, yet still requires Apollo to call a different URL—no benefit over just extending Hermes.

## Links

* Refines [ADR-0005](0005-vector-embedding-strategy.md) by clarifying Hermes responsibilities.

## References

* `docs/spec/LOGOS_SPEC_FLEXIBLE.md` – Section 3.4 (Hermes).
* `docs/research/MAKE_LOGOS_GREAT_AGAIN.md` – Scenario coverage + SDK discussions.
