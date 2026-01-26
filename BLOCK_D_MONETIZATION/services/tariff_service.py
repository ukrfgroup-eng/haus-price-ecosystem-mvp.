cat > services/tariff_service.py << 'EOF'
"""
TariffService - управление тарифными планами
"""

import logging
from typing import Dict, Any, List, Optional
from copy import deepcopy

logger = logging.getLogger(__name__)

class TariffService:
    """Сервис управления тарифными планами"""
    
    def __init__(self, config):
        """
        Инициализация сервиса тарифов
        
        Args:
            config: Конфигурация блока D
        """
        self.config = config
        self.tariffs = config.TARIFF_PLANS
        self._validate_tariffs()
    
    def _validate_tariffs(self):
        """Валидация тарифных планов"""
        required_fields = ['code', 'name', 'price_monthly', 'features']
        
        for code, tariff in self.tariffs.items():
            for field in required_fields:
                if field not in tariff:
                    logger.warning(f"Тариф {code} не содержит поле {field}")
            
            # Проверяем, что код тарифа соответствует ключу
            if tariff.get('code') != code:
                logger.warning(f"Код тарифа {tariff.get('code')} не совпадает с ключом {code}")
    
    def get_tariff(self, tariff_code: str) -> Optional[Dict]:
        """
        Получение тарифа по коду
        
        Args:
            tariff_code: Код тарифа
            
        Returns:
            Тариф или None
        """
        tariff = self.tariffs.get(tariff_code)
        if tariff:
            return deepcopy(tariff)  # Возвращаем копию, чтобы не менять оригинал
        return None
    
    def get_all_tariffs(self, active_only: bool = True) -> List[Dict]:
        """
        Получение всех тарифов
        
        Args:
            active_only: Только активные тарифы
            
        Returns:
            Список тарифов
        """
        tariffs = []
        for code, tariff in self.tariffs.items():
            if active_only and not tariff.get('is_active', True):
                continue
            tariffs.append(deepcopy(tariff))
        
        # Сортируем по цене
        return sorted(tariffs, key=lambda x: x.get('price_monthly', 0))
    
    def get_default_tariff(self) -> Optional[Dict]:
        """
        Получение тарифа по умолчанию
        
        Returns:
            Тариф по умолчанию или None
        """
        for tariff in self.tariffs.values():
            if tariff.get('is_default', False):
                return deepcopy(tariff)
        
        # Если не нашли по умолчанию, возвращаем первый активный
        active_tariffs = self.get_all_tariffs(active_only=True)
        return active_tariffs[0] if active_tariffs else None
    
    def calculate_price(self, tariff_code: str, billing_period: str,
                       partner_count: int = 1) -> Dict[str, Any]:
        """
        Расчет цены с учетом периода и количества партнеров
        
        Args:
            tariff_code: Код тарифа
            billing_period: Период оплаты
            partner_count: Количество партнеров (для групповых тарифов)
            
        Returns:
            Dict с расчетом цены
        """
        tariff = self.get_tariff(tariff_code)
        if not tariff:
            raise ValueError(f"Тариф {tariff_code} не найден")
        
        # Базовая цена за период
        price_key = f"price_{billing_period}"
        base_price = tariff.get(price_key, tariff.get('price_monthly', 0))
        
        # Расчет итоговой цены
        total_price = base_price * partner_count
        
        # Расчет экономии
        monthly_price = tariff.get('price_monthly', 0) * partner_count
        savings = 0
        
        if billing_period != 'monthly':
            savings = (monthly_price * self._get_period_months(billing_period)) - total_price
        
        return {
            'tariff_code': tariff_code,
            'tariff_name': tariff['name'],
            'billing_period': billing_period,
            'partner_count': partner_count,
            'base_price_per_partner': base_price,
            'total_price': total_price,
            'currency': tariff.get('currency', 'RUB'),
            'savings': savings,
            'savings_percentage': (savings / (monthly_price * self._get_period_months(billing_period))) * 100 if monthly_price > 0 else 0,
            'features': tariff.get('features', []),
            'leads_included': tariff.get('leads_included', 0)
        }
    
    def compare_tariffs(self, tariff_codes: List[str]) -> List[Dict]:
        """
        Сравнение тарифов
        
        Args:
            tariff_codes: Список кодов тарифов для сравнения
            
        Returns:
            Список тарифов для сравнения
        """
        comparison = []
        
        for code in tariff_codes:
            tariff = self.get_tariff(code)
            if tariff:
                comparison.append({
                    'code': code,
                    'name': tariff['name'],
                    'description': tariff.get('description', ''),
                    'price_monthly': tariff.get('price_monthly', 0),
                    'price_quarterly': tariff.get('price_quarterly'),
                    'price_yearly': tariff.get('price_yearly'),
                    'currency': tariff.get('currency', 'RUB'),
                    'leads_included': tariff.get('leads_included', 0),
                    'features': tariff.get('features', []),
                    'is_active': tariff.get('is_active', True),
                    'is_default': tariff.get('is_default', False)
                })
        
        return comparison
    
    def get_recommended_tariff(self, leads_per_month: int,
                              required_features: List[str] = None) -> Dict:
        """
        Рекомендация тарифа на основе потребностей
        
        Args:
            leads_per_month: Количество лидов в месяц
            required_features: Требуемые функции
            
        Returns:
            Рекомендованный тариф
        """
        required_features = required_features or []
        
        suitable_tariffs = []
        
        for tariff in self.get_all_tariffs(active_only=True):
            # Проверка по лидам
            if tariff.get('leads_included', 0) < leads_per_month:
                continue
            
            # Проверка по функциям
            has_all_features = True
            tariff_features = tariff.get('features', [])
            
            for feature in required_features:
                if feature not in tariff_features:
                    has_all_features = False
                    break
            
            if not has_all_features:
                continue
            
            suitable_tariffs.append(tariff)
        
        if not suitable_tariffs:
            # Возвращаем самый дорогой тариф, если ничего не подошло
            return self.get_all_tariffs(active_only=True)[-1]
        
        # Возвращаем самый дешевый из подходящих
        return min(suitable_tariffs, key=lambda x: x.get('price_monthly', 0))
    
    def _get_period_months(self, billing_period: str) -> int:
        """Получить количество месяцев в периоде"""
        periods = {
            'monthly': 1,
            'quarterly': 3,
            'yearly': 12
        }
        return periods.get(billing_period, 1)
    
    def get_tariff_features_matrix(self) -> Dict[str, List[str]]:
        """
        Получение матрицы функций по тарифам
        
        Returns:
            Dict с функциями по тарифам
        """
        matrix = {}
        
        for code, tariff in self.tariffs.items():
            if tariff.get('is_active', True):
                matrix[code] = tariff.get('features', [])
        
        return matrix
EOF
