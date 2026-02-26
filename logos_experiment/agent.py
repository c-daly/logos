from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class AgentDefinition(Protocol):
    """Minimal contract for experiment pipeline participation.

    The framework calls process(). That's the whole contract.
    Agents are free to have any additional methods, state, or dependencies.
    """

    def process(self, input_data: Any) -> Any: ...


@runtime_checkable
class StatefulAgent(AgentDefinition, Protocol):
    """Agent with observable, snapshottable, resettable state."""

    def get_state(self) -> Any: ...
    def reset(self, state: Any = None) -> None: ...
    def snapshot(self) -> Any: ...
