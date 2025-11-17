"""
Unit tests for CWM-A (Abstract World Model) module

Tests cover:
- State initialization and management
- HCG update mechanism (stub)
- State query API
- Event emission
"""

from sophia.cwm_a import CWMAbstract, StateSnapshot


class TestCWMAbstract:
    """Test suite for CWMAbstract class"""

    def test_initialization(self):
        """Test CWM-A initializes with empty state"""
        cwm_a = CWMAbstract()
        assert cwm_a.current_state is None
        assert len(cwm_a.state_history) == 0
        assert len(cwm_a.event_listeners) == 0

    def test_update_from_hcg_creates_snapshot(self):
        """Test that update_from_hcg creates a StateSnapshot"""
        cwm_a = CWMAbstract()

        snapshot = cwm_a.update_from_hcg()

        assert isinstance(snapshot, StateSnapshot)
        assert cwm_a.current_state is snapshot

    def test_get_current_state(self):
        """Test getting current state"""
        cwm_a = CWMAbstract()

        assert cwm_a.get_current_state() is None

        cwm_a.update_from_hcg()
        assert cwm_a.get_current_state() is not None

    def test_query_state_returns_dict(self):
        """Test that query_state returns a dictionary"""
        cwm_a = CWMAbstract()
        cwm_a.update_from_hcg()

        result = cwm_a.query_state({"entity": "test"})

        assert isinstance(result, dict)

    def test_event_listener_registration(self):
        """Test event listener registration"""
        cwm_a = CWMAbstract()
        events_received = []

        def listener(snapshot):
            events_received.append(snapshot)

        cwm_a.register_event_listener(listener)
        cwm_a.update_from_hcg()

        assert len(events_received) == 1
        assert isinstance(events_received[0], StateSnapshot)

    def test_state_history(self):
        """Test that state history is maintained"""
        cwm_a = CWMAbstract()

        history = cwm_a.get_state_history()
        assert len(history) == 0

    def test_update_state_does_not_raise(self):
        """Test that update_state can be called without error"""
        cwm_a = CWMAbstract()
        cwm_a.update_from_hcg()

        # Should not raise an exception (stub implementation)
        cwm_a.update_state("entity_1", "property", "value")
