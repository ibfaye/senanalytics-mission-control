"""
Application configuration — reads from environment variables with sensible defaults.
Load with: from app.config import settings
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All configuration values, loaded from environment / .env file."""

    # Server
    host: str = "0.0.0.0"
    port: int = 8001

    # PostgreSQL
    database_url: str = "postgresql://senanalytics:senanalytics_dev@localhost:5432/senanalytics"

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "senanalytics_dev"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Frontend (for CORS)
    frontend_origin: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# Singleton
settings = Settings()
