from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

from logos_experiment.agent import AgentDefinition
from logos_experiment.config import ExperimentConfig


class ExperimentRunner:
    """Orchestrates arrange/act/assert lifecycle for an experiment."""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.agents: list[AgentDefinition] = []
        self._results: list[Any] = []
        self._rng = np.random.default_rng(config.seed)

    def arrange(self, factories: dict[str, Callable] | None = None) -> None:
        """Create agents from factories using pipeline config."""
        factories = factories or {}
        for step in self.config.pipeline:
            factory = factories.get(step.name)
            if factory is None:
                raise ValueError(f"No factory provided for step '{step.name}'")
            agent = factory(step.config)
            self.agents.append(agent)

    def act(self, input_corpus: list[Any]) -> list[Any]:
        """Run each input through the pipeline of agents."""
        self._results = []
        for input_data in input_corpus:
            current = input_data
            for agent in self.agents:
                current = agent.process(current)
            self._results.append(current)
        return self._results

    def assert_results(self) -> dict[str, Any]:
        """Return experiment artifacts for evaluation."""
        return {
            "config": self.config,
            "results": list(self._results),
            "seed": self.config.seed,
        }
