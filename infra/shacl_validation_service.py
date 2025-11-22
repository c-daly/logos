#!/usr/bin/env python3
"""
SHACL Validation Service for LOGOS HCG

Provides an HTTP API for validating RDF data against SHACL shapes.
This service is part of the LOGOS infrastructure and supports the
Level 1 deterministic validation layer for the Hybrid Causal Graph.

Reference: Project LOGOS spec, Section 4.3.1 (SHACL Validation)
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pyshacl import validate
from rdflib import Graph

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load SHACL shapes at startup
# Try to find shapes file in multiple locations for flexibility
POSSIBLE_SHAPES_PATHS = [
    Path(__file__).parent.parent / "ontology" / "shacl_shapes.ttl",  # Normal location
    Path(__file__).parent / "ontology" / "shacl_shapes.ttl",  # Docker location
    Path("ontology/shacl_shapes.ttl"),  # Relative to working directory
]

shacl_shapes_graph: Graph | None = None


def load_shacl_shapes():
    """Load SHACL shapes from file."""
    global shacl_shapes_graph

    # Find the shapes file
    shapes_file = None
    for path in POSSIBLE_SHAPES_PATHS:
        if path.exists():
            shapes_file = path
            break

    if shapes_file is None:
        logger.error(f"SHACL shapes file not found in any of: {POSSIBLE_SHAPES_PATHS}")
        raise FileNotFoundError("SHACL shapes file not found")

    try:
        shacl_shapes_graph = Graph()
        shacl_shapes_graph.parse(shapes_file, format="turtle")
        logger.info(
            f"Loaded {len(shacl_shapes_graph)} SHACL triples from {shapes_file}"
        )
    except Exception as e:
        logger.error(f"Failed to load SHACL shapes: {e}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    load_shacl_shapes()
    yield
    # Shutdown
    pass


# Initialize FastAPI app
app = FastAPI(
    title="LOGOS SHACL Validation Service",
    description=(
        "REST API for validating RDF data against SHACL shapes. "
        "Part of the LOGOS infrastructure for HCG validation."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# Request/Response Models
class ValidationRequest(BaseModel):
    """Request model for RDF data validation."""

    data: str = Field(
        ...,
        description="RDF data to validate in Turtle format",
        json_schema_extra={
            "example": (
                "@prefix logos: <http://logos.ontology/> .\n"
                "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n"
                "logos:entity-test-001 a logos:Entity ;\n"
                '    logos:uuid "entity-test-001" ;\n'
                '    logos:name "Test Entity" .\n'
            )
        },
    )

    format: str = Field(
        default="turtle",
        description="RDF format of the data (turtle, n3, xml, etc.)",
        json_schema_extra={"example": "turtle"},
    )

    inference: str = Field(
        default="none",
        description="Inference mode: none, rdfs, owlrl, or both",
        json_schema_extra={"example": "rdfs"},
    )

    abort_on_first: bool = Field(
        default=False,
        description="Stop validation on first error",
        json_schema_extra={"example": False},
    )


class ValidationResult(BaseModel):
    """Response model for validation results."""

    conforms: bool = Field(..., description="True if data conforms to SHACL shapes")

    violations_count: int = Field(
        ..., description="Number of validation violations found"
    )

    report_text: str = Field(..., description="Human-readable validation report")

    report_graph: dict[str, Any] | None = Field(
        None, description="Detailed validation report as RDF triples (optional)"
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    shapes_loaded: bool = Field(..., description="Whether SHACL shapes are loaded")
    shapes_count: int = Field(..., description="Number of SHACL triples loaded")


# API Endpoints
@app.get("/", response_model=dict[str, str])
async def root():
    """Root endpoint with service information."""
    return {
        "service": "LOGOS SHACL Validation Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    if shacl_shapes_graph is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "shapes_loaded": False, "shapes_count": 0},
        )

    return {
        "status": "healthy",
        "shapes_loaded": True,
        "shapes_count": len(shacl_shapes_graph),
    }


@app.post("/validate", response_model=ValidationResult)
async def validate_data(request: ValidationRequest):
    """
    Validate RDF data against loaded SHACL shapes.

    This endpoint validates the provided RDF data against the SHACL shapes
    defined in ontology/shacl_shapes.ttl. It returns a detailed validation
    report indicating whether the data conforms to the shapes.

    Args:
        request: ValidationRequest containing RDF data and options

    Returns:
        ValidationResult with conformance status and detailed report

    Raises:
        HTTPException: If shapes are not loaded or validation fails
    """
    if shacl_shapes_graph is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SHACL shapes not loaded",
        )

    try:
        # Parse input data
        data_graph = Graph()
        data_graph.parse(data=request.data, format=request.format)
        logger.info(f"Parsed {len(data_graph)} data triples for validation")

        # Run SHACL validation
        conforms, results_graph, results_text = validate(
            data_graph,
            shacl_graph=shacl_shapes_graph,
            inference=request.inference,
            abort_on_first=request.abort_on_first,
            allow_warnings=True,
        )

        # Count violations by parsing the report text
        violations_count = 0
        if not conforms and results_text:
            # Count "Constraint Violation" occurrences in report
            violations_count = results_text.count("Constraint Violation")

        logger.info(
            f"Validation complete: conforms={conforms}, violations={violations_count}"
        )

        return ValidationResult(
            conforms=conforms,
            violations_count=violations_count,
            report_text=results_text,
            report_graph=None,  # Can be extended to return structured report
        )

    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation failed: {str(e)}",
        ) from e


@app.get("/shapes", response_model=dict[str, Any])
async def get_shapes_info():
    """
    Get information about loaded SHACL shapes.

    Returns:
        Dictionary with shape statistics and metadata
    """
    if shacl_shapes_graph is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SHACL shapes not loaded",
        )

    # Count different types of shapes
    from rdflib.namespace import RDF, SH

    node_shapes = len(list(shacl_shapes_graph.subjects(RDF.type, SH.NodeShape)))
    property_shapes = len(list(shacl_shapes_graph.subjects(RDF.type, SH.PropertyShape)))

    return {
        "total_triples": len(shacl_shapes_graph),
        "node_shapes": node_shapes,
        "property_shapes": property_shapes,
        "shapes_file": "shacl_shapes.ttl",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8081, log_level="info")
