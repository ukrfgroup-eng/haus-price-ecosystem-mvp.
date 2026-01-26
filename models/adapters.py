# models/adapters.py - адаптеры для существующих моделей

"""
Адаптеры для интеграции блока D с существующими моделями
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

try:
    from backend.models import Payment as ExistingPayment, Subscription as ExistingSubscription, db
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False

class PaymentAdapter:
    """Адаптер для работы с моделью Payment"""
    
    @staticmethod
    def to_block_d_format(payment: Any) -> Dict[str, Any]:
        """
        Преобразование существующего Payment в формат блока D
        
        Args:
            payment: Объект Payment
            
        Returns:
            Словарь в формате блока D
        """
        if not payment:
            return {}
        
        return {
            'payment_id': payment.id,
            'payment_number': payment.payment_number,
            'external_payment_id': payment.payment_system_id,
            'partner_id': payment.partner_id,
            'amount': payment.amount,
            'currency': payment.currency,
            'description': payment.description,
            'status': payment.status,
            'payment_system': payment.payment_system,
            'invoice_id': payment.invoice_data.get('invoice_id') if payment.invoice_data else None,
            'subscription_id': None,  # Нужна связь с подпиской
            'metadata': payment.invoice_data or {},
            'created_at': payment.created_at.isoformat() if payment.created_at else None,
            'updated_at': payment.updated_at.isoformat() if payment.updated_at else None,
            'paid_at': payment.paid_at.isoformat() if payment.paid_at else None,
            'refunded_amount': 0.0,  # Нужно добавить поле в модель
            'error_message': None  # Нужно добавить поле в модель
        }
    
    @staticmethod
    def from_block_d_format(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Преобразование данных из формата блока D в формат существующей модели
        
        Args:
            data: Данные в формате блока D
            
        Returns:
            Словарь для создания/обновления Payment
        """
        return {
            'payment_number': data.get('payment_number'),
            'partner_id': data.get('partner_id'),
            'amount': data.get('amount', 0),
            'currency': data.get('currency', 'RUB'),
            'status': data.get('status', 'pending'),
            'payment_type': data.get('payment_type', 'subscription'),
            'tariff_plan': data.get('tariff_code'),
            'description': data.get('description', ''),
            'invoice_data': data.get('metadata', {}),
            'payment_system': data.get('payment_system', 'yookassa'),
            'payment_system_id': data.get('external_payment_id'),
            'payment_url': data.get('payment_url'),
            'paid_at': datetime.fromisoformat(data['paid_at']) if data.get('paid_at') else None
        }

class SubscriptionAdapter:
    """Адаптер для работы с моделью Subscription"""
    
    @staticmethod
    def to_block_d_format(subscription: Any) -> Dict[str, Any]:
        """
        Преобразование существующей Subscription в формат блока D
        
        Args:
            subscription: Объект Subscription
            
        Returns:
            Словарь в формате блока D
        """
        if not subscription:
            return {}
        
        # Расчет оставшихся дней
        days_remaining = 0
        if subscription.expires_at:
            days_remaining = (subscription.expires_at - datetime.utcnow()).days
            days_remaining = max(0, days_remaining)
        
        return {
            'subscription_id': subscription.id,
            'partner_id': subscription.partner_id,
            'tariff_code': subscription.tariff_plan,
            'tariff_name': subscription.tariff_plan,  # Нужно преобразовать код в имя
            'billing_period': subscription.period or 'monthly',
            'status': subscription.status,
            'price': subscription.price,
            'currency': 'RUB',  # По умолчанию
            'start_date': subscription.starts_at.isoformat() if subscription.starts_at else None,
            'expires_at': subscription.expires_at.isoformat() if subscription.expires_at else None,
            'auto_renewal': subscription.auto_renewal,
            'next_billing_date': subscription.expires_at.isoformat() if subscription.expires_at else None,
            'cancelled_at': None,  # Нужно добавить поле
            'cancellation_reason': None,  # Нужно добавить поле
            'features': [],  # Нужно получать из тарифов
            'leads_included': subscription.leads_included,
            'payment_history': [],  # Нужно собирать из платежей
            'tariff_history': [],  # Нужно добавить поле
            'created_at': subscription.created_at.isoformat() if subscription.created_at else None,
            'updated_at': subscription.updated_at.isoformat() if subscription.updated_at else None,
            'days_remaining': days_remaining
        }
    
    @staticmethod
    def from_block_d_format(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Преобразование данных из формата блока D в формат существующей модели
        
        Args:
            data: Данные в формате блока D
            
        Returns:
            Словарь для создания/обновления Subscription
        """
        return {
            'partner_id': data.get('partner_id'),
            'tariff_plan': data.get('tariff_code'),
            'status': data.get('status', 'active'),
            'price': data.get('price', 0),
            'period': data.get('billing_period', 'monthly'),
            'leads_included': data.get('leads_included', 0),
            'starts_at': datetime.fromisoformat(data['start_date']) if data.get('start_date') else datetime.utcnow(),
            'expires_at': datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            'auto_renewal': data.get('auto_renewal', True)
        }
