cat > __init__.py << 'EOF'
"""
Блок D - Система монетизации
==================================
Автоматизированная система платной регистрации, подписок,
генерации счетов и аналитики доходов.
"""

__version__ = "1.0.0"
__author__ = "HAUS Price Ecosystem Team"
__status__ = "Development"

# Экспортируем основные классы
from .payment_processor import PaymentProcessor
from .subscription_manager import SubscriptionManager
from .tariff_service import TariffService
from .invoice_generator import InvoiceGenerator
from .revenue_analytics import RevenueAnalytics
from .notification_service import NotificationService

__all__ = [
    'PaymentProcessor',
    'SubscriptionManager', 
    'TariffService',
    'InvoiceGenerator',
    'RevenueAnalytics',
    'NotificationService',
]
EOF
