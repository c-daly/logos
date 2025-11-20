# Scenario: Swappable Hardware

## Goal
Run the same plan twice—once against a simulator, once against physical Talos hardware—and show that Sophia’s API outputs remain identical aside from telemetry.

## Prerequisites
- Access to both Talos simulator and hardware configuration
- Sophia/Hermes services running

## Capture Steps
1. Execute `./replay.sh sim` to run the simulation capture.
2. Execute `./replay.sh hardware` for the physical run.
3. Store both sets of artifacts in this directory (different subfolders if desired).

## Artifacts
- `cwm_state.jsonl` (per run)
- `plan.log`
- `state.log`
- `personas.jsonl`
- `talos_telemetry.jsonl`

## Notes
Describe differences between hardware modes and link to video evidence.
