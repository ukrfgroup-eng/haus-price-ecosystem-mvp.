"""
КОНФИГУРАЦИЯ БЛОКА A
"""

import os
from typing import Dict, Any

class BlockAConfig:
    """Конфигурация для блока A (База партнеров)"""
    
    # Настройки базы данных
    DATABASE_CONFIG = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 3600,
        'echo': False
    }
    
    # Настройки верификации
    VERIFICATION_CONFIG = {
        'inn_check_timeout': 10,  # секунд
        'max_retries': 3,
        'cache_ttl': 3600,  # кэширование результатов на 1 час
        'auto_verify_after_days': 7  # автоматическая верификация через 7 дней
    }
    
    # Настройки поиска
    SEARCH_CONFIG = {
        'default_per_page': 10,
        'max_per_page': 50,
        'default_sort': 'rating_desc',
        'search_timeout': 5
    }
    
    # Категории партнеров (согласно ТЗ)
    PARTNER_CATEGORIES = [
        'подрядчик',
        'производитель', 
        'продавец',
        'исполнитель'
    ]
    
    # Специализации (согласно ТЗ)
    SPECIALIZATIONS = [
        'каркасные дома',
        'кирпичные дома',
        'отделочные работы',
        'кровельные работы',
        'фундаменты',
        'электромонтаж',
        'сантехника',
        'окна и двери',
        'отопление и вентиляция',
        'ландшафтный дизайн'
    ]
    
    # Регионы работы
    REGIONS = [
        'Московская область',
        'Ленинградская область',
        'Краснодарский край',
        'Свердловская область',
        'Новосибирская область',
        'Республика Татарстан',
        'Ростовская область',
        'Челябинская область',
        'Нижегородская область',
        'Самарская область'
    ]
    
    @classmethod
    def get_database_url(cls) -> str:
        """Получение URL базы данных из переменных окружения"""
        return os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/haus_price_db')
    
    @classmethod
    def get_fns_api_key(cls) -> str:
        """Получение ключа API ФНС"""
        return os.getenv('FNS_API_KEY', '')
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Преобразование конфигурации в словарь"""
        return {
            'database': cls.DATABASE_CONFIG,
            'verification': cls.VERIFICATION_CONFIG,
            'search': cls.SEARCH_CONFIG,
            'categories': cls.PARTNER_CATEGORIES,
            'specializations': cls.SPECIALIZATIONS,
            'regions': cls.REGIONS
        }
