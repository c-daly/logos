# Scenario: CLI-Only Operations

## Goal
Run a goal→plan→diagnostics cycle entirely from the Apollo CLI, exercising shared SDK output and persona logging without the browser.

## Prerequisites
- Sophia/Hermes services running
- Apollo CLI installed (points to local cluster)

## Capture Steps
1. Start services.
2. Execute `./replay.sh` or run equivalent CLI commands (e.g., `logos plan create ...`).
3. Stream logs until the plan completes and diagnostics stabilize.
4. Archive artifacts below.

## Artifacts
- `cwm_state.jsonl`
- `plan.log`
- `state.log`
- `personas.jsonl`

## Notes
Document CLI commands issued, tokens used, and any anomalies observed.
