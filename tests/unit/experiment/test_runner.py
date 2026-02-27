from logos_experiment.config import ExperimentConfig, PipelineStep
from logos_experiment.runner import ExperimentRunner


class DoublerAgent:
    def process(self, input_data):
        return input_data * 2


class AdderAgent:
    def process(self, input_data):
        return input_data + 1


def make_doubler(config):
    return DoublerAgent()


def make_adder(config):
    return AdderAgent()


def test_runner_arrange_creates_agents():
    config = ExperimentConfig(
        name="test",
        seed=42,
        pipeline=[
            PipelineStep(name="double", factory="unused", config={}),
            PipelineStep(name="add", factory="unused", config={}),
        ],
    )
    runner = ExperimentRunner(config)
    runner.arrange(factories={"double": make_doubler, "add": make_adder})
    assert len(runner.agents) == 2


def test_runner_act_runs_pipeline():
    config = ExperimentConfig(
        name="test",
        seed=42,
        pipeline=[
            PipelineStep(name="double", factory="unused", config={}),
            PipelineStep(name="add", factory="unused", config={}),
        ],
    )
    runner = ExperimentRunner(config)
    runner.arrange(factories={"double": make_doubler, "add": make_adder})
    results = runner.act(input_corpus=[5, 10, 15])
    # 5 * 2 + 1 = 11, 10 * 2 + 1 = 21, 15 * 2 + 1 = 31
    assert results == [11, 21, 31]


def test_runner_assert_captures_results():
    config = ExperimentConfig(
        name="test",
        seed=42,
        pipeline=[
            PipelineStep(name="double", factory="unused", config={}),
        ],
    )
    runner = ExperimentRunner(config)
    runner.arrange(factories={"double": make_doubler})
    runner.act(input_corpus=[5])
    artifacts = runner.assert_results()
    assert "results" in artifacts
    assert artifacts["results"] == [10]
    assert artifacts["config"] == config
