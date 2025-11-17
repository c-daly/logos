"""
Unit tests for Orchestrator module

Tests cover:
- Subsystem registration and lifecycle management
- State machine transitions
- Message passing infrastructure (stub)
"""

import pytest

from sophia.orchestrator import Orchestrator, SystemState


class TestOrchestrator:
    """Test suite for Orchestrator class"""

    def test_initialization(self):
        """Test Orchestrator initializes in INITIALIZING state"""
        orchestrator = Orchestrator()
        assert orchestrator.get_state() == SystemState.INITIALIZING
        assert len(orchestrator.subsystems) == 0

    def test_register_subsystem(self):
        """Test subsystem registration"""
        orchestrator = Orchestrator()
        mock_subsystem = object()

        orchestrator.register_subsystem("test_subsystem", mock_subsystem)

        assert "test_subsystem" in orchestrator.subsystems
        assert orchestrator.get_subsystem("test_subsystem") is mock_subsystem

    def test_register_duplicate_subsystem_raises_error(self):
        """Test that registering duplicate subsystem raises ValueError"""
        orchestrator = Orchestrator()
        mock_subsystem = object()

        orchestrator.register_subsystem("test", mock_subsystem)

        with pytest.raises(ValueError, match="already registered"):
            orchestrator.register_subsystem("test", mock_subsystem)

    def test_unregister_subsystem(self):
        """Test subsystem unregistration"""
        orchestrator = Orchestrator()
        mock_subsystem = object()

        orchestrator.register_subsystem("test", mock_subsystem)
        orchestrator.unregister_subsystem("test")

        assert "test" not in orchestrator.subsystems
        assert orchestrator.get_subsystem("test") is None

    def test_unregister_nonexistent_subsystem_raises_error(self):
        """Test that unregistering nonexistent subsystem raises KeyError"""
        orchestrator = Orchestrator()

        with pytest.raises(KeyError, match="not registered"):
            orchestrator.unregister_subsystem("nonexistent")

    def test_start_transitions_to_idle(self):
        """Test that start() transitions to IDLE state"""
        orchestrator = Orchestrator()
        orchestrator.start()

        assert orchestrator.get_state() == SystemState.IDLE

    def test_shutdown_transitions_to_shutdown(self):
        """Test that shutdown() transitions to SHUTDOWN state"""
        orchestrator = Orchestrator()
        orchestrator.shutdown()

        assert orchestrator.get_state() == SystemState.SHUTDOWN

    def test_register_message_handler(self):
        """Test message handler registration"""
        orchestrator = Orchestrator()
        handler_called = []

        def test_handler(msg):
            handler_called.append(msg)

        orchestrator.register_handler("test_message", test_handler)

        assert "test_message" in orchestrator.message_handlers
        assert test_handler in orchestrator.message_handlers["test_message"]

    def test_send_message_to_nonexistent_subsystem_raises_error(self):
        """Test that sending message to nonexistent subsystem raises KeyError"""
        orchestrator = Orchestrator()

        with pytest.raises(KeyError, match="not registered"):
            orchestrator.send_message("from", "to", {})
