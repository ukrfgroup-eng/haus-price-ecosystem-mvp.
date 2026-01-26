cat > services/__init__.py << 'EOF'
"""
Сервисы блока D - система монетизации
"""

from .payment_processor import PaymentProcessor, PaymentStatus
from .subscription_manager import SubscriptionManager, SubscriptionStatus
from .tariff_service import TariffService
from .revenue_analytics import RevenueAnalytics

__all__ = [
    'PaymentProcessor',
    'PaymentStatus',
    'SubscriptionManager',
    'SubscriptionStatus',
    'TariffService',
    'RevenueAnalytics'
]
EOF
