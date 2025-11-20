"""
Simulation service for handling imagination workflows.

Integrates JEPA runner with Neo4j/Milvus storage.
"""

import logging
from typing import Any

from neo4j import Driver
from pymilvus import connections

from logos_perception import JEPARunner, JEPAConfig, SimulationRequest, SimulationResult
from logos_perception.models import ImaginedProcess, ImaginedState

logger = logging.getLogger(__name__)


class SimulationService:
    """
    Service for managing imagination simulations.

    Coordinates between JEPA runner and HCG storage.
    """

    def __init__(
        self,
        neo4j_driver: Driver,
        jepa_config: JEPAConfig | None = None,
        milvus_alias: str = "default",
    ):
        """
        Initialize simulation service.

        Args:
            neo4j_driver: Neo4j driver for HCG storage
            jepa_config: Configuration for JEPA runner
            milvus_alias: Milvus connection alias
        """
        self.neo4j_driver = neo4j_driver
        self.jepa_runner = JEPARunner(jepa_config)
        self.milvus_alias = milvus_alias
        logger.info("Initialized SimulationService")

    def run_simulation(self, request: SimulationRequest) -> SimulationResult:
        """
        Run k-step imagination simulation.

        Args:
            request: Simulation request with capability_id and context

        Returns:
            SimulationResult with imagined process and states
        """
        logger.info(
            f"Running simulation for capability {request.capability_id} "
            f"with {request.k_steps} steps"
        )

        # Run JEPA simulation
        result = self.jepa_runner.simulate(
            capability_id=request.capability_id,
            context=request.context,
            k_steps=request.k_steps,
        )

        # Store in HCG
        self._store_imagined_process(result.process)
        self._store_imagined_states(result.process.uuid, result.states)

        # Store embeddings in Milvus
        self._store_embeddings(result.states)

        # Link frame if provided
        if request.frame_id:
            self._link_frame_to_simulation(request.frame_id, result.process.uuid)

        return result

    def _store_imagined_process(self, process: ImaginedProcess) -> None:
        """
        Store ImaginedProcess in Neo4j.

        Args:
            process: ImaginedProcess to store
        """
        query = """
        CREATE (p:ImaginedProcess {
            uuid: $uuid,
            timestamp: datetime($timestamp),
            capability_id: $capability_id,
            imagined: $imagined,
            horizon: $horizon,
            assumptions: $assumptions,
            model_version: $model_version
        })
        RETURN p.uuid as process_uuid
        """

        with self.neo4j_driver.session() as session:
            result = session.run(
                query,
                uuid=process.uuid,
                timestamp=process.timestamp.isoformat(),
                capability_id=process.capability_id,
                imagined=process.imagined,
                horizon=process.horizon,
                assumptions=process.assumptions,
                model_version=process.model_version,
            )
            result.single()
            logger.info(f"Stored ImaginedProcess {process.uuid} in Neo4j")

    def _store_imagined_states(
        self, process_uuid: str, states: list[ImaginedState]
    ) -> None:
        """
        Store ImaginedStates in Neo4j and link to process.

        Args:
            process_uuid: UUID of parent ImaginedProcess
            states: List of ImaginedStates to store
        """
        query = """
        MATCH (p:ImaginedProcess {uuid: $process_uuid})
        UNWIND $states as state_data
        CREATE (s:ImaginedState {
            uuid: state_data.uuid,
            timestamp: datetime(state_data.timestamp),
            step: state_data.step,
            confidence: state_data.confidence,
            metadata: state_data.metadata
        })
        CREATE (p)-[:PREDICTS]->(s)
        """

        states_data = [
            {
                "uuid": state.uuid,
                "timestamp": state.timestamp.isoformat(),
                "step": state.step,
                "confidence": state.confidence,
                "metadata": state.metadata,
            }
            for state in states
        ]

        with self.neo4j_driver.session() as session:
            session.run(query, process_uuid=process_uuid, states=states_data)
            logger.info(
                f"Stored {len(states)} ImaginedStates linked to process {process_uuid}"
            )

    def _store_embeddings(self, states: list[ImaginedState]) -> None:
        """
        Store state embeddings in Milvus.

        Args:
            states: List of ImaginedStates with embeddings
        """
        try:
            if not connections.has_connection(self.milvus_alias):
                logger.warning(
                    f"Not connected to Milvus alias {self.milvus_alias}, "
                    "skipping embedding storage"
                )
                return

            # Store embeddings (simplified for Phase 2)
            for state in states:
                if state.embedding:
                    logger.debug(
                        f"Would store embedding for state {state.uuid} "
                        f"(dim={len(state.embedding)})"
                    )

        except Exception as e:
            logger.error(f"Failed to store embeddings in Milvus: {e}")

    def _link_frame_to_simulation(
        self, frame_id: str, process_uuid: str
    ) -> None:
        """
        Link perception frame to simulation process.

        Args:
            frame_id: Frame ID
            process_uuid: ImaginedProcess UUID
        """
        query = """
        MATCH (f:PerceptionFrame {uuid: $frame_id})
        MATCH (p:ImaginedProcess {uuid: $process_uuid})
        CREATE (f)-[:TRIGGERED_SIMULATION]->(p)
        """

        with self.neo4j_driver.session() as session:
            session.run(query, frame_id=frame_id, process_uuid=process_uuid)
            logger.info(
                f"Linked frame {frame_id} to simulation {process_uuid}"
            )

    def get_simulation_results(
        self, process_uuid: str
    ) -> dict[str, Any] | None:
        """
        Retrieve simulation results from Neo4j.

        Args:
            process_uuid: UUID of ImaginedProcess

        Returns:
            Dictionary with process and states, or None if not found
        """
        query = """
        MATCH (p:ImaginedProcess {uuid: $process_uuid})
        OPTIONAL MATCH (p)-[:PREDICTS]->(s:ImaginedState)
        RETURN p, collect(s) as states
        """

        with self.neo4j_driver.session() as session:
            result = session.run(query, process_uuid=process_uuid)
            record = result.single()

            if record:
                return {
                    "process": dict(record["p"]),
                    "states": [dict(s) for s in record["states"]],
                }
            return None
