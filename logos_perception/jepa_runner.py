"""
JEPA (Joint Embedding Predictive Architecture) runner for k-step rollout simulations.

This module provides interfaces for running imagination/simulation workflows.
Can be backed by CPU-friendly runners or hardware simulators (Talos/Gazebo).
"""

import logging
from typing import Any, cast

import numpy as np
from pydantic import BaseModel

from .models import ImaginedProcess, ImaginedState, SimulationResult

logger = logging.getLogger(__name__)


class JEPAConfig(BaseModel):
    """Configuration for JEPA runner."""

    model_version: str = "jepa-v0.1"
    embedding_dim: int = 768
    use_hardware_sim: bool = False
    hardware_sim_endpoint: str | None = None


class JEPARunner:
    """
    JEPA runner for k-step imagination rollouts.

    Supports both CPU-friendly mode (for Talos-free scenarios) and
    hardware simulator integration (Talos/Gazebo).
    """

    def __init__(self, config: JEPAConfig | None = None):
        """
        Initialize JEPA runner.

        Args:
            config: Configuration for the runner
        """
        self.config = config or JEPAConfig()
        logger.info(
            f"Initialized JEPA runner with model {self.config.model_version}, "
            f"hardware_sim={self.config.use_hardware_sim}"
        )

    def simulate(
        self,
        capability_id: str,
        context: dict[str, Any],
        k_steps: int = 5,
    ) -> SimulationResult:
        """
        Run k-step imagination rollout.

        Args:
            capability_id: ID of the capability being simulated
            context: Context information including entity references and frame data
            k_steps: Number of prediction steps to perform

        Returns:
            SimulationResult with imagined process and states
        """
        logger.info(f"Running {k_steps}-step simulation for capability {capability_id}")

        # Create imagined process
        process = ImaginedProcess(
            capability_id=capability_id,
            imagined=True,
            horizon=k_steps,
            assumptions=context,
            model_version=self.config.model_version,
        )

        # Generate predicted states
        states = self._generate_predicted_states(k_steps, context)

        return SimulationResult(
            process=process,
            states=states,
            metadata={
                "model_version": self.config.model_version,
                "use_hardware_sim": self.config.use_hardware_sim,
            },
        )

    def _generate_predicted_states(
        self, k_steps: int, context: dict[str, Any]
    ) -> list[ImaginedState]:
        """
        Generate k predicted future states.

        In production, this would use a trained JEPA model or hardware simulator.
        For Phase 2, we provide a lightweight CPU-friendly stub.

        Args:
            k_steps: Number of steps to predict
            context: Context information

        Returns:
            List of imagined states
        """
        states = []

        for step in range(k_steps):
            # Generate mock embedding (in production, this comes from JEPA model)
            embedding = self._generate_mock_embedding()

            # Confidence degrades over longer horizons
            confidence = 1.0 - (step * 0.1)

            state = ImaginedState(
                step=step,
                embedding=embedding,
                confidence=max(0.1, confidence),
                metadata={
                    "source": (
                        "cpu_runner"
                        if not self.config.use_hardware_sim
                        else "hardware_sim"
                    ),
                    "context_keys": list(context.keys()),
                },
            )
            states.append(state)

        return states

    def _generate_mock_embedding(self) -> list[float]:
        """
        Generate a mock embedding vector.

        In production, this would come from the JEPA model.

        Returns:
            Mock embedding vector
        """
        # Generate random embedding with unit norm for testing
        vec = np.random.randn(self.config.embedding_dim)
        vec = vec / np.linalg.norm(vec)
        return cast(list[float], vec.tolist())

    def connect_hardware_sim(self, endpoint: str) -> None:
        """
        Connect to hardware simulator (Talos/Gazebo).

        Args:
            endpoint: Simulator endpoint URL
        """
        logger.info(f"Connecting to hardware simulator at {endpoint}")
        self.config.use_hardware_sim = True
        self.config.hardware_sim_endpoint = endpoint
        # In production, establish connection to Talos/Gazebo here

    def disconnect_hardware_sim(self) -> None:
        """Disconnect from hardware simulator."""
        logger.info("Disconnecting from hardware simulator")
        self.config.use_hardware_sim = False
        self.config.hardware_sim_endpoint = None
