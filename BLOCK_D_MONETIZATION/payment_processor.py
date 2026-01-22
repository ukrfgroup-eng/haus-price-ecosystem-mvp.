"""
ОБРАБОТЧИК ПЛАТЕЖЕЙ
Согласно ТЗ: ПРОЦЕСС ОПЛАТЫ
"""

import uuid
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from decimal import Decimal

logger = logging.getLogger(__name__)

class PaymentProcessor:
    """Обработчик платежей и подписок"""
    
    def __init__(self, payment_gateway=None):
        self.payment_gateway = payment_gateway
        
    def create_subscription(self, partner_code: str, tariff_plan: str, 
                           period: str = 'monthly') -> Dict[str, Any]:
        """Создание подписки для партнера"""
        try:
            # Получение информации о тарифе
            from .tariff_plans import TariffManager
            tariff_manager = TariffManager()
            
            tariff_info = tariff_manager.calculate_price(tariff_plan, period)
            if not tariff_info['success']:
                return tariff_info
            
            # Генерация уникального идентификатора платежа
            payment_id = f"PAY-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
            
            # Подготовка данных для платежного шлюза
            payment_data = {
                'amount': tariff_info['final_price'],
                'currency': tariff_info['currency'],
                'description': f"Подписка {tariff_plan} ({period}) для партнера {partner_code}",
                'metadata': {
                    'partner_code': partner_code,
                    'tariff_plan': tariff_plan,
                    'period': period,
                    'payment_id': payment_id,
                    'leads_limit': self._get_tariff_leads_limit(tariff_plan),
                    'features': self._get_tariff_features(tariff_plan)
                }
            }
            
            # Если есть платежный шлюз, создаем платеж
            if self.payment_gateway:
                result = self.payment_gateway.create_payment(**payment_data)
                if not result.get('success'):
                    return result
                
                payment_url = result.get('confirmation_url')
            else:
                # Заглушка для тестирования
                payment_url = f"https://payment.дома-цены.рф/pay/{payment_id}"
                result = {
                    'success': True,
                    'payment_id': payment_id,
                    'confirmation_url': payment_url
                }
            
            # Расчет дат подписки
            subscription_dates = self._calculate_subscription_dates(period)
            
            return {
                'success': True,
                'payment': {
                    'id': payment_id,
                    'amount': tariff_info['final_price'],
                    'currency': tariff_info['currency'],
                    'period': period,
                    'status': 'pending'
                },
                'subscription': {
                    'partner_code': partner_code,
                    'tariff_plan': tariff_plan,
                    'period': period,
                    'starts_at': subscription_dates['starts_at'],
                    'expires_at': subscription_dates['expires_at'],
                    'auto_renew': True
                },
                'payment_url': payment_url,
                'next_steps': [
                    'Оплатите счет по ссылке выше',
                    'После оплаты аккаунт будет активирован автоматически',
                    'На почту придет подтверждение оплаты'
                ]
            }
            
        except Exception as e:
            logger.error(f"Error creating subscription for {partner_code}: {e}")
            return {
                'success': False,
                'error': f'Ошибка создания подписки: {str(e)}'
            }
    
    def process_payment_webhook(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка вебхука об успешном платеже"""
        try:
            payment_id = payment_data.get('payment_id')
            status = payment_data.get('status')
            metadata = payment_data.get('metadata', {})
            
            logger.info(f"Processing payment webhook: {payment_id}, status={status}")
            
            if status == 'succeeded':
                partner_code = metadata.get('partner_code')
                tariff_plan = metadata.get('tariff_plan')
                period = metadata.get('period', 'monthly')
                
                if not partner_code or not tariff_plan:
                    return {
                        'success': False,
                        'error': 'Отсутствуют данные партнера в метаданных платежа'
                    }
                
                # Активация подписки
                activation_result = self.activate_subscription(
                    partner_code=partner_code,
                    tariff_plan=tariff_plan,
                    period=period,
                    payment_id=payment_id
                )
                
                if activation_result['success']:
                    # Отправка уведомления партнеру
                    self._send_activation_notification(partner_code, tariff_plan)
                    
                    return {
                        'success': True,
                        'action': 'subscription_activated',
                        'partner_code': partner_code,
                        'tariff_plan': tariff_plan,
                        'payment_id': payment_id,
                        'message': 'Подписка успешно активирована'
                    }
                else:
                    return activation_result
                
            elif status == 'failed':
                partner_code = metadata.get('partner_code')
                
                return {
                    'success': True,
                    'action': 'payment_failed',
                    'partner_code': partner_code,
                    'payment_id': payment_id,
                    'message': 'Платеж не прошел',
                    'next_steps': ['Попробуйте оплатить снова', 'Свяжитесь с поддержкой при повторных ошибках']
                }
            
            return {
                'success': True,
                'action': 'payment_processed',
                'payment_id': payment_id,
                'status': status,
                'message': 'Платеж обработан'
            }
            
        except Exception as e:
            logger.error(f"Error processing payment webhook: {e}")
            return {
                'success': False,
                'error': f'Ошибка обработки платежа: {str(e)}'
            }
    
    def activate_subscription(self, partner_code: str, tariff_plan: str,
                             period: str = 'monthly', payment_id: Optional[str] = None) -> Dict[str, Any]:
        """Активация подписки для партнера"""
        try:
            # Расчет дат подписки
            subscription_dates = self._calculate_subscription_dates(period)
            
            # Здесь должна быть логика обновления партнера в базе данных
            # Пока возвращаем результат активации
            
            from .tariff_plans import TARIFF_PLANS
            tariff_info = TARIFF_PLANS.get(tariff_plan, {})
            
            subscription_data = {
                'partner_code': partner_code,
                'tariff_plan': tariff_plan,
                'tariff_name': tariff_info.get('name', 'Неизвестный'),
                'period': period,
                'payment_id': payment_id,
                'activated_at': datetime.utcnow().isoformat(),
                'starts_at': subscription_dates['starts_at'],
                'expires_at': subscription_dates['expires_at'],
                'features': tariff_info.get('features', []),
                'leads_limit': tariff_info.get('leads_per_month', 0),
                'max_projects': tariff_info.get('max_active_projects', 0),
                'status': 'active'
            }
            
            logger.info(f"Subscription activated for {partner_code}: {tariff_plan}")
            
            return {
                'success': True,
                'subscription': subscription_data,
                'message': 'Подписка успешно активирована'
            }
            
        except Exception as e:
            logger.error(f"Error activating subscription for {partner_code}: {e}")
            return {
                'success': False,
                'error': f'Ошибка активации подписки: {str(e)}'
            }
    
    def cancel_subscription(self, partner_code: str, 
                           reason: Optional[str] = None) -> Dict[str, Any]:
        """Отмена подписки партнера"""
        try:
            # Здесь должна быть логика отмены в базе данных
            
            cancellation_data = {
                'partner_code': partner_code,
                'cancelled_at': datetime.utcnow().isoformat(),
                'reason': reason or 'По инициативе партнера',
                'effective_date': (datetime.utcnow() + timedelta(days=30)).isoformat(),  # До конца периода
                'refund_eligible': self._check_refund_eligibility(partner_code)
            }
            
            logger.info(f"Subscription cancelled for {partner_code}: {reason}")
            
            return {
                'success': True,
                'cancellation': cancellation_data,
                'message': 'Подписка будет отменена в конце текущего периода'
            }
            
        except Exception as e:
            logger.error(f"Error cancelling subscription for {partner_code}: {e}")
            return {
                'success': False,
                'error': f'Ошибка отмены подписки: {str(e)}'
            }
    
    def upgrade_subscription(self, partner_code: str, new_tariff: str,
                            period: str = 'monthly') -> Dict[str, Any]:
        """Обновление тарифного плана"""
        try:
            # Получение информации о текущем тарифе (в реальности из БД)
            current_tariff = 'free'  # Заглушка
            
            # Валидация апгрейда
            from .tariff_plans import TariffManager
            tariff_manager = TariffManager()
            
            validation = tariff_manager.validate_upgrade(current_tariff, new_tariff)
            if not validation['success']:
                return validation
            
            # Расчет доплаты
            prorated_amount = validation.get('prorated_amount', 0)
            
            if prorated_amount > 0:
                # Создание платежа за апгрейд
                upgrade_payment = self.create_subscription(partner_code, new_tariff, period)
                
                return {
                    'success': True,
                    'action': 'upgrade_payment_required',
                    'partner_code': partner_code,
                    'current_tariff': current_tariff,
                    'new_tariff': new_tariff,
                    'prorated_amount': prorated_amount,
                    'payment_data': upgrade_payment,
                    'message': 'Требуется оплата разницы тарифов'
                }
            else:
                # Бесплатный апгрейд (или даунгрейд с кредитом)
                return self.activate_subscription(partner_code, new_tariff, period)
                
        except Exception as e:
            logger.error(f"Error upgrading subscription for {partner_code}: {e}")
            return {
                'success': False,
                'error': f'Ошибка обновления подписки: {str(e)}'
            }
    
    def check_subscription_status(self, partner_code: str) -> Dict[str, Any]:
        """Проверка статуса подписки партнера"""
        try:
            # Здесь должна быть логика получения из базы данных
            # Пока возвращаем тестовые данные
            
            subscription_data = {
                'partner_code': partner_code,
                'tariff_plan': 'basic',
                'status': 'active',
                'activated_at': '2024-01-15T10:30:00Z',
                'expires_at': '2024-02-15T10:30:00Z',
                'auto_renew': True,
                'leads_used': 8,
                'leads_limit': 25,
                'leads_remaining': 17,
                'payment_method': 'card',
                'next_payment_date': '2024-02-15',
                'next_payment_amount': 5000
            }
            
            return {
                'success': True,
                'subscription': subscription_data,
                'is_active': subscription_data['status'] == 'active',
                'days_remaining': self._calculate_days_remaining(subscription_data['expires_at'])
            }
            
        except Exception as e:
            logger.error(f"Error checking subscription status for {partner_code}: {e}")
            return {
                'success': False,
                'error': f'Ошибка проверки статуса подписки: {str(e)}'
            }
    
    def process_refund(self, partner_code: str, amount: float,
                      reason: str) -> Dict[str, Any]:
        """Обработка возврата средств"""
        try:
            refund_id = f"REF-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
            
            # Здесь должна быть логика возврата через платежный шлюз
            
            refund_data = {
                'refund_id': refund_id,
                'partner_code': partner_code,
                'amount': amount,
                'currency': 'RUB',
                'reason': reason,
                'processed_at': datetime.utcnow().isoformat(),
                'status': 'pending'
            }
            
            logger.info(f"Refund initiated for {partner_code}: {amount} RUB")
            
            return {
                'success': True,
                'refund': refund_data,
                'message': 'Запрос на возврат средств принят',
                'processing_time': '3-10 рабочих дней'
            }
            
        except Exception as e:
            logger.error(f"Error processing refund for {partner_code}: {e}")
            return {
                'success': False,
                'error': f'Ошибка обработки возврата: {str(e)}'
            }
    
    def _calculate_subscription_dates(self, period: str) -> Dict[str, str]:
        """Расчет дат начала и окончания подписки"""
        now = datetime.utcnow()
        
        if period == 'yearly':
            expires_at = now + timedelta(days=365)
        elif period == 'quarterly':
            expires_at = now + timedelta(days=90)
        else:  # monthly
            expires_at = now + timedelta(days=30)
        
        return {
            'starts_at': now.isoformat(),
            'expires_at': expires_at.isoformat()
        }
    
    def _get_tariff_leads_limit(self, tariff_plan: str) -> int:
        """Получение лимита лидов для тарифа"""
        from .tariff_plans import TARIFF_PLANS
        return TARIFF_PLANS.get(tariff_plan, {}).get('leads_per_month', 0)
    
    def _get_tariff_features(self, tariff_plan: str) -> List[str]:
        """Получение возможностей тарифа"""
        from .tariff_plans import TARIFF_PLANS
        return TARIFF_PLANS.get(tariff_plan, {}).get('features', [])
    
    def _send_activation_notification(self, partner_code: str, tariff_plan: str):
        """Отправка уведомления об активации"""
        # В реальности здесь должен быть вызов email сервиса
        logger.info(f"Activation notification sent to {partner_code} for {tariff_plan}")
    
    def _check_refund_eligibility(self, partner_code: str) -> bool:
        """Проверка возможности возврата средств"""
        # В реальности здесь должна быть бизнес-логика
        return True
    
    def _calculate_days_remaining(self, expires_at: str) -> int:
        """Расчет оставшихся дней подписки"""
        try:
            expires_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            now = datetime.utcnow()
            delta = expires_date - now
            return max(0, delta.days)
        except:
            return 0
