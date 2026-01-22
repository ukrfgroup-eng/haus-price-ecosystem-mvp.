python
"""
Нагрузочные тесты
"""

import pytest
import concurrent.futures
from main import app
import json


class TestLoad:
    def test_multiple_registrations(self):
        """Тест множественной регистрации партнеров"""
        def register_partner(i):
            data = {
                "company_name": f"Company {i}",
                "inn": f"123456789{i:03d}",
                "contact_person": f"Person {i}",
                "phone": f"+799999999{i:02d}",
                "email": f"test{i}@test.com"
            }
            with app.test_client() as client:
                response = client.post('/api/v1/partners/register', json=data)
                return response.status_code
        
        # Тест 10 одновременных регистраций
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(register_partner, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # Проверяем, что все запросы обработаны
        assert all(code in [201, 400, 409] for code in results)
