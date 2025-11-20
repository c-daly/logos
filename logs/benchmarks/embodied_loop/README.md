# Scenario: Embodied Loop

## Goal
Talos (physical or simulated) performs the pick-and-place loop used in demos, exercising JEPA predictions and persona reflections during execution.

## Prerequisites
- HCG dev cluster + Sophia/Hermes services running
- Talos simulator or hardware profile configured
- Apollo CLI/browser connected to Sophia

## Capture Steps
1. Start the infrastructure (`docker compose -f infra/docker-compose.hcg.dev.yml up -d`).
2. Launch Talos simulator/hardware.
3. Execute `./replay.sh` to run the scripted goal, or reproduce the steps manually via Apollo.
4. Export Neo4j/Milvus evidence as described below.

## Artifacts
- `cwm_state.jsonl`
- `plan.log`
- `state.log`
- `personas.jsonl`
- `jepe_frames/`
- `talos_telemetry.jsonl`

## Notes
Document entities involved, hardware configuration, and links to screenshots/video.
