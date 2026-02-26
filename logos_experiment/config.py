from pydantic import BaseModel, Field


class PipelineStep(BaseModel):
    """One step in an experiment pipeline."""

    name: str
    factory: str  # dotted.path:function_name
    config: dict = Field(default_factory=dict)


class ExperimentConfig(BaseModel):
    """Full specification of an experiment."""

    name: str
    description: str = ""
    seed: int
    init_config: dict = Field(default_factory=dict)
    pipeline: list[PipelineStep]
    input_corpus: str = ""  # path or generator reference
    logging: dict = Field(default_factory=dict)
    evaluators: list[str] = Field(default_factory=list)
    comparison_baseline: str = ""
