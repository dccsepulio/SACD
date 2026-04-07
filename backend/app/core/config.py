from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SACD API"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite+pysqlite:///./sacd.db"
    cors_origins: str = "http://localhost:5173"
    results_dir: str = "./results"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
