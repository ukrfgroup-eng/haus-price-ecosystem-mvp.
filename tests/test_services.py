python
"""
Тесты сервисов
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.services import (
    fns_service, invoice_generator, 
    revenue_analytics, subscription_manager
)


class TestFnsService:
    """Тесты сервиса ФНС"""
    
    @patch('backend.services.fns_service.requests.get')
    def test_verify_inn_success(self, mock_get):
        """Тест успешной проверки ИНН"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "data": {
                "ИНН": "123456789012",
                "Статус": "действующая"
            }
        }
        mock_get.return_value = mock_response
        
        service = fns_service.FNSVerificationService()
        result = service.verify_inn("123456789012")
        
        assert result['success'] == True
        assert result['data']['ИНН'] == "123456789012"
    
    @patch('backend.services.fns_service.requests.get')
    def test_verify_inn_failure(self, mock_get):
        """Тест неудачной проверки ИНН"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        service = fns_service.FNSVerificationService()
        result = service.verify_inn("invalid_inn")
        
        assert result['success'] == False
        assert 'error' in result


class TestInvoiceGenerator:
    """Тесты генератора счетов"""
    
    def test_generate_invoice_number(self):
        """Тест генерации номера счета"""
        generator = invoice_generator.InvoiceGenerator()
        
        with patch('backend.services.invoice_generator.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "240101"
            mock_datetime.now.return_value.replace.return_value = "2024-01-01"
            
            with patch('backend.services.invoice_generator.Payment') as mock_payment:
                mock_query = Mock()
                mock_filter = Mock()
                mock_count = Mock()
                mock_count.count.return_value = 5
                mock_filter.filter.return_value = mock_count
                mock_query.filter.return_value = mock_filter
                mock_payment.query = mock_query
                
                invoice_number = generator.generate_invoice_number("TEST001")
                
                assert invoice_number.startswith("INV-")
                assert "240101" in invoice_number
                assert "TEST001" in invoice_number


class TestRevenueAnalytics:
    """Тесты аналитики доходов"""
    
    @patch('backend.services.revenue_analytics.Payment')
    def test_get_monthly_revenue(self, mock_payment):
        """Тест расчета месячного дохода"""
        analytics = revenue_analytics.RevenueAnalytics()
        
        # Мокаем платежи
        mock_payment1 = Mock()
        mock_payment1.amount = 5000.00
        mock_payment1.created_at = "2024-01-15"
        mock_payment1.tariff_plan = "professional"
        
        mock_payment2 = Mock()
        mock_payment2.amount = 15000.00
        mock_payment2.created_at = "2024-01-20"
        mock_payment2.tariff_plan = "business"
        
        with patch('backend.services.revenue_analytics.db.session') as mock_session:
            mock_query = Mock()
            mock_filter = Mock()
            mock_filter.filter.return_value.all.return_value = [mock_payment1, mock_payment2]
            mock_query.filter.return_value = mock_filter
            mock_session.query.return_value = mock_query
            
            result = analytics.get_monthly_revenue(2024, 1)
            
            assert result is not None
            assert result['total_revenue'] == 20000.00
            assert result['payment_count'] == 2


def test_service_initialization():
    """Тест инициализации всех сервисов"""
    # Проверяем, что все сервисы можно создать
    services = [
        fns_service.FNSVerificationService,
        invoice_generator.InvoiceGenerator,
        revenue_analytics.RevenueAnalytics,
        subscription_manager.SubscriptionManager
    ]
    
    for service_class in services:
        try:
            instance = service_class()
            assert instance is not None
        except Exception as e:
            pytest.fail(f"Не удалось инициализировать {service_class.__name__}: {e}")
