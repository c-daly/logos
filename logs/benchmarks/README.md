# Scenario Benchmark Bundles

Each folder under `logs/benchmarks/` captures the artifacts needed to replay a canonical LOGOS scenario. Use these bundles when preparing verification evidence or running the Scenario Coverage Index tooling (see docs/phase2/METRICS_IDEAS.md).

## Required Artifacts per Scenario
- `README.md` — context, prerequisites, replay steps.
- `replay.sh` — script or command list to reproduce the run.
- `cwm_state.jsonl` — serialized CWMState emissions.
- `plan.log` / `state.log` — API transcripts.
- `personas.jsonl` — PersonaEntry events.
- `jepe_frames/` — imagined frames (if applicable).
- `talos_telemetry.jsonl` — actuator/sensor traces for embodied runs.

Populate each bundle with real data before submitting verification evidence; placeholder files below describe the expectations.
