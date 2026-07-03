"""
LabhArth AI — Configuration Management
========================================
Centralized configuration using Pydantic Settings.
Loads values from environment variables and .env files.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- Application ---
    app_name: str = Field(default="LabhArth AI", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # --- Google / Gemini ---
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    gemini_model: str = Field(default="gemini-3.1-flash-lite", alias="GEMINI_MODEL")

    # --- PostgreSQL (Neon) ---
    database_url: str = Field(
        default="postgresql+asyncpg://localhost/labharth",
        alias="DATABASE_URL",
    )
    database_pool_size: int = Field(default=5, alias="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=10, alias="DATABASE_MAX_OVERFLOW")

    # --- Qdrant Cloud ---
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: str = Field(default="", alias="QDRANT_API_KEY")
    qdrant_collection_name: str = Field(
        default="government_schemes", alias="QDRANT_COLLECTION_NAME"
    )

    # --- RAG Retrieval ---
    rag_top_k: int = Field(default=5, alias="RAG_TOP_K")
    rag_similarity_threshold: float = Field(default=0.50, alias="RAG_SIMILARITY_THRESHOLD")
    rag_embedding_model: str = Field(default="gemini-embedding-001", alias="RAG_EMBEDDING_MODEL")
    rag_timeout_seconds: float = Field(default=10.0, alias="RAG_TIMEOUT_SECONDS")
    rag_max_retries: int = Field(default=3, alias="RAG_MAX_RETRIES")

    # --- Security ---
    secret_key: str = Field(
        default="change-this-to-a-random-secret-key", alias="SECRET_KEY"
    )
    allowed_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        alias="ALLOWED_ORIGINS",
    )
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")

    # --- MCP Server ---
    mcp_server_host: str = Field(default="0.0.0.0", alias="MCP_SERVER_HOST")
    mcp_server_port: int = Field(default=8001, alias="MCP_SERVER_PORT")

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse comma-separated origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton — call this instead of instantiating Settings directly."""
    return Settings()
