from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Industrial AI Foundry"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://foundry:foundry@postgres:5432/foundry"
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "change-me"
    redis_url: str = "redis://redis:6379/0"
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "foundry"
    minio_secret_key: str = "change-me"
    minio_secure: bool = False
    minio_document_bucket: str = "enterprise-documents"
    document_max_upload_bytes: int = 52_428_800

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
