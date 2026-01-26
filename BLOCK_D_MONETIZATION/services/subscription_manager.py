cat > services/subscription_manager.py << 'EOF'
"""
SubscriptionManager - управление подписками для блока D
Версия: 1.0.0
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class SubscriptionStatus(Enum):
    """Статусы подписок для блока D"""
    ACTIVE = 'active'
    EXPIRED = 'expired'
    CANCELLED = 'cancelled'
    SUSPENDED = 'suspended'
    PENDING = 'pending'

class SubscriptionManager:
    """Менеджер подписок блока D"""
    
    def __init__(self, config, tariff_service):
        """
        Инициализация менеджера подписок блока D
        
        Args:
            config: Конфигурация блока D
            tariff_service: Сервис тарифов блока D
        """
        self.config = config
        self.tariff_service = tariff_service
        
        # Хранилище подписок (в production - БД)
        self._subscriptions = {}
        logger.info("SubscriptionManager блока D инициализирован")
    
    def create_subscription(self, partner_id: str, tariff_code: str,
                           billing_period: str = 'monthly',
                           auto_renewal: bool = True) -> Dict[str, Any]:
        """
        Создание новой подписки (блок D)
        
        Args:
            partner_id: ID партнера
            tariff_code: Код тарифа (start/professional/business)
            billing_period: Период оплаты
            auto_renewal: Автопродление
            
        Returns:
            Информация о подписке
        """
        try:
            # Получаем тариф
            tariff = self.tariff_service.get_tariff(tariff_code)
            if not tariff:
                raise ValueError(f"Тариф {tariff_code} не найден в блоке D")
            
            # Генерируем ID подписки
            subscription_id = f"sub_d_{partner_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Рассчитываем даты
            start_date = datetime.utcnow()
            expires_at = self._calculate_expiry_date(start_date, billing_period)
            
            # Получаем цену
            price = self._get_price_for_period(tariff, billing_period)
            
            # Создаем подписку блока D
            subscription = {
                'subscription_id': subscription_id,
                'partner_id': partner_id,
                'tariff_code': tariff_code,
                'tariff_name': tariff.get('name', tariff_code),
                'billing_period': billing_period,
                'status': SubscriptionStatus.ACTIVE.value,
                'price': price,
                'currency': tariff.get('currency', 'RUB'),
                'start_date': start_date.isoformat(),
                'expires_at': expires_at.isoformat(),
                'auto_renewal': auto_renewal,
                'next_billing_date': expires_at.isoformat(),
                'features': tariff.get('features', []),
                'leads_included': tariff.get('leads_included', 0),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'source': 'block_d'  # Метка, что это подписка блока D
            }
            
            # Сохраняем
            self._subscriptions[subscription_id] = subscription
            
            logger.info(f"Блок D: Создана подписка {subscription_id} для партнера {partner_id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Блок D: Ошибка создания подписки: {e}")
            raise
    
    def get_subscription(self, subscription_id: str) -> Optional[Dict]:
        """
        Получение подписки блока D
        
        Args:
            subscription_id: ID подписки
            
        Returns:
            Подписка или None
        """
        return self._subscriptions.get(subscription_id)
    
    def get_partner_subscription(self, partner_id: str) -> Optional[Dict]:
        """
        Получение активной подписки партнера (блок D)
        
        Args:
            partner_id: ID партнера
            
        Returns:
            Активная подписка или None
        """
        for subscription in self._subscriptions.values():
            if (subscription['partner_id'] == partner_id and 
                subscription['status'] == SubscriptionStatus.ACTIVE.value):
                return subscription
        return None
    
    def cancel_subscription(self, partner_id: str, reason: str = '') -> bool:
        """
        Отмена подписки (блок D)
        
        Args:
            partner_id: ID партнера
            reason: Причина отмены
            
        Returns:
            bool: Успешность отмены
        """
        subscription = self.get_partner_subscription(partner_id)
        if not subscription:
            logger.warning(f"Блок D: Активная подписка партнера {partner_id} не найдена")
            return False
        
        subscription_id = subscription['subscription_id']
        subscription['status'] = SubscriptionStatus.CANCELLED.value
        subscription['cancelled_at'] = datetime.utcnow().isoformat()
        subscription['cancellation_reason'] = reason
        subscription['updated_at'] = datetime.utcnow().isoformat()
        
        logger.info(f"Блок D: Отменена подписка {subscription_id}")
        return True
    
    def check_expiring_subscriptions(self, days_before: int = 3) -> List[Dict]:
        """
        Проверка подписок, срок действия которых истекает (блок D)
        
        Args:
            days_before: За сколько дней проверять
            
        Returns:
            Список подписок, которые скоро истекают
        """
        expiring = []
        now = datetime.utcnow()
        
        for subscription in self._subscriptions.values():
            if subscription['status'] != SubscriptionStatus.ACTIVE.value:
                continue
            
            expires_at = datetime.fromisoformat(subscription['expires_at'])
            days_until_expire = (expires_at - now).days
            
            if 0 <= days_until_expire <= days_before:
                expiring.append({
                    'subscription': subscription,
                    'days_until_expire': days_until_expire,
                    'partner_id': subscription['partner_id']
                })
        
        logger.info(f"Блок D: Найдено {len(expiring)} подписок, истекающих в течение {days_before} дней")
        return expiring
    
    def renew_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Продление подписки (блок D)
        
        Args:
            subscription_id: ID подписки
            
        Returns:
            Обновленная подписка
        """
        subscription = self._subscriptions.get(subscription_id)
        if not subscription:
            raise ValueError(f"Блок D: Подписка {subscription_id} не найдена")
        
        # Получаем тариф
        tariff = self.tariff_service.get_tariff(subscription['tariff_code'])
        
        # Обновляем даты
        current_expires = datetime.fromisoformat(subscription['expires_at'])
        period_days = self._get_period_days(subscription['billing_period'])
        new_expires = current_expires + timedelta(days=period_days)
        
        # Обновляем подписку
        subscription['expires_at'] = new_expires.isoformat()
        subscription['next_billing_date'] = new_expires.isoformat()
        subscription['renewed_at'] = datetime.utcnow().isoformat()
        subscription['updated_at'] = datetime.utcnow().isoformat()
        
        logger.info(f"Блок D: Продлена подписка {subscription_id} до {new_expires.date()}")
        return subscription
    
    def _calculate_expiry_date(self, start_date: datetime, billing_period: str) -> datetime:
        """Расчет даты истечения"""
        period_days = self._get_period_days(billing_period)
        return start_date + timedelta(days=period_days)
    
    def _get_period_days(self, billing_period: str) -> int:
        """Получить количество дней в периоде"""
        periods = {
            'monthly': 30,
            'quarterly': 90,
            'yearly': 365
        }
        return periods.get(billing_period, 30)
    
    def _get_price_for_period(self, tariff: Dict, billing_period: str) -> float:
        """Получить цену для периода"""
        price_key = f"price_{billing_period}"
        return tariff.get(price_key, tariff.get('price_monthly', 0))

# Экспорт
__all__ = ['SubscriptionManager', 'SubscriptionStatus']
EOF
