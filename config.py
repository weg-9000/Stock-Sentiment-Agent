import os
from pathlib import Path
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # === API KEY ===
    TWITTER_BEARER_TOKEN: str = Field(..., env="TWITTER_BEARER_TOKEN")
    ALPHA_VANTAGE_KEY: str   = Field(..., env="ALPHA_VANTAGE_KEY")
    HYPERCLOVA_X_API_KEY: str = Field(..., env="HYPERCLOVA_X_API_KEY")

    # === DATABASE ===
    POSTGRES_URL: str = "postgresql://user:password@localhost:5432/stock_sentiment"
    REDIS_URL: str    = "redis://localhost:6379/0"

    # === KAFKA ===
    KAFKA_BOOTSTRAP_SERVERS: list[str] = ["localhost:9092"]
    KAFKA_SECURITY_PROTOCOL: str = "PLAINTEXT"      # TODO: SASL_SSL on Ncloud

    # === VECTOR DB ===
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530

    # === CLOVA STUDIO ===
    CLOVA_ENDPOINT: str = "https://clovastudio.stream.ntruss.com"

    class Config:
        env_file = Path(__file__).parent / ".env"

settings = Settings()