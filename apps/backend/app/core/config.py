from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "A2UI Backend"
    version: str = "0.1.0"
    api_prefix: str = "/api"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:4200"]

    # --- LLM provider ---
    llm_provider: Literal["openai", "anthropic"] = "openai"
    llm_api_key: SecretStr = Field(..., description="API key do provedor LLM")
    llm_model: str = Field(..., description="Modelo LLM a utilizar")
    llm_temperature: float = Field(0.7, ge=0.0, le=2.0)
    llm_max_tokens: int = Field(1024, gt=0)

    @field_validator("llm_api_key")
    @classmethod
    def _validate_api_key(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("llm_api_key é obrigatório e não pode ser vazio")
        return value

    @field_validator("llm_model")
    @classmethod
    def _validate_model(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("llm_model é obrigatório e não pode ser vazio")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
