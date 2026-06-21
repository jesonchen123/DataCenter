from dataclasses import dataclass
import os


def _get_env(name: str, default: str) -> str:
    return os.environ.get(name, default)


@dataclass(frozen=True)
class Settings:
    app_name: str = _get_env("APP_NAME", "chat-data-platform")
    app_env: str = _get_env("APP_ENV", "development")
    app_secret_key: str = _get_env("APP_SECRET_KEY", "change_me")
    database_url: str = _get_env(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/chat_data_platform",
    )
    redis_url: str = _get_env("REDIS_URL", "redis://localhost:6379/0")
    jwt_secret_key: str = _get_env("JWT_SECRET_KEY", "change_me")
    jwt_expire_minutes: int = int(_get_env("JWT_EXPIRE_MINUTES", "1440"))
    llm_api_base_url: str = _get_env("LLM_API_BASE_URL", "https://api.openai.com/v1")
    llm_api_key: str = _get_env("LLM_API_KEY", "your_api_key")
    llm_model_name: str = _get_env("LLM_MODEL_NAME", "gpt-4o-mini")
    llm_temperature: float = float(_get_env("LLM_TEMPERATURE", "0.2"))
    llm_max_tokens: int = int(_get_env("LLM_MAX_TOKENS", "2000"))
    llm_timeout: int = int(_get_env("LLM_TIMEOUT", "60"))


settings = Settings()
