# Planner Stub CI/CD Integration

This document explains how the planner stub service is integrated into the CI/CD pipeline for M3/M4 testing.

## Overview

The planner stub service is automatically started in the M3 and M4 workflows before running tests. This allows tests to make real HTTP calls to the planner API instead of using direct Cypher queries or mocks.

## GitHub Actions Integration

### M3 Planning Workflow

The M3 workflow (`.github/workflows/m3-planning.yml`) starts the planner service before running tests:

```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -e .
    pip install pytest pytest-cov rdflib pyshacl httpx

- name: Start planner stub service
  run: |
    python -m planner_stub.app &
    PLANNER_PID=$!
    echo "PLANNER_PID=$PLANNER_PID" >> $GITHUB_ENV
    
    # Wait for service to be ready
    for i in {1..30}; do
      if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "✓ Planner service is ready"
        break
      fi
      sleep 2
    done

- name: Run M3 Planning Tests
  run: pytest tests/phase1/test_m3_planning.py -v

- name: Stop planner service
  if: always()
  run: kill $PLANNER_PID || true
```

### M4 End-to-End Workflow

The M4 workflow (`.github/workflows/m4-end-to-end.yml`) follows the same pattern but also includes Neo4j and Milvus services:

1. Start HCG infrastructure (Neo4j + Milvus)
2. Start planner stub service
3. Load ontology and test data
4. Run M4 integration tests
5. Stop all services

## Environment Variables in CI

The workflows use the following environment variables:

- `PLANNER_PID` - Process ID of the planner service (for cleanup)
- `RUN_M4_E2E` - Set to "1" to enable full M4 end-to-end tests

## Testing Locally with CI Configuration

To test the CI setup locally:

```bash
# Install dependencies
pip install -e .
pip install pytest pytest-cov rdflib pyshacl httpx

# Start planner service
python -m planner_stub.app &
PLANNER_PID=$!

# Wait for service
sleep 5
curl http://localhost:8001/health

# Run M3 tests
pytest tests/phase1/test_m3_planning.py -v

# Run planner stub tests
pytest tests/test_planner_stub.py -v

# Stop service
kill $PLANNER_PID
```

## Troubleshooting

### Service Not Starting

If the planner service fails to start in CI:

1. Check that all dependencies are installed (especially `httpx`)
2. Verify port 8001 is not already in use
3. Check logs for startup errors

### Service Not Ready in Time

The workflow waits up to 60 seconds for the service to respond to health checks. If this fails:

1. Increase the wait time in the workflow
2. Check if the service is crashing on startup
3. Verify network connectivity in the CI environment

### Tests Skipping API Calls

Tests that require the planner service will be skipped if:

1. The `planner_stub.client` module cannot be imported
2. The service is not available (health check fails)
3. The service is not responding on port 8001

Check that:
- `httpx` is installed
- The planner service is running
- The `PLANNER_URL` environment variable is set correctly (default: `http://localhost:8001`)

## Port Configuration

The planner service uses port 8001 by default. To change the port:

1. Set the `PLANNER_PORT` environment variable
2. Update the workflow to use the new port
3. Update test fixtures and client initialization

Example:

```bash
export PLANNER_PORT=9001
python -m uvicorn planner_stub.app:app --port 9001
```

## Future Enhancements

As the planner stub evolves:

1. Add Docker container support for easier CI deployment
2. Add health check retries with exponential backoff
3. Add metrics/logging for CI debugging
4. Consider using a service container in GitHub Actions
5. Add integration tests that verify service startup/shutdown

## References

- M3 Planning Workflow: `.github/workflows/m3-planning.yml`
- M4 E2E Workflow: `.github/workflows/m4-end-to-end.yml`
- Planner Stub README: `planner_stub/README.md`
- Start Script: `scripts/start_planner.sh`
