"""
Orchestrator - Control Flow and Subsystem Coordination

The Orchestrator manages the overall control flow of the Sophia cognitive core,
coordinating communication between subsystems and managing their lifecycle.

Tasks (from Workstream B1):
- Design control flow state machine
- Implement subsystem registration and lifecycle management
- Add inter-subsystem message passing
- Create Orchestrator integration tests

Reference: Section 3.3, Workstream B1
"""

from collections.abc import Callable
from enum import Enum
from typing import Any


class SystemState(Enum):
    """Orchestrator system states"""
    INITIALIZING = "initializing"
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class Orchestrator:
    """
    Manages overall control flow and subsystem coordination for Sophia.

    The Orchestrator implements a state machine that coordinates the flow of
    information between CWM-A, CWM-G, Planner, and Executor subsystems.
    All internal processing occurs in graph-structured representations.

    Attributes:
        state: Current system state
        subsystems: Registry of registered subsystems
        message_handlers: Callbacks for inter-subsystem messages
    """

    def __init__(self):
        """Initialize the Orchestrator in INITIALIZING state"""
        self.state = SystemState.INITIALIZING
        self.subsystems: dict[str, Any] = {}
        self.message_handlers: dict[str, list[Callable]] = {}

    def register_subsystem(self, name: str, subsystem: Any) -> None:
        """
        Register a subsystem with the Orchestrator.

        Args:
            name: Unique identifier for the subsystem
            subsystem: The subsystem instance to register

        Raises:
            ValueError: If subsystem name is already registered
        """
        if name in self.subsystems:
            raise ValueError(f"Subsystem '{name}' is already registered")
        self.subsystems[name] = subsystem

    def unregister_subsystem(self, name: str) -> None:
        """
        Unregister a subsystem from the Orchestrator.

        Args:
            name: Identifier of the subsystem to unregister

        Raises:
            KeyError: If subsystem name is not registered
        """
        if name not in self.subsystems:
            raise KeyError(f"Subsystem '{name}' is not registered")
        del self.subsystems[name]

    def send_message(self, from_subsystem: str, to_subsystem: str,
                    message: dict[str, Any]) -> None:
        """
        Send a message between subsystems.

        Args:
            from_subsystem: Name of the sending subsystem
            to_subsystem: Name of the receiving subsystem
            message: Message payload as a dictionary

        Raises:
            KeyError: If either subsystem is not registered
        """
        if to_subsystem not in self.subsystems:
            raise KeyError(f"Target subsystem '{to_subsystem}' is not registered")

        # TODO: Implement message passing mechanism
        # This will be extended in Phase 1 implementation
        pass

    def register_handler(self, message_type: str, handler: Callable) -> None:
        """
        Register a message handler for a specific message type.

        Args:
            message_type: Type of message to handle
            handler: Callback function to handle the message
        """
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)

    def start(self) -> None:
        """
        Start the Orchestrator and transition to IDLE state.

        This initializes all registered subsystems and prepares the system
        for processing.
        """
        # TODO: Implement subsystem initialization
        self.state = SystemState.IDLE

    def shutdown(self) -> None:
        """
        Shutdown the Orchestrator and all registered subsystems.

        This performs cleanup and transitions to SHUTDOWN state.
        """
        # TODO: Implement graceful shutdown
        self.state = SystemState.SHUTDOWN

    def get_state(self) -> SystemState:
        """
        Get the current system state.

        Returns:
            Current SystemState enum value
        """
        return self.state

    def get_subsystem(self, name: str) -> Any | None:
        """
        Retrieve a registered subsystem by name.

        Args:
            name: Name of the subsystem to retrieve

        Returns:
            The subsystem instance, or None if not found
        """
        return self.subsystems.get(name)
