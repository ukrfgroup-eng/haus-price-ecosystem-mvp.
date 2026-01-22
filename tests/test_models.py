python
"""
Тесты моделей данных
"""

import pytest
from datetime import datetime
from backend.models import (
    db, Partner, PartnerVerificationLog, 
    Payment, Subscription, Lead, CustomerRequest
)


class TestPartnerModel:
    """Тесты модели Partner"""
    
    def test_create_partner(self):
        """Тест создания партнера"""
        partner = Partner(
            partner_id="TEST001",
            company_name="Тестовая компания",
            inn="123456789012",
            verification_status="pending"
        )
        
        assert partner.partner_id == "TEST001"
        assert partner.company_name == "Тестовая компания"
        assert partner.inn == "123456789012"
        assert partner.verification_status == "pending"
        assert partner.is_active == False
        assert partner.subscription_type == "free"
    
    def test_partner_to_dict(self):
        """Тест сериализации партнера в словарь"""
        partner = Partner(
            partner_id="TEST002",
            company_name="Компания ООО",
            inn="123456789013"
        )
        
        data = partner.to_dict()
        
        assert isinstance(data, dict)
        assert data['partner_id'] == "TEST002"
        assert data['company_name'] == "Компания ООО"
        assert 'created_at' in data


class TestPaymentModel:
    """Тесты модели Payment"""
    
    def test_create_payment(self):
        """Тест создания платежа"""
        payment = Payment(
            payment_number="INV-20240101-001",
            partner_id="TEST001",
            amount=5000.00,
            currency="RUB",
            status="pending"
        )
        
        assert payment.payment_number == "INV-20240101-001"
        assert payment.partner_id == "TEST001"
        assert payment.amount == 5000.00
        assert payment.currency == "RUB"
        assert payment.status == "pending"
    
    def test_payment_status_transitions(self):
        """Тест переходов статуса платежа"""
        payment = Payment(
            payment_number="INV-20240101-002",
            partner_id="TEST001",
            amount=3000.00
        )
        
        # Изначально pending
        assert payment.status == "pending"
        
        # Меняем статус
        payment.status = "completed"
        assert payment.status == "completed"


class TestSubscriptionModel:
    """Тесты модели Subscription"""
    
    def test_create_subscription(self):
        """Тест создания подписки"""
        from datetime import datetime, timedelta
        
        subscription = Subscription(
            partner_id="TEST001",
            tariff_plan="professional",
            price=5000.00,
            period="monthly",
            leads_included=15,
            starts_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        assert subscription.partner_id == "TEST001"
        assert subscription.tariff_plan == "professional"
        assert subscription.price == 5000.00
        assert subscription.period == "monthly"
        assert subscription.leads_included == 15
        assert subscription.status == "active"
        assert subscription.auto_renewal == True
    
    def test_subscription_days_remaining(self):
        """Тест расчета оставшихся дней подписки"""
        from datetime import datetime, timedelta
        
        subscription = Subscription(
            partner_id="TEST001",
            tariff_plan="professional",
            price=5000.00,
            starts_at=datetime.utcnow() - timedelta(days=10),
            expires_at=datetime.utcnow() + timedelta(days=20)
        )
        
        days = subscription.days_remaining
        assert 19 <= days <= 20  # Примерно 20 дней осталось


@pytest.fixture
def init_database(app):
    """Фикстура для инициализации базы данных"""
    with app.app_context():
        db.create_all()
        yield
        db.drop_all()


def test_database_connection(app, init_database):
    """Тест подключения к базе данных"""
    with app.app_context():
        # Пробуем выполнить простой запрос
        result = db.session.execute("SELECT 1").fetchone()
        assert result[0] == 1
