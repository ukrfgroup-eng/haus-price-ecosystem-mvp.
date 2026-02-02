"""
Базовые настройки SQLAlchemy для Блока A
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

# Получаем настройки из переменных окружения или используем значения по умолчанию
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME", "haus_partners")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# Формируем URL для подключения
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создаем engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Включаем логирование SQL запросов (для разработки)
    pool_size=10,
    max_overflow=20
)

# Создаем сессию
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

def get_db():
    """Генератор сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Создание всех таблиц в БД"""
    Base.metadata.create_all(bind=engine)
    print("✅ Все таблицы созданы успешно!")
