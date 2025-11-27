"""Configuration for HCG client using Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class HCGConfig(BaseSettings):
    """Configuration for HCG client.

    Configuration can be provided via environment variables or directly.
    Environment variables use the prefix specified in model_config.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Neo4j connection settings
    neo4j_uri: str = Field(
        default="bolt://localhost:7687",
        description="Neo4j Bolt URI",
        alias="NEO4J_URI",
    )
    neo4j_user: str = Field(
        default="neo4j",
        description="Neo4j username",
        alias="NEO4J_USER",
    )
    neo4j_password: str = Field(
        default="password",
        description="Neo4j password",
        alias="NEO4J_PASSWORD",
    )
    neo4j_database: str = Field(
        default="neo4j",
        description="Neo4j database name",
        alias="NEO4J_DATABASE",
    )

    # Connection pool settings
    max_connection_pool_size: int = Field(
        default=50,
        description="Maximum connection pool size",
        alias="HCG_MAX_POOL_SIZE",
    )

    # Retry settings
    retry_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of retry attempts for transient failures",
        alias="HCG_RETRY_ATTEMPTS",
    )
    retry_min_wait: float = Field(
        default=2.0,
        description="Minimum wait time between retries (seconds)",
        alias="HCG_RETRY_MIN_WAIT",
    )
    retry_max_wait: float = Field(
        default=10.0,
        description="Maximum wait time between retries (seconds)",
        alias="HCG_RETRY_MAX_WAIT",
    )

    # SHACL validation settings
    shacl_enabled: bool = Field(
        default=True,
        description="Enable SHACL validation for write operations",
        alias="HCG_SHACL_ENABLED",
    )
    shacl_shapes_path: str | None = Field(
        default=None,
        description="Path to custom SHACL shapes file",
        alias="HCG_SHACL_SHAPES_PATH",
    )


# Convenience function for creating config from environment
def load_config() -> HCGConfig:
    """Load HCG configuration from environment variables.

    Returns:
        HCGConfig instance populated from environment
    """
    return HCGConfig()
