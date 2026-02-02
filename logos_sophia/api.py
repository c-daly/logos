"""
FastAPI endpoints for Sophia service.

Provides REST API for planning, state queries, and simulation.
"""

import logging

from fastapi import APIRouter, HTTPException
from neo4j import Driver
from opentelemetry import trace
from pydantic import BaseModel

from logos_perception import JEPAConfig, SimulationRequest

from .simulation import SimulationService

logger = logging.getLogger(__name__)
tracer = trace.get_tracer("sophia.simulation")


class SimulateResponse(BaseModel):
    """Response model for /simulate endpoint."""

    process_uuid: str
    states_count: int
    horizon: int
    model_version: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str


def create_sophia_api(
    neo4j_driver: Driver,
    jepa_config: JEPAConfig | None = None,
) -> APIRouter:
    """
    Create FastAPI router for Sophia endpoints.

    Args:
        neo4j_driver: Neo4j driver instance
        jepa_config: Optional JEPA configuration

    Returns:
        Configured APIRouter
    """
    router = APIRouter(prefix="/sophia", tags=["sophia"])
    simulation_service = SimulationService(neo4j_driver, jepa_config)

    @router.get("/health", response_model=HealthResponse)
    def health_check():
        """
        Health check endpoint.

        Returns:
            Health status
        """
        return HealthResponse(status="healthy", service="sophia")

    @router.post("/simulate", response_model=SimulateResponse)
    def simulate(request: SimulationRequest):
        """
        Run k-step imagination simulation.

        Accepts capability_id and context, runs JEPA rollout,
        and stores ImaginedProcess/ImaginedState nodes in Neo4j/Milvus.

        Args:
            request: Simulation request

        Returns:
            Simulation results summary
        """
        with tracer.start_as_current_span("sophia.simulate") as span:
            try:
                logger.info(
                    f"Received simulation request for capability {request.capability_id}"
                )

                result = simulation_service.run_simulation(request)

                # Link trace to plan ID
                span.set_attribute("plan_id", result.process.uuid)
                span.set_attribute("capability_id", request.capability_id)
                span.set_attribute("horizon", result.process.horizon)

                return SimulateResponse(
                    process_uuid=result.process.uuid,
                    states_count=len(result.states),
                    horizon=result.process.horizon,
                    model_version=result.process.model_version,
                )

            except Exception as e:
                logger.error(f"Simulation failed: {e}", exc_info=True)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise HTTPException(
                    status_code=500, detail=f"Simulation failed: {str(e)}"
                ) from e

    @router.get("/simulate/{process_uuid}")
    def get_simulation(process_uuid: str):
        """
        Retrieve simulation results.

        Args:
            process_uuid: UUID of ImaginedProcess

        Returns:
            Simulation process and states
        """
        result = simulation_service.get_simulation_results(process_uuid)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Simulation {process_uuid} not found",
            )

        return result

    return router
