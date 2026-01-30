
"""
Конфигурация блока партнерской базы данных
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """Конфигурация базы данных"""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", 5432))
    name: str = os.getenv("DB_NAME", "haus_partners")
    user: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASSWORD", "")
    pool_size: int = int(os.getenv("DB_POOL_SIZE", 10))
    echo: bool = os.getenv("DB_ECHO", "false").lower() == "true"


@dataclass
class FNSConfig:
    """Конфигурация интеграции с ФНС"""
    api_url: str = os.getenv("FNS_API_URL", "https://api-fns.ru/api/")
    api_key: str = os.getenv("FNS_API_KEY", "")
    timeout: int = int(os.getenv("FNS_TIMEOUT", 30))
    max_retries: int = int(os.getenv("FNS_MAX_RETRIES", 3))


@dataclass
class RedisConfig:
    """Конфигурация Redis для кеширования"""
    host: str = os.getenv("REDIS_HOST", "localhost")
    port: int = int(os.getenv("REDIS_PORT", 6379))
    password: Optional[str] = os.getenv("REDIS_PASSWORD")
    db: int = int(os.getenv("REDIS_DB", 0))


@dataclass
class APIConfig:
    """Конфигурация API"""
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", 5000))
    debug: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me")


@dataclass
class AppConfig:
    """Основная конфигурация приложения"""
    env: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Конфигурации подсистем
    database: DatabaseConfig = DatabaseConfig()
    fns: FNSConfig = FNSConfig()
    redis: RedisConfig = RedisConfig()
    api: APIConfig = APIConfig()
    
    # Настройки приложения
    partner_id_prefix: str = os.getenv("PARTNER_ID_PREFIX", "PART")
    verification_auto_approve_score: float = float(
        os.getenv("VERIFICATION_AUTO_APPROVE_SCORE", "80.0")
    )
    
    @property
    def is_development(self) -> bool:
        return self.env == "development"
    
    @property
    def is_production(self) -> bool:
        return self.env == "production"


# Создаем глобальный объект конфигурации
config = AppConfig()


def load_config():
    """Загрузка конфигурации"""
    return config


def get_database_url() -> str:
    """Получение URL для подключения к БД"""
    db = config.database
    return f"postgresql://{db.user}:{db.password}@{db.host}:{db.port}/{db.name}"
