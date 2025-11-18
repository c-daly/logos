# SHACL Validation Service

REST API for validating RDF data against SHACL shapes in the LOGOS ecosystem.

## Overview

The SHACL Validation Service provides an HTTP API for validating RDF data against the SHACL shapes defined in `ontology/shacl_shapes.ttl`. This service is part of the LOGOS infrastructure and supports Level 1 deterministic validation for the Hybrid Causal Graph (HCG).

Reference: Project LOGOS Specification, Section 4.3.1 (SHACL Validation)

## Quick Start

### Running with Docker Compose

The service is included in the HCG development cluster:

```bash
# Start all services (Neo4j, Milvus, SHACL Validation)
docker compose -f infra/docker-compose.hcg.dev.yml up -d

# Check service health
curl http://localhost:8081/health
```

### Running Standalone

```bash
# Install dependencies
pip install -e ".[dev]"

# Start the service
python infra/shacl_validation_service.py

# Service will be available at http://localhost:8081
```

## API Endpoints

### GET /

Service information and version

```bash
curl http://localhost:8081/
```

### GET /health

Health check endpoint

```bash
curl http://localhost:8081/health
```

Response:
```json
{
  "status": "healthy",
  "shapes_loaded": true,
  "shapes_count": 296
}
```

### GET /shapes

Get information about loaded SHACL shapes

```bash
curl http://localhost:8081/shapes
```

Response:
```json
{
  "total_triples": 296,
  "node_shapes": 16,
  "property_shapes": 0,
  "shapes_file": "shacl_shapes.ttl"
}
```

### POST /validate

Validate RDF data against SHACL shapes

```bash
curl -X POST http://localhost:8081/validate \
  -H "Content-Type: application/json" \
  -d '{
    "data": "@prefix logos: <http://logos.ontology/> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\nlogos:entity-test-001 a logos:Entity ;\n    logos:uuid \"entity-test-001\" ;\n    logos:name \"Test Entity\" .",
    "format": "turtle",
    "inference": "rdfs",
    "abort_on_first": false
  }'
```

**Request Parameters:**

- `data` (required): RDF data to validate as a string
- `format` (optional, default: "turtle"): RDF format (turtle, n3, xml, etc.)
- `inference` (optional, default: "none"): Inference mode (none, rdfs, owlrl, both)
- `abort_on_first` (optional, default: false): Stop validation on first error

**Response (Success):**
```json
{
  "conforms": true,
  "violations_count": 0,
  "report_text": "Validation Report\nConforms: True\n",
  "report_graph": null
}
```

**Response (Validation Failure):**
```json
{
  "conforms": false,
  "violations_count": 2,
  "report_text": "Validation Report\nConforms: False\n\nConstraint Violation in ...",
  "report_graph": null
}
```

### GET /docs

Interactive API documentation (Swagger UI)

Open in browser: http://localhost:8081/docs

### GET /redoc

Alternative API documentation (ReDoc)

Open in browser: http://localhost:8081/redoc

## Examples

### Validate a Valid Entity

```bash
curl -X POST http://localhost:8081/validate \
  -H "Content-Type: application/json" \
  -d '{
    "data": "@prefix logos: <http://logos.ontology/> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\nlogos:entity-cube-001 a logos:Entity ;\n    logos:uuid \"entity-cube-001\" ;\n    logos:name \"Cube\" ;\n    logos:width \"0.1\"^^xsd:decimal ;\n    logos:height \"0.1\"^^xsd:decimal ;\n    logos:depth \"0.1\"^^xsd:decimal .",
    "format": "turtle"
  }'
```

### Validate an Invalid Entity (Missing Required Field)

```bash
curl -X POST http://localhost:8081/validate \
  -H "Content-Type: application/json" \
  -d '{
    "data": "@prefix logos: <http://logos.ontology/> .\n\nlogos:entity-invalid a logos:Entity ;\n    logos:name \"Invalid Entity\" .",
    "format": "turtle"
  }'
```

This will return `conforms: false` because the `uuid` field is required for entities.

### Validate with RDFS Inference

```bash
curl -X POST http://localhost:8081/validate \
  -H "Content-Type: application/json" \
  -d '{
    "data": "@prefix logos: <http://logos.ontology/> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\nlogos:entity-test a logos:Entity ;\n    logos:uuid \"entity-test\" ;\n    logos:name \"Test\" .",
    "format": "turtle",
    "inference": "rdfs"
  }'
```

## Python Client Example

```python
import requests

# Validate RDF data
response = requests.post(
    "http://localhost:8081/validate",
    json={
        "data": """
            @prefix logos: <http://logos.ontology/> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
            
            logos:entity-test-001 a logos:Entity ;
                logos:uuid "entity-test-001" ;
                logos:name "Test Entity" .
        """,
        "format": "turtle",
        "inference": "none"
    }
)

result = response.json()
print(f"Conforms: {result['conforms']}")
print(f"Violations: {result['violations_count']}")
print(f"Report:\n{result['report_text']}")
```

## Supported RDF Formats

- `turtle` - Turtle (default)
- `n3` - Notation3
- `xml` - RDF/XML
- `nt` - N-Triples
- `trig` - TriG
- `nquads` - N-Quads
- `json-ld` - JSON-LD

## Inference Modes

- `none` - No inference (default)
- `rdfs` - RDFS inference
- `owlrl` - OWL-RL inference
- `both` - Both RDFS and OWL-RL inference

## Testing

Run the test suite:

```bash
pytest tests/infra/test_shacl_validation_service.py -v
```

## Architecture

The service:
1. Loads SHACL shapes from `ontology/shacl_shapes.ttl` at startup
2. Validates incoming RDF data using pyshacl
3. Returns structured validation reports
4. Supports multiple RDF formats and inference modes
5. Provides health checks for monitoring

## Docker Build

To build the Docker image manually:

```bash
docker build -t logos-shacl-validation -f infra/Dockerfile.shacl-validation .
```

To run the container:

```bash
docker run -d \
  --name logos-shacl-validation \
  -p 8081:8081 \
  -v $(pwd)/ontology:/app/ontology:ro \
  logos-shacl-validation
```

## Integration

The SHACL validation service can be integrated into other LOGOS components:

- **Sophia**: Validate graph updates before committing to Neo4j
- **Apollo**: Validate user inputs before processing
- **Talos**: Validate sensor data representations
- **CI/CD**: Validate test fixtures and example data

## Troubleshooting

### Service Won't Start

Check if the SHACL shapes file exists:
```bash
ls -l ontology/shacl_shapes.ttl
```

Check service logs:
```bash
docker logs logos-shacl-validation
```

### Validation Errors

Enable debug mode by checking the detailed report text in the response. The `report_text` field contains detailed information about which constraints failed.

### Port Already in Use

Change the port mapping in `docker-compose.hcg.dev.yml`:
```yaml
ports:
  - "8082:8081"  # Use port 8082 instead
```

## References

- [SHACL Specification](https://www.w3.org/TR/shacl/)
- [pyshacl Library](https://github.com/RDFLib/pySHACL)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Project LOGOS Specification](../docs/spec/project_logos_full.md)

## License

MIT License - See repository root for details

## Maintainer

LOGOS Development Team
