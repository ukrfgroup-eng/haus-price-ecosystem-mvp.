"""
Блок A: База партнеров + Верификация

Основной модуль для управления партнерами, верификации и поиска.
"""

__version__ = "1.0.0"
__author__ = "HausPrice Ecosystem Team"


from .config import config, load_config, get_database_url


# Экспортируем основные классы для удобного импорта
__all__ = [
    'config',
    'load_config',
    'get_database_url',
]
