"""
Planner Stub API Service

FastAPI application that exposes the planner stub via HTTP endpoints.

Endpoints:
- GET /health - Health check
- POST /plan - Generate a plan

Reference: This demonstrates the planner API that Sophia will implement
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from . import __version__
from .models import HealthResponse, PlanRequest, PlanResponse
from .planner import get_planner

# Create FastAPI app
app = FastAPI(
    title="LOGOS Planner Stub",
    description="Minimal planner stub for LOGOS Phase 1 testing",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns service status and version.
    """
    return HealthResponse(status="healthy", version=__version__)


@app.post("/plan", response_model=PlanResponse)
async def generate_plan(request: PlanRequest):
    """
    Generate a plan from initial state to goal state.

    This stub implementation uses pre-defined scenarios from test fixtures.
    A full implementation would perform causal reasoning over the HCG.

    Args:
        request: PlanRequest with initial_state, goal_state, and optional scenario_name

    Returns:
        PlanResponse with the generated plan

    Raises:
        HTTPException: If plan generation fails
    """
    try:
        planner = get_planner()
        response = planner.generate_plan(request)

        if not response.success:
            # Return 422 for planning failures
            raise HTTPException(
                status_code=422, detail=response.message or "Plan generation failed"
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal error during plan generation: {str(e)}"
        ) from e


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "LOGOS Planner Stub",
        "version": __version__,
        "endpoints": {"health": "/health", "plan": "/plan", "docs": "/docs"},
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(status_code=404, content={"detail": "Endpoint not found"})


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


if __name__ == "__main__":
    import uvicorn

    # Run with: python -m planner_stub.app
    uvicorn.run("planner_stub.app:app", host="0.0.0.0", port=8001, reload=True)
