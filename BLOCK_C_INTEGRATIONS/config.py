"""
КОНФИГУРАЦИЯ БЛОКА C
"""

import os
from typing import Dict, Any

class BlockCConfig:
    """Конфигурация для блока C (Интеграции)"""
    
    # Настройки API ФНС
    FNS_CONFIG = {
        'base_url': 'https://api-fns.ru',
        'timeout': 10,
        'retry_count': 3,
        'cache_ttl': 3600
    }
    
    # Настройки Protalk
    PROTALK_CONFIG = {
        'api_url': 'https://api.protalk.io',
        'webhook_path': '/webhook/protalk',
        'timeout': 10,
        'max_message_length': 4096
    }
    
    # Настройки Umnico
    UMNICO_CONFIG = {
        'api_url': 'https://umnico.com',
        'webhook_path': '/webhook/umnico',
        'widget_theme': 'light',
        'widget_position': 'bottom-right'
    }
    
    # Настройки Tilda
    TILDA_CONFIG = {
        'api_url': 'https://api.tildacdn.info',
        'partner_portal_url': 'https://партнер.дома-цены.рф',
        'form_submission_url': '/webhook/tilda'
    }
    
    # Настройки платежных систем
    PAYMENT_CONFIG = {
        'default_provider': 'yookassa',
        'currency': 'RUB',
        'tax_rate': 0.20,  # НДС 20%
        'invoice_template': 'default'
    }
    
    # Настройки email
    EMAIL_CONFIG = {
        'templates_dir': 'templates/email',
        'default_from': 'noreply@дома-цены.рф',
        'support_email': 'support@дома-цены.рф',
        'bounce_email': 'bounces@дома-цены.рф'
    }
    
    # Webhook конфигурация
    WEBHOOK_CONFIG = {
        'secret_header': 'X-Webhook-Secret',
        'signature_header': 'X-Signature',
        'timestamp_header': 'X-Timestamp',
        'timestamp_tolerance': 300  # 5 минут
    }
    
    @classmethod
    def get_fns_api_key(cls) -> str:
        """Получение ключа API ФНС"""
        return os.getenv('FNS_API_KEY', '')
    
    @classmethod
    def get_protalk_token(cls, bot_type: str = 'client') -> str:
        """Получение токена Protalk бота"""
        if bot_type == 'client':
            return os.getenv('PROTALK_CLIENT_BOT_TOKEN', '')
        elif bot_type == 'partner':
            return os.getenv('PROTALK_PARTNER_BOT_TOKEN', '')
        return ''
    
    @classmethod
    def get_umnico_credentials(cls) -> Dict[str, str]:
        """Получение учетных данных Umnico"""
        return {
            'api_key': os.getenv('UMNICO_API_KEY', ''),
            'widget_token': os.getenv('UMNICO_WIDGET_TOKEN', '')
        }
    
    @classmethod
    def get_tilda_credentials(cls) -> Dict[str, str]:
        """Получение учетных данных Tilda"""
        return {
            'public_key': os.getenv('TILDA_PUBLIC_KEY', ''),
            'secret_key': os.getenv('TILDA_SECRET_KEY', '')
        }
    
    @classmethod
    def get_payment_credentials(cls, provider: str = None) -> Dict[str, str]:
        """Получение учетных данных платежной системы"""
        provider = provider or cls.PAYMENT_CONFIG['default_provider']
        
        if provider == 'yookassa':
            return {
                'shop_id': os.getenv('YUKASSA_SHOP_ID', ''),
                'secret_key': os.getenv('YUKASSA_SECRET_KEY', '')
            }
        elif provider == 'cloudpayments':
            return {
                'public_id': os.getenv('CLOUDPAYMENTS_PUBLIC_ID', ''),
                'api_secret': os.getenv('CLOUDPAYMENTS_API_SECRET', '')
            }
        return {}
    
    @classmethod
    def get_email_credentials(cls) -> Dict[str, Any]:
        """Получение учетных данных email"""
        return {
            'smtp_host': os.getenv('SMTP_HOST', 'smtp.yandex.ru'),
            'smtp_port': int(os.getenv('SMTP_PORT', 587)),
            'smtp_user': os.getenv('SMTP_USER', ''),
            'smtp_password': os.getenv('SMTP_PASSWORD', ''),
            'email_from': os.getenv('EMAIL_FROM', 'noreply@дома-цены.рф')
        }
    
    @classmethod
    def get_webhook_secret(cls, service: str) -> str:
        """Получение секрета для вебхука"""
        return os.getenv(f'{service.upper()}_WEBHOOK_SECRET', '')
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Преобразование конфигурации в словарь"""
        return {
            'fns': cls.FNS_CONFIG,
            'protalk': cls.PROTALK_CONFIG,
            'umnico': cls.UMNICO_CONFIG,
            'tilda': cls.TILDA_CONFIG,
            'payment': cls.PAYMENT_CONFIG,
            'email': cls.EMAIL_CONFIG,
            'webhook': cls.WEBHOOK_CONFIG
        }
