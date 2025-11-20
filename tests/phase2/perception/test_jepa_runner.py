"""
Unit tests for JEPA runner.

Tests the k-step imagination rollout simulation logic.
"""

import pytest

from logos_perception import JEPARunner, JEPAConfig


def test_jepa_runner_initialization():
    """Test JEPA runner can be initialized with default config."""
    runner = JEPARunner()
    assert runner.config.model_version == "jepa-v0.1"
    assert runner.config.embedding_dim == 768
    assert runner.config.use_hardware_sim is False


def test_jepa_runner_custom_config():
    """Test JEPA runner with custom configuration."""
    config = JEPAConfig(
        model_version="jepa-v0.2",
        embedding_dim=512,
        use_hardware_sim=False,
    )
    runner = JEPARunner(config)
    assert runner.config.model_version == "jepa-v0.2"
    assert runner.config.embedding_dim == 512


def test_simulate_generates_states():
    """Test that simulate generates the correct number of states."""
    runner = JEPARunner()
    
    result = runner.simulate(
        capability_id="test-capability",
        context={"entity_id": "test-entity"},
        k_steps=5,
    )
    
    assert result.process.capability_id == "test-capability"
    assert result.process.imagined is True
    assert result.process.horizon == 5
    assert len(result.states) == 5


def test_imagined_states_have_embeddings():
    """Test that imagined states include embedding vectors."""
    runner = JEPARunner()
    
    result = runner.simulate(
        capability_id="test-capability",
        context={},
        k_steps=3,
    )
    
    for state in result.states:
        assert state.embedding is not None
        assert len(state.embedding) == 768  # default embedding_dim
        assert isinstance(state.embedding, list)
        assert all(isinstance(x, float) for x in state.embedding)


def test_confidence_degrades_over_horizon():
    """Test that confidence decreases for later steps."""
    runner = JEPARunner()
    
    result = runner.simulate(
        capability_id="test-capability",
        context={},
        k_steps=5,
    )
    
    confidences = [state.confidence for state in result.states]
    
    # First state should have highest confidence
    assert confidences[0] == 1.0
    
    # Confidence should decrease with each step
    for i in range(1, len(confidences)):
        assert confidences[i] <= confidences[i - 1]
    
    # All confidences should be in valid range
    assert all(0.0 <= c <= 1.0 for c in confidences)


def test_imagined_states_have_correct_step_numbers():
    """Test that imagined states have sequential step numbers."""
    runner = JEPARunner()
    
    result = runner.simulate(
        capability_id="test-capability",
        context={},
        k_steps=4,
    )
    
    for i, state in enumerate(result.states):
        assert state.step == i


def test_simulation_metadata():
    """Test that simulation result includes correct metadata."""
    runner = JEPARunner()
    
    result = runner.simulate(
        capability_id="test-capability",
        context={"entity_id": "test-entity", "frame_id": "test-frame"},
        k_steps=3,
    )
    
    assert result.metadata["model_version"] == "jepa-v0.1"
    assert "use_hardware_sim" in result.metadata
    
    # Check process assumptions captured context
    assert result.process.assumptions["entity_id"] == "test-entity"
    assert result.process.assumptions["frame_id"] == "test-frame"


def test_hardware_sim_connection():
    """Test connecting and disconnecting hardware simulator."""
    runner = JEPARunner()
    
    assert runner.config.use_hardware_sim is False
    assert runner.config.hardware_sim_endpoint is None
    
    runner.connect_hardware_sim("http://localhost:11345")
    
    assert runner.config.use_hardware_sim is True
    assert runner.config.hardware_sim_endpoint == "http://localhost:11345"
    
    runner.disconnect_hardware_sim()
    
    assert runner.config.use_hardware_sim is False
    assert runner.config.hardware_sim_endpoint is None


def test_multiple_simulations_generate_different_results():
    """Test that multiple simulations generate different predictions."""
    runner = JEPARunner()
    
    result1 = runner.simulate(
        capability_id="test-capability",
        context={},
        k_steps=2,
    )
    
    result2 = runner.simulate(
        capability_id="test-capability",
        context={},
        k_steps=2,
    )
    
    # Different process UUIDs
    assert result1.process.uuid != result2.process.uuid
    
    # Different state UUIDs
    assert result1.states[0].uuid != result2.states[0].uuid
    
    # Different embeddings (stochastic generation)
    assert result1.states[0].embedding != result2.states[0].embedding
