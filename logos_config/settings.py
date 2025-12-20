"""Base configuration models for LOGOS services.

All config classes support environment variable overrides via pydantic-settings.
Priority: env var > explicit arg > default

These are base models - individual repos may extend them with additional fields.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Neo4jConfig(BaseSettings):
    """Neo4j connection configuration.

    Env vars: NEO4J_HOST, NEO4J_HTTP_PORT, NEO4J_BOLT_PORT, NEO4J_USER, NEO4J_PASSWORD

    Example:
        >>> config = Neo4jConfig(password="secret")
        >>> config.uri
        'bolt://localhost:7687'

        # With env vars set:
        # NEO4J_HOST=neo4j-service NEO4J_BOLT_PORT=7688
        >>> config = Neo4jConfig(password="secret")
        >>> config.uri
        'bolt://neo4j-service:7688'
    """

    model_config = SettingsConfigDict(env_prefix="NEO4J_")

    host: str = Field(default="localhost")
    http_port: int = Field(default=7474)
    bolt_port: int = Field(default=7687)
    user: str = Field(default="neo4j")
    password: str = Field(...)  # REQUIRED - no default for secrets

    @property
    def uri(self) -> str:
        """Return the bolt:// connection URI."""
        return f"bolt://{self.host}:{self.bolt_port}"

    @property
    def http_url(self) -> str:
        """Return the HTTP API URL."""
        return f"http://{self.host}:{self.http_port}"


class MilvusConfig(BaseSettings):
    """Milvus connection configuration.

    Env vars: MILVUS_HOST, MILVUS_PORT, MILVUS_COLLECTION_NAME

    Example:
        >>> config = MilvusConfig()
        >>> config.port
        19530

        # With env vars set:
        # MILVUS_PORT=37530
        >>> config = MilvusConfig()
        >>> config.port
        37530
    """

    model_config = SettingsConfigDict(env_prefix="MILVUS_")

    host: str = Field(default="localhost")
    port: int = Field(default=19530)
    collection_name: str = Field(default="embeddings")


class ServiceConfig(BaseSettings):
    """Generic service configuration.

    This is a base class - subclass with a specific env_prefix for each service.

    Env vars (with default prefix): SERVICE_HOST, SERVICE_PORT, SERVICE_API_KEY

    Example:
        >>> class MyServiceConfig(ServiceConfig):
        ...     model_config = SettingsConfigDict(env_prefix="MY_SERVICE_")
        ...
        >>> config = MyServiceConfig(port=8080)
    """

    model_config = SettingsConfigDict(env_prefix="SERVICE_")

    host: str = Field(default="localhost")
    port: int = Field(...)  # REQUIRED - varies by service
    api_key: str | None = Field(default=None)
