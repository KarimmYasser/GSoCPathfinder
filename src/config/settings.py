"""Application settings loaded from environment variables."""

from enum import Enum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Supported LLM provider backends."""

    LOCAL = "local"
    REMOTE = "remote"


class Settings(BaseSettings):
    """Global application settings, loaded from .env file or environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    llm_provider: LLMProvider = LLMProvider.LOCAL
    llm_base_url: str = "http://localhost:1234/v1"
    llm_api_key: str = "lm-studio"
    llm_chat_model: str = "your-chat-model-name"

    # Embedding
    embed_base_url: str = "http://localhost:1234/v1"
    embed_api_key: str = "lm-studio"
    embed_model: str = "your-embed-model-name"
    embed_dimension: int = 768

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "pathfinder123"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_grpc_port: int = 6334

    # Data
    data_dir: Path = Path("./Data")

    # Agent
    top_n_results: int = 10
    embed_batch_size: int = 32


def get_settings() -> Settings:
    """Get cached application settings instance."""
    return Settings()
