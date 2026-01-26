cat > services/tariff_service.py << 'EOF'
"""
TariffService - управление тарифами для блока D
Версия: 1.0.0
"""

import logging
from typing import Dict, Any, List, Optional
from copy import deepcopy

logger = logging.getLogger(__name__)

class TariffService:
    """Сервис тарифов блока D"""
    
    def __init__(self, config):
        """
        Инициализация сервиса тарифов блока D
        
        Args:
            config: Конфигурация блока D
        """
        self.config = config
        self.tariffs = config.TARIFF_PLANS
        logger.info("TariffService блока D инициализирован")
    
    def get_tariff(self, tariff_code: str) -> Optional[Dict]:
        """
        Получение тарифа блока D
        
        Args:
            tariff_code: Код тарифа
            
        Returns:
            Тариф или None
        """
        tariff = self.tariffs.get(tariff_code)
        if tariff:
            result = deepcopy(tariff)
            result['source'] = 'block_d'
            return result
        return None
    
    def get_all_tariffs(self, active_only: bool = True) -> List[Dict]:
        """
        Получение всех тарифов блока D
        
        Args:
            active_only: Только активные
            
        Returns:
            Список тарифов
        """
        tariffs = []
        for code, tariff in self.tariffs.items():
            if active_only and not tariff.get('is_active', True):
                continue
            
            tariff_copy = deepcopy(tariff)
            tariff_copy['code'] = code
            tariff_copy['source'] = 'block_d'
            tariffs.append(tariff_copy)
        
        # Сортируем по цене
        return sorted(tariffs, key=lambda x: x.get('price_monthly', 0))
    
    def calculate_price(self, tariff_code: str, billing_period: str,
                       partner_count: int = 1) -> Dict[str, Any]:
        """
        Расчет цены (блок D)
        
        Args:
            tariff_code: Код тарифа
            billing_period: Период
            partner_count: Количество партнеров
            
        Returns:
            Расчет цены
        """
        tariff = self.get_tariff(tariff_code)
        if not tariff:
            raise ValueError(f"Блок D: Тариф {tariff_code} не найден")
        
        # Базовая цена за период
        price_key = f"price_{billing_period}"
        base_price = tariff.get(price_key, tariff.get('price_monthly', 0))
        
        # Итоговая цена
        total_price = base_price * partner_count
        
        # Расчет экономии
        monthly_price = tariff.get('price_monthly', 0) * partner_count
        savings = 0
        
        if billing_period != 'monthly' and monthly_price > 0:
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
            'leads_included': tariff.get('leads_included', 0),
            'source': 'block_d'
        }
    
    def get_recommended_tariff(self, leads_per_month: int,
                              required_features: List[str] = None) -> Dict:
        """
        Рекомендация тарифа (блок D)
        
        Args:
            leads_per_month: Количество лидов
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
            # Возвращаем самый дорогой тариф
            all_tariffs = self.get_all_tariffs(active_only=True)
            return all_tariffs[-1] if all_tariffs else None
        
        # Самый дешевый из подходящих
        return min(suitable_tariffs, key=lambda x: x.get('price_monthly', 0))
    
    def _get_period_months(self, billing_period: str) -> int:
        """Получить количество месяцев в периоде"""
        periods = {
            'monthly': 1,
            'quarterly': 3,
            'yearly': 12
        }
        return periods.get(billing_period, 1)

# Экспорт
__all__ = ['TariffService']
EOF
