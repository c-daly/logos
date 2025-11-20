# LOGOS SDKs

This directory contains auto-generated Python client SDKs for the LOGOS services (Sophia and Hermes). These SDKs are generated from the OpenAPI contracts in `/contracts` and provide type-safe, idiomatic Python interfaces for interacting with LOGOS services.

## Available SDKs

- **`hermes_client/`** - Python client for Hermes API (STT, TTS, NLP, embeddings)
- **`sophia_client/`** - Python client for Sophia API (planning, state, simulation)

## Installation

### Local Development

For local development or when using the Apollo CLI, install the SDKs in editable mode:

```bash
# From the repository root
cd sdk/hermes_client && pip install -e .
cd ../sophia_client && pip install -e .
```

### From Source Repository

Install directly from the repository:

```bash
pip install git+https://github.com/c-daly/logos.git#subdirectory=sdk/hermes_client
pip install git+https://github.com/c-daly/logos.git#subdirectory=sdk/sophia_client
```

### Local Package Install

Build and install the wheel packages:

```bash
# Build packages
cd sdk/hermes_client && python -m build
cd ../sophia_client && python -m build

# Install packages
pip install sdk/hermes_client/dist/hermes_client-1.0.0-py3-none-any.whl
pip install sdk/sophia_client/dist/sophia_client-1.0.0-py3-none-any.whl
```

## Usage

### Hermes Client

```python
from hermes_client import ApiClient, Configuration, DefaultApi

# Configure the client
config = Configuration(host="http://localhost:8080")
client = ApiClient(configuration=config)
api = DefaultApi(client)

# Text-to-speech
tts_request = {
    "text": "Hello from LOGOS",
    "language": "en-US"
}
audio_response = api.text_to_speech(tts_request)

# Generate embeddings
embed_request = {
    "text": "The red block is on the table"
}
embedding_response = api.embed_text(embed_request)
print(f"Embedding dimension: {embedding_response.dimension}")

# Simple NLP processing
nlp_request = {
    "text": "The quick brown fox jumps over the lazy dog",
    "operations": ["tokenize", "pos_tag"]
}
nlp_response = api.simple_nlp(nlp_request)
print(f"Tokens: {nlp_response.tokens}")
```

### Sophia Client

```python
from sophia_client import ApiClient, Configuration, DefaultApi

# Configure the client
config = Configuration(host="http://localhost:8000")
client = ApiClient(configuration=config)
api = DefaultApi(client)

# Generate a plan
plan_request = {
    "goal": "Pick up the red block and place it in the bin",
    "goal_state": {
        "entities": [
            {
                "entity_id": "block_red_001",
                "desired_state": "in_bin"
            }
        ]
    }
}
plan_response = api.generate_plan(plan_request)
print(f"Plan ID: {plan_response.plan_id}")
print(f"Number of processes: {len(plan_response.processes)}")

# Query current state
state_response = api.get_state(limit=10, model_type="CWM_A")
print(f"Retrieved {len(state_response.states)} states")

# Run simulation
sim_request = {
    "capability_id": "grasp_object",
    "context": {
        "entity_ids": ["block_red_001", "gripper_001"],
        "horizon_steps": 5
    }
}
sim_response = api.run_simulation(sim_request)
print(f"Simulation ID: {sim_response.simulation_id}")
print(f"Imagined states: {len(sim_response.imagined_states)}")
```

## Versioning

The SDK versions follow semantic versioning and are tied to the OpenAPI contract versions:

- **Major version**: Breaking API changes
- **Minor version**: New features, backward compatible
- **Patch version**: Bug fixes, backward compatible

Current versions:
- Hermes SDK: `1.0.0` (matches `contracts/hermes.openapi.yaml` v1.0.0)
- Sophia SDK: `1.0.0` (matches `contracts/sophia.openapi.yaml` v1.0.0)

## Publishing

### Internal Package Registry (Optional)

If your organization uses an internal package registry (e.g., Azure Artifacts, GitHub Packages, JFrog Artifactory):

1. Configure package publishing in `pyproject.toml`
2. Build the packages:
   ```bash
   cd sdk/hermes_client && python -m build
   cd ../sophia_client && python -m build
   ```
3. Publish to the registry:
   ```bash
   twine upload -r internal-registry sdk/hermes_client/dist/*
   twine upload -r internal-registry sdk/sophia_client/dist/*
   ```

### PyPI (Public Release)

For public release to PyPI:

1. Update version numbers in OpenAPI contracts
2. Regenerate SDKs using `scripts/generate_sdks.sh`
3. Build packages:
   ```bash
   cd sdk/hermes_client && python -m build
   cd ../sophia_client && python -m build
   ```
4. Upload to PyPI:
   ```bash
   twine upload sdk/hermes_client/dist/*
   twine upload sdk/sophia_client/dist/*
   ```

## Regenerating SDKs

The SDKs are automatically regenerated in CI when OpenAPI contracts change. To regenerate manually:

```bash
./scripts/generate_sdks.sh
```

This script:
1. Validates the OpenAPI contracts
2. Generates fresh Python SDKs using OpenAPI Generator
3. Generates fresh TypeScript SDKs for browser usage
4. Cleans up old generated files

**Note**: After regeneration, review the changes and ensure backward compatibility. Breaking changes require a major version bump.

## Development

### Testing

Each SDK includes generated test stubs. To run tests:

```bash
cd sdk/hermes_client && pytest
cd ../sophia_client && pytest
```

### Type Checking

The generated SDKs include type hints. Run mypy for type checking:

```bash
cd sdk/hermes_client && mypy hermes_client/
cd ../sophia_client && mypy sophia_client/
```

## Contributing

When updating the OpenAPI contracts:

1. Update the contract file in `/contracts`
2. Validate the contract: `swagger-cli validate contracts/<service>.openapi.yaml`
3. Regenerate SDKs: `./scripts/generate_sdks.sh`
4. Review generated changes
5. Update SDK version if necessary
6. Test the SDKs with example code
7. Update this README if API usage has changed

## Support

- **Issues**: Report bugs and issues on the [LOGOS GitHub repository](https://github.com/c-daly/logos/issues)
- **Documentation**: See the [Phase 2 specification](../docs/phase2/PHASE2_SPEC.md)
- **API Reference**: See individual SDK READMEs and `docs/` directories

## License

These SDKs are part of Project LOGOS and are released under the MIT License.
