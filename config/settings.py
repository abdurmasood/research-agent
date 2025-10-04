from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Keys
    anthropic_api_key: str
    parallel_api_key: str

    # Model Configuration
    model_name: str = "claude-sonnet-4-5-20250929"
    model_temperature: float = 0.7
    max_tokens: int = 4096

    # Research Configuration
    max_subagents: int = 5
    min_subagents: int = 3
    parallel_max_results: int = 10
    parallel_max_chars: int = 6000
    parallel_processor: str = "base"

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/research.log"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
