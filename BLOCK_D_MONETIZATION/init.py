"""
БЛОК D: СИСТЕМА МОНЕТИЗАЦИИ
Реализация платной регистрации и подписки для партнеров
"""

__version__ = "1.0.0"
__description__ = "Система монетизации и управления подписками"

from .tariff_plans import TARIFF_PLANS, TariffManager
from .payment_processor import PaymentProcessor
from .subscription_manager import SubscriptionManager
from .invoice_generator import InvoiceGenerator
from .revenue_analytics import RevenueAnalytics

__all__ = [
    'TARIFF_PLANS',
    'TariffManager',
    'PaymentProcessor',
    'SubscriptionManager',
    'InvoiceGenerator',
    'RevenueAnalytics'
]
