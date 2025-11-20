# Demo Capture Scripts

This directory contains utilities for capturing demo artifacts for Phase 2 verification.

## capture_demo.py

Captures browser sessions, CLI interactions, and system logs for verification evidence.

### Prerequisites

- **Browser capture**: ffmpeg (for screen recording)
  ```bash
  # Ubuntu/Debian
  sudo apt-get install ffmpeg
  
  # macOS
  brew install ffmpeg
  ```

- **CLI capture**: `script` command (usually pre-installed on Unix systems)

### Usage

#### Capture Everything (Browser + CLI + Logs)
```bash
python capture_demo.py --mode all --duration 120
```

#### Browser Session Only
```bash
python capture_demo.py --mode browser --duration 60
```

#### CLI Session Only
```bash
# Interactive recording
python capture_demo.py --mode cli

# Or specify commands to execute
python capture_demo.py --mode cli --commands "logos-cli status" "logos-cli query"
```

#### Logs Aggregation Only
```bash
python capture_demo.py --mode logs --log-dirs /tmp/logos_telemetry ./logs
```

### Output

All artifacts are saved to `./demo_output/` (configurable with `--output-dir`):

- `browser_demo_<timestamp>.mp4` - Screen recording of browser UI
- `cli_demo_<timestamp>.log` - CLI session transcript
- `logs_aggregated_<timestamp>.json` - Collected logs from all LOGOS components
- `MANIFEST.json` - Manifest of all captured artifacts

### Demo Recording Tips

#### Browser Demo
1. Start the Apollo browser UI (`http://localhost:3000`)
2. Run the capture script
3. During recording, demonstrate:
   - Chat with persona-aware responses
   - View plan/state updates in diagnostics panel
   - Show emotion states in graph viewer
   - Query persona diary entries

#### CLI Demo
1. Demonstrate key CLI commands:
   ```bash
   logos-cli status
   logos-cli plan --goal "example goal"
   logos-cli state --entity <uuid>
   logos-cli persona --recent 10
   logos-cli emotions --process <uuid>
   ```

2. Show observability:
   ```bash
   tail -f /tmp/logos_telemetry/plan_update_*.jsonl
   ```

### Integration with Verification

Captured artifacts should be referenced in `docs/phase2/VERIFY.md` as evidence for:
- P2-M4 acceptance criteria
- Observability stack functionality
- Persona diary API usage
- CWM-E emotion tagging
- Demo capture process documentation

## Alternative Tools

If `ffmpeg` or `script` are not available:

- **Browser**: Use OBS Studio, Loom, or similar screen recording tools
- **CLI**: Use `asciinema` for terminal session recording
- **Logs**: Manually copy log files to `demo_output/` directory

## See Also

- `docs/phase2/VERIFY.md` - Verification checklist for Phase 2
- `docs/phase2/PHASE2_SPEC.md` - Phase 2 specification
