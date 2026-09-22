from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./piyasa.db"
    app_env: str = "development"
    data_provider: str = "demo"
    demo_auth: bool = True
    firebase_project_id: str = ""
    worker_interval_seconds: int = 60
    quote_max_age_seconds: int = 900
    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"
    daily_llm_limit: int = 20
    expo_push_url: str = "https://exp.host/--/api/v2/push/send"


@lru_cache
def get_settings() -> Settings:
    return Settings()

