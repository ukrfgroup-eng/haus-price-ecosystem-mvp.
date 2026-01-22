"""
МЕНЕДЖЕР ПОДПИСОК
Управление подписками партнеров
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class SubscriptionStatus(Enum):
    """Статусы подписки"""
    ACTIVE = "active"
    PENDING = "pending"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    TRIAL = "trial"

@dataclass
class Subscription:
    """Модель подписки"""
    id: str
    partner_code: str
    tariff_plan: str
    status: SubscriptionStatus
    starts_at: datetime
    expires_at: datetime
    auto_renew: bool
    payment_method: Optional[str] = None
    payment_id: Optional[str] = None
    leads_used: int = 0
    leads_limit: int = 0
    features: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        data = asdict(self)
        data['status'] = self.status.value
        data['starts_at'] = self.starts_at.isoformat()
        data['expires_at'] = self.expires_at.isoformat()
        return data
    
    @property
    def is_active(self) -> bool:
        """Проверка активности подписки"""
        now = datetime.utcnow()
        return (self.status == SubscriptionStatus.ACTIVE and 
                self.starts_at <= now <= self.expires_at)
    
    @property
    def days_remaining(self) -> int:
        """Количество оставшихся дней"""
        if not self.is_active:
            return 0
        
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def leads_remaining(self) -> int:
        """Количество оставшихся лидов"""
        return max(0, self.leads_limit - self.leads_used)

class SubscriptionManager:
    """Менеджер для управления подписками"""
    
    def __init__(self):
        # В реальности здесь будет подключение к базе данных
        self.subscriptions = {}
        self._load_tariff_data()
    
    def _load_tariff_data(self):
        """Загрузка данных о тарифах"""
        from .tariff_plans import TARIFF_PLANS
        self.tariffs = TARIFF_PLANS
    
    def create_subscription(self, partner_code: str, tariff_plan: str,
                           payment_id: str, period: str = 'monthly') -> Dict[str, Any]:
        """Создание новой подписки"""
        try:
            # Проверка существующей подписки
            existing = self.get_subscription(partner_code)
            if existing and existing['status'] == 'active':
                return {
                    'success': False,
                    'error': 'У партнера уже есть активная подписка'
                }
            
            # Получение данных тарифа
            tariff = self.tariffs.get(tariff_plan)
            if not tariff:
                return {'success': False, 'error': 'Тариф не найден'}
            
            # Расчет дат
            dates = self._calculate_dates(period)
            
            # Создание подписки
            subscription_id = f"SUB-{datetime.now().strftime('%y%m%d')}-{partner_code}"
            
            subscription = Subscription(
                id=subscription_id,
                partner_code=partner_code,
                tariff_plan=tariff_plan,
                status=SubscriptionStatus.ACTIVE,
                starts_at=dates['starts_at'],
                expires_at=dates['expires_at'],
                auto_renew=True,
                payment_id=payment_id,
                leads_limit=tariff['leads_per_month'],
                features=tariff['features']
            )
            
            # Сохранение
            self.subscriptions[partner_code] = subscription
            
            logger.info(f"Subscription created: {subscription_id} for {partner_code}")
            
            return {
                'success': True,
                'subscription': subscription.to_dict(),
                'message': 'Подписка успешно создана'
            }
            
        except Exception as e:
            logger.error(f"Error creating subscription for {partner_code}: {e}")
            return {
                'success': False,
                'error': f'Ошибка создания подписки: {str(e)}'
            }
    
    def get_subscription(self, partner_code: str) -> Optional[Dict[str, Any]]:
        """Получение подписки партнера"""
        subscription = self.subscriptions.get(partner_code)
        if subscription:
            return subscription.to_dict()
        
        # В реальности здесь будет запрос к базе данных
        # Пока возвращаем тестовые данные если нет в памяти
        
        return {
            'id': f"SUB-TEST-{partner_code}",
            'partner_code': partner_code,
            'tariff_plan': 'free',
            'status': 'active',
            'starts_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(days=365)).isoformat(),
            'auto_renew': False,
            'leads_used': 0,
            'leads_limit': 3,
            'features': ['basic_listing', 'email_notifications'],
            'days_remaining': 365,
            'leads_remaining': 3
        }
    
    def update_subscription(self, partner_code: str, 
                           updates: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление подписки"""
        try:
            subscription = self.subscriptions.get(partner_code)
            if not subscription:
                return {'success': False, 'error': 'Подписка не найдена'}
            
            # Обновление полей
            for key, value in updates.items():
                if hasattr(subscription, key):
                    setattr(subscription, key, value)
            
            logger.info(f"Subscription updated for {partner_code}")
            
            return {
                'success': True,
                'subscription': subscription.to_dict(),
                'message': 'Подписка обновлена'
            }
            
        except Exception as e:
            logger.error(f"Error updating subscription for {partner_code}: {e}")
            return {
                'success': False,
                'error': f'Ошибка обновления подписки: {str(e)}'
            }
    
    def cancel_subscription(self, partner_code: str, 
                           immediate: bool = False) -> Dict[str, Any]:
        """Отмена подписки"""
        try:
            subscription = self.subscriptions.get(partner_code)
            if not subscription:
                return {'success': False, 'error': 'Подписка не найдена'}
            
            if immediate:
                subscription.status = SubscriptionStatus.CANCELLED
                subscription.expires_at = datetime.utcnow()
                message = 'Подписка немедленно отменена'
            else:
                subscription.auto_renew = False
                message = 'Автопродление отключено'
            
            logger.info(f"Subscription cancelled for {partner_code}")
            
            return {
                'success': True,
                'subscription': subscription.to_dict(),
                'message': message
            }
            
        except Exception as e:
            logger.error(f"Error cancelling subscription for {partner_code}: {e}")
            return {
                'success': False,
                'error': f'Ошибка отмены подписки: {str(e)}'
            }
    
    def renew_subscription(self, partner_code: str, 
                          payment_id: str) -> Dict[str, Any]:
        """Продление подписки"""
        try:
            subscription = self.subscriptions.get(partner_code)
            if not subscription:
                return {'success': False, 'error': 'Подписка не найдена'}
            
            # Расчет новой даты окончания
            current_expiry = subscription.expires_at
            if current_expiry < datetime.utcnow():
                current_expiry = datetime.utcnow()
            
            # Продление на месяц (можно сделать настраиваемым)
            new_expiry = current_expiry + timedelta(days=30)
            
            subscription.expires_at = new_expiry
            subscription.payment_id = payment_id
            subscription.status = SubscriptionStatus.ACTIVE
            
            # Сброс счетчика лидов
            subscription.leads_used = 0
            
            logger.info(f"Subscription renewed for {partner_code} until {new_expiry}")
            
            return {
                'success': True,
                'subscription': subscription.to_dict(),
                'message': 'Подписка успешно продлена'
            }
            
        except Exception as e:
            logger.error(f"Error renewing subscription for {partner_code}: {e}")
            return {
                'success': False,
                'error': f'Ошибка продления подписки: {str(e)}'
            }
    
    def record_lead_usage(self, partner_code: str) -> Dict[str, Any]:
        """Запись использования лида"""
        try:
            subscription = self.subscriptions.get(partner_code)
            if not subscription:
                return {'success': False, 'error': 'Подписка не найдена'}
            
            # Проверка лимита
            if subscription.leads_used >= subscription.leads_limit:
                return {
                    'success': False,
                    'error': 'Лимит лидов исчерпан',
                    'leads_used': subscription.leads_used,
                    'leads_limit': subscription.leads_limit
                }
            
            # Увеличение счетчика
            subscription.leads_used += 1
            
            logger.info(f"Lead usage recorded for {partner_code}: {subscription.leads_used}/{subscription.leads_limit}")
            
            return {
                'success': True,
                'leads_used': subscription.leads_used,
                'leads_remaining': subscription.leads_remaining,
                'leads_limit': subscription.leads_limit,
                'message': 'Использование лида записано'
            }
            
        except Exception as e:
            logger.error(f"Error recording lead usage for {partner_code}: {e}")
            return {
                'success': False,
                'error': f'Ошибка записи использования лида: {str(e)}'
            }
    
    def check_expired_subscriptions(self) -> List[Dict[str, Any]]:
        """Проверка истекших подписок"""
        expired = []
        now = datetime.utcnow()
        
        for partner_code, subscription in self.subscriptions.items():
            if subscription.expires_at < now and subscription.status == SubscriptionStatus.ACTIVE:
                subscription.status = SubscriptionStatus.EXPIRED
                expired.append(subscription.to_dict())
                logger.info(f"Subscription expired for {partner_code}")
        
        return expired
    
    def send_renewal_reminders(self, days_before: int = 7) -> List[Dict[str, Any]]:
        """Отправка напоминаний о продлении"""
        reminders = []
        now = datetime.utcnow()
        
        for partner_code, subscription in self.subscriptions.items():
            if not subscription.auto_renew:
                continue
            
            days_remaining = subscription.days_remaining
            
            if days_remaining == days_before:
                reminder_data = {
                    'partner_code': partner_code,
                    'days_remaining': days_remaining,
                    'expires_at': subscription.expires_at.isoformat(),
                    'tariff_plan': subscription.tariff_plan
                }
                reminders.append(reminder_data)
                
                # Здесь должна быть отправка email/уведомления
                logger.info(f"Renewal reminder sent to {partner_code}: {days_remaining} days remaining")
        
        return reminders
    
    def upgrade_tariff(self, partner_code: str, new_tariff: str) -> Dict[str, Any]:
        """Обновление тарифного плана"""
        try:
            subscription = self.subscriptions.get(partner_code)
            if not subscription:
                return {'success': False, 'error': 'Подписка не найдена'}
            
            # Проверка нового тарифа
            new_tariff_data = self.tariffs.get(new_tariff)
            if not new_tariff_data:
                return {'success': False, 'error': 'Новый тариф не найден'}
            
            # Обновление данных подписки
            old_tariff = subscription.tariff_plan
            subscription.tariff_plan = new_tariff
            subscription.leads_limit = new_tariff_data['leads_per_month']
            subscription.features = new_tariff_data['features']
            
            # Пропорциональный расчет (упрощенный)
            # В реальности здесь должна быть сложная логика расчета
            
            logger.info(f"Tariff upgraded for {partner_code}: {old_tariff} -> {new_tariff}")
            
            return {
                'success': True,
                'subscription': subscription.to_dict(),
                'message': f'Тариф обновлен с {old_tariff} на {new_tariff}'
            }
            
        except Exception as e:
            logger.error(f"Error upgrading tariff for {partner_code}: {e}")
            return {
                'success': False,
                'error': f'Ошибка обновления тарифа: {str(e)}'
            }
    
    def get_subscription_analytics(self, partner_code: str) -> Dict[str, Any]:
        """Получение аналитики по подписке"""
        subscription = self.subscriptions.get(partner_code)
        if not subscription:
            return {'success': False, 'error': 'Подписка не найдена'}
        
        subscription_dict = subscription.to_dict()
        
        analytics = {
            'subscription': subscription_dict,
            'usage': {
                'leads_used': subscription.leads_used,
                'leads_remaining': subscription.leads_remaining,
                'leads_utilization': round((subscription.leads_used / subscription.leads_limit * 100) if subscription.leads_limit > 0 else 0, 1),
                'days_active': (datetime.utcnow() - subscription.starts_at).days,
                'days_remaining': subscription.days_remaining,
                'auto_renew': subscription.auto_renew
            },
            'value': {
                'cost_per_lead': round(subscription_dict.get('price', 0) / subscription.leads_limit, 2) if subscription.leads_limit > 0 else 0,
                'features_count': len(subscription.features),
                'active_features': subscription.features
            }
        }
        
        return {'success': True, 'analytics': analytics}
    
    def _calculate_dates(self, period: str) -> Dict[str, datetime]:
        """Расчет дат начала и окончания"""
        now = datetime.utcnow()
        
        if period == 'yearly':
            expires_at = now + timedelta(days=365)
        elif period == 'quarterly':
            expires_at = now + timedelta(days=90)
        else:  # monthly
            expires_at = now + timedelta(days=30)
        
        return {
            'starts_at': now,
            'expires_at': expires_at
        }
