"""HCG-specific exceptions."""


class HCGError(Exception):
    """Base exception for HCG client errors."""

    pass


class HCGConnectionError(HCGError):
    """Raised when connection to Neo4j fails."""

    pass


class HCGValidationError(HCGError):
    """Raised when SHACL validation fails."""

    def __init__(self, message: str, errors: list[str] | None = None) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            errors: List of specific validation errors
        """
        super().__init__(message)
        self.errors = errors or []


class HCGQueryError(HCGError):
    """Raised when a Cypher query fails."""

    pass


class HCGNotFoundError(HCGError):
    """Raised when a requested entity is not found."""

    pass
