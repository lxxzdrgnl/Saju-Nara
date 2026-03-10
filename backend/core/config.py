"""앱 설정 — pydantic-settings 기반 환경변수 관리."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Embedding / RAG
    embedding_provider: str = "gemini"
    embedding_model: str = "gemini-embedding-001"
    chroma_path: str = "./chroma_db"

    # DB (PostgreSQL)
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/sajubon"

    # Server
    port: int = 8000

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
