from typing import Any, Dict, Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator, AnyHttpUrl

class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "VerseForge"
    API_V1_STR: str = "/api/v1"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 天
    
    # 数据库配置
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_USER: str = "verseforge"
    POSTGRES_PASSWORD: str = "verseforge"
    POSTGRES_DB: str = "verseforge"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    # Redis配置
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Kafka配置
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:29092"
    
    # 事件总线配置
    EVENT_BUS_IMPLEMENTATION: str = "kafka"  # 可选值: "kafka", "redis", "memory"
    
    # Milvus配置
    MILVUS_HOST: str = "milvus"
    MILVUS_PORT: int = 19530
    
    # Celery配置
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    
    # CORS配置
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"

# 创建设置实例
settings = Settings()