# Scenario: Browser + LLM Co-Processor

## Goal
Capture an Apollo browser session where the embedded LLM proposes actions and Sophia validates them via the shared SDK, including gullibility/conflict logging.

## Prerequisites
- Sophia/Hermes services with persona pipeline enabled
- Apollo browser configured with LLM provider credentials

## Capture Steps
1. Start services and browser front-end.
2. Use `./replay.sh` (or manual steps) to run a scripted conversation.
3. Save chat transcripts along with the artifacts below.

## Artifacts
- `cwm_state.jsonl`
- `plan.log`
- `state.log`
- `personas.jsonl`
- `jepe_frames/` (if `/simulate` invoked)

## Notes
Note prompts, LLM model, and conflicts detected for gullibility metrics.
