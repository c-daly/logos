# Scenario: Talos-Free Perception

## Goal
Demonstrate the browser upload → JEPA prediction path without Talos, capturing how Sophia logs imagined states and surface diagnostics.

## Prerequisites
- Sophia/Hermes services running
- Apollo browser configured
- Sample media clip(s) for upload

## Capture Steps
1. Start services (`docker compose ...`).
2. From Apollo browser, upload the prepared media via the perception panel.
3. Run `./replay.sh` to automate the upload if desired.
4. Collect artifacts listed below.

## Artifacts
- `cwm_state.jsonl`
- `plan.log`
- `state.log`
- `personas.jsonl`
- `jepe_frames/`

## Notes
Record media sample IDs, JEPA model version, and any assumptions used.
