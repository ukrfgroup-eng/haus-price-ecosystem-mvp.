"""
Сервис верификации партнеров через ФНС и проверки документов
"""

import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..models.partner_models import Partner, PartnerDocument

logger = logging.getLogger(__name__)


class VerificationService:
    """Сервис верификации партнеров"""
    
    def __init__(self, fns_api_key: str = None):
        self.fns_api_key = fns_api_key
        self.max_retries = 3
        self.timeout_seconds = 30
    
    def verify_inn(self, inn: str) -> Dict[str, Any]:
        """
        Проверка ИНН через API ФНС
        
        Args:
            inn: ИНН для проверки
            
        Returns:
            Результат проверки
        """
        # 1. Базовая валидация формата
        if not self._validate_inn_format(inn):
            return {
                "is_valid": False,
                "error": "Неверный формат ИНН",
                "inn": inn
            }
        
        # 2. Проверка контрольной суммы
        if not self._validate_inn_checksum(inn):
            return {
                "is_valid": False,
                "error": "Неверная контрольная сумма ИНН",
                "inn": inn
            }
        
        # 3. Проверка через API ФНС (заглушка)
        # В реальности здесь будет обращение к API ФНС
        try:
            # Имитация ответа от ФНС
            fns_response = self._mock_fns_check(inn)
            
            if fns_response.get("status") == "ACTIVE":
                return {
                    "is_valid": True,
                    "company_name": fns_response.get("name"),
                    "legal_form": fns_response.get("legal_form"),
                    "ogrn": fns_response.get("ogrn"),
                    "kpp": fns_response.get("kpp"),
                    "legal_address": fns_response.get("address"),
                    "status": fns_response.get("status"),
                    "fns_data": fns_response
                }
            else:
                return {
                    "is_valid": False,
                    "error": f"Компания не активна. Статус: {fns_response.get('status')}",
                    "fns_data": fns_response
                }
                
        except Exception as e:
            logger.error(f"FNS API error for INN {inn}: {str(e)}")
            
            # Fallback: возвращаем базовую информацию
            return {
                "is_valid": True,  # ИНН валиден формально
                "company_name": "Требуется ручная проверка",
                "legal_form": "Не определено",
                "status": "PENDING_MANUAL_CHECK",
                "error": f"Ошибка API ФНС: {str(e)}"
            }
    
    def verify_documents(self, partner: Partner) -> bool:
        """
        Проверка документов партнера
        
        Args:
            partner: Объект партнера
            
        Returns:
            True если документы в порядке
        """
        required_docs = ["inn_certificate", "ogrn_certificate", "extract"]
        
        uploaded_docs = [doc.type for doc in partner.documents]
        
        # Проверяем наличие обязательных документов
        for doc_type in required_docs:
            if doc_type not in uploaded_docs:
                logger.warning(f"Missing required document: {doc_type}")
                return False
        
        # Проверяем качество документов
        valid_docs_count = 0
        for doc in partner.documents:
            if self._validate_document_quality(doc):
                valid_docs_count += 1
        
        # Минимум 2 из 3 документов должны быть хорошего качества
        return valid_docs_count >= 2
    
    def verify_via_fns(self, inn: str) -> Dict[str, Any]:
        """
        Полная проверка через ФНС (ЕГРЮЛ/ЕГРИП)
        
        Args:
            inn: ИНН для проверки
            
        Returns:
            Детальная информация из ФНС
        """
        try:
            # Пытаемся получить расширенную информацию
            company_info = self._mock_extended_fns_check(inn)
            
            return {
                "success":
