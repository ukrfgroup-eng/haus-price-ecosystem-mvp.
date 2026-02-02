"""
Тестовый скрипт для проверки настройки Блока A
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Тест импорта основных модулей"""
    print("🧪 Тест импорта модулей...")
    
    try:
        from models.base import Base, engine
        print("✅ models.base - OK")
        
        from models.partner_models import Partner, VerificationLog
        print("✅ models.partner_models - OK")
        
        from config import config
        print("✅ config - OK")
        
        from services.partner_manager import PartnerManager
        print("✅ services.partner_manager - OK")
        
        from api.routes import bp
        print("✅ api.routes - OK")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_database():
    """Тест подключения к базе данных"""
    print("\n🧪 Тест подключения к базе данных...")
    
    try:
        from models.base import engine
        with engine.connect() as conn:
            result = conn.execute("SELECT version()")
            version = result.fetchone()[0]
            print(f"✅ База данных: {version}")
            return True
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return False

def test_config():
    """Тест конфигурации"""
    print("\n🧪 Тест конфигурации...")
    
    try:
        from config import config
        print(f"✅ Режим: {config.env}")
        print(f"✅ Логирование: {config.log_level}")
        print(f"✅ API порт: {config.api.port}")
        print(f"✅ БД: {config.database.host}:{config.database.port}/{config.database.name}")
        return True
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестов настройки Блока A")
    print("="*50)
    
    tests = [
        test_imports,
        test_config,
        test_database
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "="*50)
    print(f"📊 Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("✅ Все тесты пройдены! Блок A готов к работе.")
    else:
        print("❌ Есть проблемы с настройкой.")
        sys.exit(1)
