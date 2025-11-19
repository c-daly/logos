# LOGOS Planner Stub

Minimal stub implementation of the Sophia Planner component for Phase 1 testing.

## Overview

This planner stub provides a callable API for plan generation without requiring the full Sophia cognitive core implementation. It is used in M3/M4 tests to validate planning concepts and integration.

**Purpose**: Demonstrate the planner API contract that Sophia will implement, allowing M3/M4 tests to use real HTTP calls instead of direct Cypher queries.

**Phase 1 Scope**: Uses pre-defined scenarios from test fixtures. Full causal reasoning over the HCG will be implemented in Sophia during later phases.

## API Endpoints

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### `POST /plan`
Generate a plan from initial state to goal state.

**Request:**
```json
{
  "initial_state": {
    "properties": {
      "gripper": "open",
      "arm_position": "home",
      "object_grasped": false
    }
  },
  "goal_state": {
    "properties": {
      "object_location": "bin",
      "object_grasped": false
    }
  },
  "scenario_name": "pick_and_place"
}
```

**Response:**
```json
{
  "plan": [
    {
      "process": "MoveAction",
      "preconditions": ["arm_at_home"],
      "effects": ["arm_at_pre_grasp"],
      "uuid": "process-moveaction-a1b2c3d4"
    },
    {
      "process": "GraspAction",
      "preconditions": ["gripper_open", "arm_at_pre_grasp"],
      "effects": ["object_grasped", "gripper_closed"],
      "uuid": "process-graspaction-e5f6g7h8"
    }
  ],
  "success": true,
  "message": "Plan generated for scenario: pick_and_place",
  "scenario_name": "pick_and_place"
}
```

## Running Locally

### Start the service

```bash
# From repository root
python -m planner_stub.app
```

The service will start on `http://localhost:8001`.

### Using Docker Compose

Add to your `docker-compose.yml`:

```yaml
planner-stub:
  build:
    context: .
    dockerfile: planner_stub/Dockerfile
  ports:
    - "8001:8001"
  environment:
    - PLANNER_PORT=8001
```

### Environment Variables

- `PLANNER_URL`: Base URL for the planner service (default: `http://localhost:8001`)
- `PLANNER_PORT`: Port to run the service on (default: `8001`)

## Usage from Tests

```python
from planner_stub.client import PlannerClient

# Create client
client = PlannerClient()

# Check if service is available
if client.is_available():
    # Generate a plan
    response = client.generate_plan(
        initial_state={"gripper": "open", "object_grasped": False},
        goal_state={"object_grasped": True},
        scenario_name="simple_grasp"
    )
    
    print(f"Generated {len(response.plan)} steps")
    for step in response.plan:
        print(f"  - {step.process}: {step.uuid}")
```

## Running in CI

The GitHub Actions workflows automatically start the planner stub service before running M3/M4 tests:

```yaml
- name: Start planner stub
  run: |
    python -m planner_stub.app &
    sleep 5  # Wait for service to start
    
- name: Run M3 tests
  run: pytest tests/phase1/test_m3_planning.py
```

## Scenarios

The planner stub uses pre-defined scenarios from `tests/phase1/fixtures/plan_scenarios.json`:

- **simple_grasp**: Single-step plan to grasp an object
- **pick_and_place**: Multi-step plan to pick up and place an object

## Future Implementation

This stub will be replaced by the full Sophia Planner implementation, which will:
- Perform causal reasoning over the HCG
- Use Neo4j queries to traverse process/state relationships
- Support dynamic plan generation without pre-defined scenarios
- Integrate with the Executor for plan execution and monitoring

## API Documentation

Interactive API documentation is available when the service is running:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
