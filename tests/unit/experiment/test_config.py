from logos_experiment.config import ExperimentConfig, PipelineStep


def test_experiment_config_minimal():
    config = ExperimentConfig(
        name="test-experiment",
        seed=42,
        pipeline=[
            PipelineStep(name="step1", factory="module.path:make_agent", config={}),
        ],
    )
    assert config.name == "test-experiment"
    assert config.seed == 42
    assert len(config.pipeline) == 1


def test_experiment_config_defaults():
    config = ExperimentConfig(
        name="test",
        seed=0,
        pipeline=[],
    )
    assert config.description == ""
    assert config.init_config == {}
    assert config.logging == {}


def test_pipeline_step():
    step = PipelineStep(
        name="filter",
        factory="sophia.experiments.agents:make_filter",
        config={"alpha": 0.01},
    )
    assert step.name == "filter"
    assert step.config["alpha"] == 0.01
