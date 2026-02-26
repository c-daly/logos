from logos_experiment.agent import AgentDefinition


class SimpleAgent:
    """Minimal agent that doubles its input."""

    def process(self, input_data):
        return input_data * 2


def test_agent_satisfies_protocol():
    agent = SimpleAgent()
    assert isinstance(agent, AgentDefinition)


def test_agent_process():
    agent = SimpleAgent()
    assert agent.process(5) == 10
