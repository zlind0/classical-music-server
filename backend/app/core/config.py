from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Classical Music Player"

    DATABASE_URL: str = "postgresql+asyncpg://user:password@db:5432/musicdb"

    OPENAI_API_KEY: Optional[str] = "X"
    OPENAI_API_BASE: str = "http://192.168.1.4:11434/v1/"
    OPENAI_MODEL: str = "qwen3.5:9b"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    MUSIC_PATH: str = "/music"
    SECRET_KEY: str = "your-secret-key-change-me-in-production"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
