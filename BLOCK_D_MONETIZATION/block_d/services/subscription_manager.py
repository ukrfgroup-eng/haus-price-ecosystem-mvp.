cat > BLOCK_D_MONETIZATION/block_d/services/subscription_manager.py << 'EOF'
"""
SubscriptionManager - управление подписками для блока D
"""

from datetime import datetime, timedelta

class SubscriptionManager:
    """Менеджер подписок блока D"""
    
    def __init__(self, config, tariff_service):
        self.config = config
        self.tariff_service = tariff_service
        self._subscriptions = {}
        print("✅ SubscriptionManager инициализирован")
    
    def create_subscription(self, partner_id, tariff_code, billing_period='monthly'):
        """Создание подписки"""
        tariff = self.tariff_service.get_tariff(tariff_code)
        if not tariff:
            raise ValueError(f"Тариф {tariff_code} не найден")
        
        subscription_id = f"sub_{partner_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        start_date = datetime.now()
        
        # Рассчитываем дату истечения
        if billing_period == 'monthly':
            expires_at = start_date + timedelta(days=30)
        elif billing_period == 'quarterly':
            expires_at = start_date + timedelta(days=90)
        else:  # yearly
            expires_at = start_date + timedelta(days=365)
        
        subscription = {
            'subscription_id': subscription_id,
            'partner_id': partner_id,
            'tariff_code': tariff_code,
            'tariff_name': tariff['name'],
            'billing_period': billing_period,
            'status': 'active',
            'price': tariff['price_monthly'],
            'start_date': start_date.isoformat(),
            'expires_at': expires_at.isoformat(),
            'auto_renewal': True,
            'created_at': datetime.now().isoformat()
        }
        
        self._subscriptions[subscription_id] = subscription
        print(f"✅ Создана подписка: {subscription_id}")
        return subscription
    
    def get_subscription(self, subscription_id):
        """Получение подписки"""
        return self._subscriptions.get(subscription_id)
    
    def get_partner_subscription(self, partner_id):
        """Получение подписки партнера"""
        for sub in self._subscriptions.values():
            if sub['partner_id'] == partner_id and sub['status'] == 'active':
                return sub
        return None
EOF
