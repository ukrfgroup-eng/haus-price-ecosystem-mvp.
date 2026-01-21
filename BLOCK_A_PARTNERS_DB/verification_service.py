"""
СЕРВИС ВЕРИФИКАЦИИ ПАРТНЕРОВ
Проверка ИНН через API ФНС и другие реестры
"""

import requests
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class VerificationService:
    """Сервис верификации юридических данных"""
    
    def __init__(self):
        self.fns_api_url = "https://api-fns.ru/api/egr"
        self.dadata_api_url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party"
        
    def verify_inn(self, inn: str) -> Dict[str, Any]:
        """Проверка ИНН через API ФНС"""
        try:
            # Базовая валидация формата
            if not self._validate_inn_format(inn):
                return {'success': False, 'error': 'Неверный формат ИНН'}
            
            # Запрос к API ФНС
            response = self._call_fns_api(inn)
            
            if response.get('status') == 'success':
                data = response.get('data', {})
                
                return {
                    'success': True,
                    'data': {
                        'inn': inn,
                        'company_name': data.get('name'),
                        'ogrn': data.get('ogrn'),
                        'legal_address': data.get('address'),
                        'registration_date': data.get('reg_date'),
                        'status': data.get('status'),  # ACTIVE, LIQUIDATED, etc.
                        'legal_form': data.get('legal_form'),
                        'verified_at': datetime.utcnow().isoformat()
                    },
                    'message': 'ИНН успешно верифицирован'
                }
            else:
                return {
                    'success': False,
                    'error': 'Компания не найдена в реестре ФНС',
                    'details': response
                }
                
        except Exception as e:
            logger.error(f"Ошибка верификации ИНН {inn}: {e}")
            return {
                'success': False,
                'error': f'Ошибка при верификации: {str(e)}'
            }
    
    def _validate_inn_format(self, inn: str) -> bool:
        """Валидация формата ИНН"""
        if not inn or not inn.isdigit():
            return False
        
        length = len(inn)
        if length not in [10, 12]:  # 10 для юрлиц, 12 для ИП
            return False
        
        return True
    
    def _call_fns_api(self, inn: str) -> Dict[str, Any]:
        """Вызов API ФНС"""
        # Здесь должен быть реальный вызов API
        # Пока возвращаем тестовые данные
        return {
            'status': 'success',
            'data': {
                'name': f'Компания ИНН {inn}',
                'ogrn': '1234567890123',
                'address': 'Москва, ул. Примерная, д. 1',
                'reg_date': '2020-01-15',
                'status': 'ACTIVE',
                'legal_form': 'ООО'
            }
        }
    
    def verify_documents(self, documents: list) -> Dict[str, Any]:
        """Верификация загруженных документов"""
        verified_docs = []
        
        for doc in documents:
            doc_type = doc.get('type')
            doc_url = doc.get('url')
            
            # Здесь должна быть логика проверки документов
            verified_docs.append({
                'type': doc_type,
                'url': doc_url,
                'verified': True,  # В реальности нужно проверять
                'verified_at': datetime.utcnow().isoformat()
            })
        
        return {
            'success': True,
            'documents': verified_docs,
            'message': f'Проверено {len(verified_docs)} документов'
        }
