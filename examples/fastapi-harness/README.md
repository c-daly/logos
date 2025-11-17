# FastAPI Contract Validation Harness

## Purpose

This is a **minimal FastAPI validation harness** that demonstrates how the canonical LOGOS OpenAPI contracts (defined in `/contracts/hermes.openapi.yaml`) are used by a running application. 

**This is NOT a full service scaffold.** It is intentionally limited in scope to:
- Demonstrate contract-based request/response validation
- Provide automated tests that verify contract compliance
- Serve as a CI smoke test for contract artifacts

For full service scaffolding, deployment manifests, and production-ready infrastructure, please refer to the **logos-template** repository (or your organization's service template repository).

## What's Included

### Application Structure
```
examples/fastapi-harness/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application factory
│   └── models.py        # Pydantic models from OpenAPI contract
├── tests/
│   ├── __init__.py
│   └── test_contract_validation.py  # Contract validation tests
├── Dockerfile           # Minimal Docker image for CI
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Implemented Endpoints

The harness implements **mock versions** of two Hermes API endpoints:

1. **POST /simple_nlp** - Simple NLP Preprocessing
   - Validates request against contract schema
   - Returns mock NLP results (tokens, POS tags, lemmas, entities)
   - Demonstrates operation parameter validation

2. **POST /embed_text** - Text Embedding Generation
   - Validates request against contract schema
   - Returns mock embedding vectors
   - Demonstrates model parameter handling

## Running the Harness Locally

### Prerequisites
- Python 3.10 or higher
- pip

### Installation

```bash
cd examples/fastapi-harness
pip install -r requirements.txt
```

### Run the Application

```bash
# From the fastapi-harness directory
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload
```

The application will start on `http://localhost:8080`.

### Interactive API Documentation

Once running, you can explore the API at:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc
- OpenAPI JSON: http://localhost:8080/openapi.json

### Example Requests

**Simple NLP Processing:**
```bash
curl -X POST http://localhost:8080/simple_nlp \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The quick brown fox",
    "operations": ["tokenize", "pos_tag"]
  }'
```

**Text Embedding:**
```bash
curl -X POST http://localhost:8080/embed_text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Sample text for embedding",
    "model": "default"
  }'
```

## Running Tests

The test suite validates that the application correctly implements the contract:

```bash
# From the fastapi-harness directory
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=term-missing
```

### What the Tests Validate

- ✅ Canonical OpenAPI contract is valid
- ✅ Request validation against contract schemas
- ✅ Response validation against contract schemas
- ✅ Required fields are enforced
- ✅ Error handling for invalid inputs
- ✅ Default values are applied correctly
- ✅ OpenAPI schema is properly exposed

## Docker

Build and run the container for CI testing:

```bash
# Build the image
docker build -t logos-fastapi-harness .

# Run the container
docker run -p 8080:8080 logos-fastapi-harness
```

**Note:** This Dockerfile is for CI smoke testing only, not production deployment.

## Linting

```bash
# Run ruff for code quality
ruff check app/ tests/

# Auto-fix issues
ruff check app/ tests/ --fix
```

## Integration with CI

This harness is designed to be used in GitHub Actions workflows for:
1. Validating that the OpenAPI contract is syntactically correct
2. Verifying that a minimal implementation can satisfy the contract
3. Ensuring contract changes don't break expected behavior

See `.github/workflows/fastapi-harness.yml` for the CI configuration.

## Contract Reference

All models and endpoint definitions are derived from the canonical contract:
- **Location:** `/contracts/hermes.openapi.yaml`
- **Spec Reference:** Table 2 in Section 3.4 of the LOGOS specification
- **API Type:** Stateless language & embedding utility

The contract defines the following endpoints (only 2 implemented in this harness):
- `/stt` - Speech-to-Text (not implemented in harness)
- `/tts` - Text-to-Speech (not implemented in harness)
- `/simple_nlp` - Simple NLP Preprocessing (✅ implemented)
- `/embed_text` - Text Embedding Generation (✅ implemented)

## Limitations and Non-Goals

This harness intentionally does NOT include:
- ❌ Real NLP processing or embedding generation
- ❌ Database connections or state management
- ❌ Authentication or authorization
- ❌ Production-grade error handling
- ❌ Logging and monitoring infrastructure
- ❌ Deployment manifests (Kubernetes, Helm, etc.)
- ❌ Full CI/CD pipeline
- ❌ Performance optimization
- ❌ All endpoints from the contract (only 2 of 4 implemented)

For production service development, use your organization's service template repository.

## For Service Developers

If you're building the actual Hermes service or other LOGOS components:

1. **Use this harness as a reference** for how to structure Pydantic models from the contract
2. **Run the contract validation tests** as part of your service's test suite
3. **Refer to the canonical contract** (`/contracts/hermes.openapi.yaml`) as the source of truth
4. **Use a proper service template** for your production service scaffold

This harness exists to validate the contract, not to serve as a production starting point.

## Contributing

When updating the canonical Hermes contract (`/contracts/hermes.openapi.yaml`):

1. Update the corresponding models in `app/models.py` if schemas change
2. Update endpoint implementations in `app/main.py` if new operations are added
3. Add/update tests in `tests/test_contract_validation.py`
4. Ensure all tests pass before committing

The goal is to keep this harness in sync with the contract while maintaining its minimal scope.

## Links

- **Canonical Contracts:** `/contracts/` in this repository
- **LOGOS Specification:** `/docs/spec/project_logos_full.md`
- **Service Template:** See `logos-template` repository (or your org's template repo)
- **Hermes Service:** See `c-daly/hermes` repository

## License

Part of Project LOGOS. See repository root for license information.
