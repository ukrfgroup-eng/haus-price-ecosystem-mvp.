"""
Конфигурация блока партнерской базы данных
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DatabaseConfig:
    """Конфигурация базы данных"""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", 5432))
    name: str = os.getenv("DB_NAME", "haus_partners")
    user: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASSWORD", "postgres")
    pool_size: int = int(os.getenv("DB_POOL_SIZE", 10))
    echo: bool = os.getenv("DB_ECHO", "false").lower() == "true"

@dataclass
class RedisConfig:
    """Конфигурация Redis для кеширования"""
    host: str = os.getenv("REDIS_HOST", "localhost")
    port: int = int(os.getenv("REDIS_PORT", 6379))
    password: Optional[str] = os.getenv("REDIS_PASSWORD", "redis123")
    db: int = int(os.getenv("REDIS_DB", 0))
    cache_ttl: int = int(os.getenv("CACHE_TTL", 3600))  # 1 час

@dataclass
class APIConfig:
    """Конфигурация API"""
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", 5000))
    debug: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    cors_origins: list = os.getenv("CORS_ORIGINS", "*").split(",")

@dataclass 
class AppConfig:
    """Основная конфигурация приложения"""
    env: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Конфигурации подсистем
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    api: APIConfig = APIConfig()
    
    # Настройки приложения
    partner_id_prefix: str = os.getenv("PARTNER_ID_PREFIX", "PART")
    verification_auto_approve_score: float = float(
        os.getenv("VERIFICATION_AUTO_APPROVE_SCORE", "80.0")
    )
    search_cache_enabled: bool = os.getenv("SEARCH_CACHE_ENABLED", "true").lower() == "true"
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", 10))
    
    @property
    def is_development(self) -> bool:
        return self.env == "development"
    
    @property
    def is_production(self) -> bool:
        return self.env == "production"

# Глобальный объект конфигурации
config = AppConfig()
