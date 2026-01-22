python
"""
Тесты для блока A: База партнеров + Верификация
"""

import pytest
from backend.models import Partner
from backend.services.fns_service import FNSVerificationService


class TestPartnerRegistration:
    def test_partner_creation(self):
        """Тест создания партнера"""
        partner = Partner(
            company_name="Тестовая компания",
            inn="123456789012",
            verification_status="pending"
        )
        assert partner.company_name == "Тестовая компания"
        assert partner.inn == "123456789012"
        assert partner.verification_status == "pending"
