"""
Pydantic models derived from the canonical Hermes OpenAPI contract.

These models ensure request/response validation against the contract defined in
contracts/hermes.openapi.yaml (Table 2, Section 3.4 of the LOGOS spec).
"""


from pydantic import BaseModel, Field


# /simple_nlp endpoint models
class SimpleNlpRequest(BaseModel):
    """Request model for Simple NLP Preprocessing endpoint."""

    text: str = Field(..., description="Text to process")
    operations: list[str] = Field(
        default=["tokenize"],
        description="List of NLP operations to perform",
    )


class PosTag(BaseModel):
    """Part-of-speech tag model."""

    token: str
    tag: str


class NamedEntity(BaseModel):
    """Named entity model."""

    text: str
    label: str
    start: int
    end: int


class SimpleNlpResponse(BaseModel):
    """Response model for Simple NLP Preprocessing endpoint."""

    tokens: list[str] | None = Field(None, description="Tokenized text (if requested)")
    pos_tags: list[PosTag] | None = Field(None, description="POS tags (if requested)")
    lemmas: list[str] | None = Field(None, description="Lemmatized tokens (if requested)")
    entities: list[NamedEntity] | None = Field(
        None, description="Named entities (if requested)"
    )


# /embed_text endpoint models
class EmbedTextRequest(BaseModel):
    """Request model for Text Embedding Generation endpoint."""

    text: str = Field(..., description="Text to embed")
    model: str = Field(default="default", description="Optional embedding model identifier")


class EmbedTextResponse(BaseModel):
    """Response model for Text Embedding Generation endpoint."""

    embedding: list[float] = Field(..., description="Vector embedding")
    dimension: int = Field(..., description="Embedding dimension")
    model: str = Field(..., description="Model used for embedding")
