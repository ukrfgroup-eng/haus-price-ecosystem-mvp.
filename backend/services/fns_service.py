"""
Минимальная версия для тестов
"""

class FNSVerificationService:
    def verify_inn(self, inn):
        return {
            'success': True,
            'data': {'ИНН': inn, 'Статус': 'действующая'}
        }
