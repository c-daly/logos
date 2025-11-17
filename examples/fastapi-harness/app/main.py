"""
Minimal FastAPI application demonstrating contract validation against the canonical
Hermes OpenAPI contract (contracts/hermes.openapi.yaml).

This is NOT a full service scaffold. This is a minimal validation harness that:
- Demonstrates how LOGOS OpenAPI contracts are used by a running app
- Validates request/response against the canonical contract
- Provides a foundation for automated contract testing

For full service scaffolding, see the logos-template repository.
"""


from fastapi import FastAPI, HTTPException

from .models import (
    EmbedTextRequest,
    EmbedTextResponse,
    SimpleNlpRequest,
    SimpleNlpResponse,
)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="Hermes API Contract Validation Harness",
        version="1.0.0",
        description=(
            "Minimal FastAPI harness demonstrating contract validation against "
            "the canonical LOGOS Hermes OpenAPI contract. "
            "See contracts/hermes.openapi.yaml (Table 2, Section 3.4)."
        ),
    )

    @app.get("/")
    async def root():
        """Root endpoint providing harness information."""
        return {
            "message": "LOGOS Hermes API Contract Validation Harness",
            "purpose": "Minimal example demonstrating contract-based validation",
            "note": "This is not a full service. See logos-template for scaffolding.",
            "endpoints": ["/simple_nlp", "/embed_text"],
        }

    @app.post("/simple_nlp", response_model=SimpleNlpResponse)
    async def simple_nlp(request: SimpleNlpRequest) -> SimpleNlpResponse:
        """
        Simple NLP Preprocessing endpoint.

        Demonstrates contract validation for the /simple_nlp endpoint
        defined in contracts/hermes.openapi.yaml.

        This is a mock implementation for validation purposes only.
        """
        # Validate operations are supported
        valid_operations = {"tokenize", "pos_tag", "lemmatize", "ner"}
        for op in request.operations:
            if op not in valid_operations:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid operation: {op}. Must be one of {valid_operations}",
                )

        # Mock response based on requested operations
        response_data = {}

        if "tokenize" in request.operations:
            # Simple whitespace tokenization for validation
            response_data["tokens"] = request.text.split()

        if "pos_tag" in request.operations:
            # Mock POS tags
            tokens = request.text.split()
            response_data["pos_tags"] = [
                {"token": token, "tag": "NN"} for token in tokens
            ]

        if "lemmatize" in request.operations:
            # Mock lemmatization (lowercase for demonstration)
            response_data["lemmas"] = [token.lower() for token in request.text.split()]

        if "ner" in request.operations:
            # Mock named entity (empty list for demonstration)
            response_data["entities"] = []

        return SimpleNlpResponse(**response_data)

    @app.post("/embed_text", response_model=EmbedTextResponse)
    async def embed_text(request: EmbedTextRequest) -> EmbedTextResponse:
        """
        Text Embedding Generation endpoint.

        Demonstrates contract validation for the /embed_text endpoint
        defined in contracts/hermes.openapi.yaml.

        This is a mock implementation for validation purposes only.
        """
        # Mock embedding generation
        # For validation, return a simple deterministic embedding based on text length
        text_length = len(request.text)
        mock_dimension = 384  # Common embedding dimension

        # Generate a simple mock embedding
        mock_embedding = [float(i * text_length % 100) / 100.0 for i in range(mock_dimension)]

        return EmbedTextResponse(
            embedding=mock_embedding, dimension=mock_dimension, model=request.model
        )

    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
