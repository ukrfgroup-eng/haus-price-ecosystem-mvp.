"""
Клиент для работы с API ФНС (Федеральная налоговая служба)
"""

import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class FNSClient:
    """Клиент для API ФНС"""
    
    def __init__(self, api_key: str = "", base_url: str = "https://api-fns.ru/api/"):
        """
        Инициализация клиента ФНС
        
        Args:
            api_key: Ключ API ФНС
            base_url: Базовый URL API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HausPrice-Ecosystem/1.0',
            'Accept': 'application/json'
        })
    
    def get_company_info(self, inn: str) -> Dict[str, Any]:
        """
        Получение основной информации о компании по ИНН
        
        Args:
            inn: ИНН компании (10 или 12 цифр)
            
        Returns:
            Информация о компании
        """
        endpoint = f"{self.base_url}egr"
        params = {
            'req': inn,
            'key': self.api_key
        }
        
        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Обработка ответа API ФНС
            if data.get('Items'):
                company_data = data['Items'][0]
                return {
                    'inn': inn,
                    'name': company_data.get('ЮЛ', {}).get('НаимСокрЮЛ') or 
                           company_data.get('ИП', {}).get('ФИОПолн'),
                    'legal_form': self._detect_legal_form(company_data),
                    'ogrn': company_data.get('ЮЛ', {}).get('ОГРН') or 
                           company_data.get('ИП', {}).get('ОГРНИП'),
                    'kpp': company_data.get('ЮЛ', {}).get('КПП'),
                    'address': company_data.get('ЮЛ', {}).get('Адрес') or 
                              company_data.get('ИП', {}).get('Адрес'),
                    'status': company_data.get('ЮЛ', {}).get('Статус') or 
                             company_data.get('ИП', {}).get('Статус'),
                    'registration_date': company_data.get('ЮЛ', {}).get('ДатаРег') or 
                                        company_data.get('ИП', {}).get('ДатаРег'),
                    'raw_data': company_data
                }
            else:
                return {
                    'inn': inn,
                    'error': 'Компания не найдена в ФНС',
                    'found': False
                }
                
        except requests.exceptions.Timeout:
            logger.error(f"FNS API timeout for INN: {inn}")
            return {
                'inn': inn,
                'error': 'Таймаут при запросе к ФНС',
                'found': False
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"FNS API error for INN {inn}: {str(e)}")
            return {
                'inn': inn,
                'error': f'Ошибка API ФНС: {str(e)}',
                'found': False
            }
    
    def check_inn_validity(self, inn: str) -> Dict[str, Any]:
        """
        Проверка валидности ИНН
        
        Args:
            inn: ИНН для проверки
            
        Returns:
            Результат проверки
        """
        # Если нет API ключа, используем базовую проверку
        if not self.api_key:
            return self._basic_inn_check(inn)
        
        # Иначе используем API ФНС
        company_info = self.get_company_info(inn)
        
        if company_info.get('found', True) and 'error' not in company_info:
            return {
                'is_valid': True,
                'inn': inn,
                'company_name': company_info.get('name'),
                'status': company_info.get('status'),
                'checked_via': 'fns_api'
            }
        else:
            return {
                'is_valid': False,
                'inn': inn,
                'error': company_info.get('error', 'ИНН не найден'),
                'checked_via': 'fns_api'
            }
    
    def get_extended_info(self, inn: str) -> Dict[str, Any]:
        """
        Получение расширенной информации о компании
        
        Args:
            inn: ИНН компании
            
        Returns:
            Расширенная информация
        """
        # Заглушка для расширенной информации
        # В реальности может использоваться другой endpoint
        
        basic_info = self.get_company_info(inn)
        
        if 'error' in basic_info:
            return basic_info
        
        # Добавляем дополнительную информацию
        extended_info = {
            **basic_info,
            'tax_debt': self._check_tax_debt(inn),
            'in_liquidation': self._check_liquidation(inn),
            'in_bankruptcy': self._check_bankruptcy(inn),
            'last_checked': datetime.utcnow().isoformat()
        }
        
        return extended_info
    
    def _basic_inn_check(self, inn: str) -> Dict[str, Any]:
        """Базовая проверка ИНН без API"""
        from ...utils.validators import validate_inn
        
        is_valid, error = validate_inn(inn)
        
        if is_valid:
            return {
                'is_valid': True,
                'inn': inn,
                'checked_via': 'local_validation',
                'note': 'Только проверка формата (API ключ не настроен)'
            }
        else:
            return {
                'is_valid': False,
                'inn': inn,
                'error': error,
                'checked_via': 'local_validation'
            }
    
    def _detect_legal_form(self, company_data: Dict[str, Any]) -> str:
        """Определение организационно-правовой формы"""
        if 'ЮЛ' in company_data:
            юл = company_data['ЮЛ']
            if 'НаимПолнЮЛ' in юл:
                if 'Общество с ограниченной ответственностью' in юл['НаимПолнЮЛ']:
                    return 'ООО'
                elif 'Акционерное общество' in юл['НаимПолнЮЛ']:
                    return 'АО'
                elif 'Закрытое акционерное общество' in юл['НаимПолнЮЛ']:
                    return 'ЗАО'
        elif 'ИП' in company_data:
            return 'ИП'
        
        return 'Не определено'
    
    def _check_tax_debt(self, inn: str) -> bool:
        """Проверка налоговой задолженности (заглушка)"""
        # В реальности - запрос к API ФНС о задолженностях
        return False
    
    def _check_liquidation(self, inn: str) -> bool:
        """Проверка на ликвидацию (заглушка)"""
        # В реальности - анализ статуса компании
        return False
    
    def _check_bankruptcy(self, inn: str) -> bool:
        """Проверка на банкротство (заглушка)"""
        # В реальности - проверка через API
        return False
    
    def test_connection(self) -> bool:
        """Тестирование подключения к API ФНС"""
        try:
            # Пробуем запросить тестовый ИНН
            test_inn = "7707083893"  # Яндекс
            result = self.get_company_info(test_inn)
            return 'error' not in result
        except Exception as e:
            logger.error(f"FNS connection test failed: {str(e)}")
            return False
