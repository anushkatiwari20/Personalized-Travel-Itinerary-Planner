"""Application configuration and settings."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Supabase
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None

    # JWT
    secret_key: str = "dev-secret-change-me-in-production-please-32chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # AI Model
    ai_provider: str = "groq"  # groq, huggingface, ollama
    groq_api_key: Optional[str] = None
    groq_model: str = "openai/gpt-oss-120b"
    huggingface_api_key: Optional[str] = None
    huggingface_model: str = "mistralai/Mistral-7B-Instruct-v0.3"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # Server
    debug: bool = True
    environment: str = "development"
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"

    # Optional
    redis_url: Optional[str] = None
    log_level: str = "INFO"

    @property
    def supabase_configured(self) -> bool:
        def real(v):
            return bool(v) and not str(v).startswith("your")
        return real(self.supabase_url) and (real(self.supabase_service_role_key) or real(self.supabase_key))

    @property
    def cors_origins(self) -> list[str]:
        origins = {
            self.frontend_url.rstrip("/"),
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
        }
        return [o for o in origins if o]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
