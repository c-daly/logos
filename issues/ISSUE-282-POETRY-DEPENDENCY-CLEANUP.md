# Issue #282 — Align Poetry dependencies and pip usage

## Summary
Running `poetry run pytest` in the LOGOS repo currently fails because required packages (e.g., OpenTelemetry) aren’t declared in `pyproject.toml`. Developers have been installing them ad‑hoc via `pip`, which breaks reproducibility and CI consistency. We need to move all required deps into Poetry (core + optional extras) and eliminate direct `pip install …` steps in scripts/workflows.

## Tasks
1. **Audit tests + code for undeclared deps**
   - LOGOS: OpenTelemetry (`opentelemetry-api`, `opentelemetry-sdk`, exporter) used in `logos_observability` and Sophia modules.
   - Hermes: verify Torch/Milvus/MLO extras are fully captured (already under `[project.optional-dependencies]`, but confirm we don’t rely on `poetry run pip install torch …` anywhere else).
   - Other repos (sophia, talos, apollo) if they have local pip installs in docs/scripts.

2. **Update `pyproject.toml`**
   - Add missing dependencies under the appropriate group (`[tool.poetry.dependencies]`, `[tool.poetry.group.dev.dependencies]`, or extras).
   - Define extras for optional stacks (e.g., `observability`, `perception`) so contributors can `poetry install --extras "observability"` when needed.

3. **Clean up scripts/workflows**
   - Replace `poetry run pip install …` commands with either `poetry install --extras …` or document the extras.
   - Ensure CI uses those extras instead of ad hoc pip calls (e.g., in `.github/workflows/ci.yml`).

4. **Documentation**
   - Update `DEVELOPMENT.md` / repo-specific READMEs with instructions for installing extras (e.g., `poetry install --all-extras` or `poetry install --extras "observability perception"`).

5. **Verification**
   - Run `poetry lock && poetry install` from a clean environment.
   - Verify `poetry run pytest` succeeds without needing manual pip installs.

## Acceptance Criteria
- All dependencies referenced in tests or runtime code are declared in Poetry configs (LOGOS + Hermes + any other affected repo).
- No CI script or doc instructs running `pip install` in addition to Poetry.
- Contributors can recreate full dev envs using only `poetry install` commands (with documented extras) on a clean machine.
