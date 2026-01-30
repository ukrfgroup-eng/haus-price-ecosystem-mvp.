"""
Функции безопасности для блока партнеров
Шифрование, хеширование, проверка доступа
"""

import hashlib
import hmac
import secrets
import string
from typing import Optional, Tuple
from datetime import datetime, timedelta
import jwt
from cryptography.fernet import Fernet
import base64
import os


class SecurityUtils:
    """Утилиты безопасности"""
    
    # Алгоритм для JWT
    JWT_ALGORITHM = "HS256"
    
    @staticmethod
    def generate_api_key(length: int = 32) -> str:
        """
        Генерация API ключа
        
        Args:
            length: Длина ключа
            
        Returns:
            Сгенерированный API ключ
        """
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Хеширование пароля
        
        Args:
            password: Пароль для хеширования
            salt: Соль (если None - генерируется новая)
            
        Returns:
            Tuple[хеш, соль]
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Используем PBKDF2 с SHA256
        dk = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # Количество итераций
        )
        
        return dk.hex(), salt
    
    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """
        Проверка пароля
        
        Args:
            password: Пароль для проверки
            password_hash: Ожидаемый хеш
            salt: Соль
            
        Returns:
            True если пароль верный
        """
        new_hash, _ = SecurityUtils.hash_password(password, salt)
        return hmac.compare_digest(new_hash, password_hash)
    
    @staticmethod
    def generate_jwt_token(
        payload: dict,
        secret_key: str,
        expires_in_hours: int = 24
    ) -> str:
        """
        Генерация JWT токена
        
        Args:
            payload: Данные для токена
            secret_key: Секретный ключ
            expires_in_hours: Время жизни токена в часах
            
        Returns:
            JWT токен
        """
        # Добавляем время истечения
        expiration = datetime.utcnow() + timedelta(hours=expires_in_hours)
        payload['exp'] = expiration
        
        # Генерируем токен
        token = jwt.encode(
            payload,
            secret_key,
            algorithm=SecurityUtils.JWT_ALGORITHM
        )
        
        return token
    
    @staticmethod
    def verify_jwt_token(token: str, secret_key: str) -> Optional[dict]:
        """
        Верификация JWT токена
        
        Args:
            token: JWT токен
            secret_key: Секретный ключ
            
        Returns:
            Декодированные данные или None при ошибке
        """
        try:
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=[SecurityUtils.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None  # Токен истек
        except jwt.InvalidTokenError:
            return None  # Невалидный токен
    
    @staticmethod
    def generate_encryption_key() -> str:
        """
        Генерация ключа для шифрования
        
        Returns:
            Ключ в формате base64
        """
        return Fernet.generate_key().decode('utf-8')
    
    @staticmethod
    def encrypt_data(data: str, key: str) -> str:
        """
        Шифрование данных
        
        Args:
            data: Данные для шифрования
            key: Ключ шифрования (base64)
            
        Returns:
            Зашифрованные данные (base64)
        """
        fernet = Fernet(key.encode('utf-8'))
        encrypted = fernet.encrypt(data.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')
    
    @staticmethod
    def decrypt_data(encrypted_data: str, key: str) -> Optional[str]:
        """
        Расшифровка данных
        
        Args:
            encrypted_data: Зашифрованные данные (base64)
            key: Ключ шифрования (base64)
            
        Returns:
            Расшифрованные данные или None при ошибке
        """
        try:
            fernet = Fernet(key.encode('utf-8'))
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception:
            return None
    
    @staticmethod
    def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
        """
        Маскировка чувствительных данных
        
        Args:
            data: Данные для маскировки
            visible_chars: Количество видимых символов
            
        Returns:
            Замаскированные данные
        """
        if len(data) <= visible_chars * 2:
            return '*' * len(data)
        
        visible_start = data[:visible_chars]
        visible_end = data[-visible_chars:]
        masked_middle = '*' * (len(data) - visible_chars * 2)
        
        return f"{visible_start}{masked_middle}{visible_end}"
    
    @staticmethod
    def validate_access_token(access_token: str, allowed_roles: list) -> Tuple[bool, Optional[dict]]:
        """
        Проверка токена доступа и ролей
        
        Args:
            access_token: Токен доступа
            allowed_roles: Разрешенные роли
            
        Returns:
            Tuple[валиден?, данные_токена]
        """
        # Заглушка - в реальности проверка JWT
        if not access_token:
            return False, None
        
        # Проверяем формат токена
        if not access_token.startswith("Bearer "):
            return False, None
        
        # Извлекаем токен
        token = access_token[7:]  # Убираем "Bearer "
        
        # В реальности здесь была бы проверка JWT
        # Сейчас возвращаем заглушку
        
        # Пример проверки (заглушка)
        if token == "valid_admin_token":
            return True, {
                "user_id": "admin123",
                "role": "admin",
                "permissions": ["read", "write", "delete"]
            }
        elif token == "valid_partner_token":
            return True, {
                "user_id": "partner456",
                "role": "partner",
                "permissions": ["read", "write"]
            }
        else:
            return False, None
    
    @staticmethod
    def generate_csrf_token() -> str:
        """
        Генерация CSRF токена
        
        Returns:
            CSRF токен
        """
        return secrets.token_hex(32)
    
    @staticmethod
    def verify_csrf_token(token: str, expected_token: str) -> bool:
        """
        Проверка CSRF токена
        
        Args:
            token: Токен для проверки
            expected_token: Ожидаемый токен
            
        Returns:
            True если токен верный
        """
        return hmac.compare_digest(token, expected_token)
    
    @staticmethod
    def sanitize_input(input_string: str) -> str:
        """
        Очистка пользовательского ввода
        
        Args:
            input_string: Строка для очистки
            
        Returns:
            Очищенная строка
        """
        import html
        
        # Экранируем HTML символы
        sanitized = html.escape(input_string)
        
        # Убираем лишние пробелы
        sanitized = ' '.join(sanitized.split())
        
        # Обрезаем длину (безопасный лимит)
        max_length = 1000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def check_password_strength(password: str) -> dict:
        """
        Проверка сложности пароля
        
        Args:
            password: Пароль для проверки
            
        Returns:
            Словарь с результатами проверки
        """
        results = {
            'is_strong': False,
            'length_ok': len(password) >= 8,
            'has_uppercase': any(c.isupper() for c in password),
            'has_lowercase': any(c.islower() for c in password),
            'has_digit': any(c.isdigit() for c in password),
            'has_special': any(c in '!@#$%^&*()-_=+[]{}|;:,.<>?/~`' for c in password),
            'score': 0,
            'suggestions': []
        }
        
        # Подсчет баллов
        score = 0
        if results['length_ok']:
            score += 1
        if results['has_uppercase']:
            score += 1
        if results['has_lowercase']:
            score += 1
        if results['has_digit']:
            score += 1
        if results['has_special']:
            score += 1
        
        results['score'] = score
        results['is_strong'] = score >= 4
        
        # Рекомендации
        if not results['length_ok']:
            results['suggestions'].append("Используйте не менее 8 символов")
        if not results['has_uppercase']:
            results['suggestions'].append("Добавьте заглавные буквы")
        if not results['has_lowercase']:
            results['suggestions'].append("Добавьте строчные буквы")
        if not results['has_digit']:
            results['suggestions'].append("Добавьте цифры")
        if not results['has_special']:
            results['suggestions'].append("Добавьте специальные символы (!@#$% и т.д.)")
        
        return results
    
    @staticmethod
    def generate_secure_filename(original_filename: str) -> str:
        """
        Генерация безопасного имени файла
        
        Args:
            original_filename: Оригинальное имя файла
            
        Returns:
            Безопасное имя файла
        """
        import uuid
        import os
        
        # Извлекаем расширение
        _, ext = os.path.splitext(original_filename)
        ext = ext.lower()
        
        # Генерируем UUID
        unique_id = str(uuid.uuid4())
        
        # Создаем безопасное имя
        safe_name = f"{unique_id}{ext}"
        
        return safe_name
    
    @staticmethod
    def validate_ip_address(ip_address: str) -> bool:
        """
        Проверка валидности IP адреса
        
        Args:
            ip_address: IP адрес для проверки
            
        Returns:
            True если IP валиден
        """
        import ipaddress
        
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def rate_limit_check(identifier: str, max_requests: int, window_seconds: int) -> bool:
        """
        Проверка лимита запросов
        
        Args:
            identifier: Идентификатор (IP, user_id)
            max_requests: Максимальное количество запросов
            window_seconds: Окно времени в секундах
            
        Returns:
            True если лимит не превышен
        """
        # Заглушка - в реальности используется Redis или другая быстрая БД
        # Сейчас всегда возвращаем True для демонстрации
        return True
