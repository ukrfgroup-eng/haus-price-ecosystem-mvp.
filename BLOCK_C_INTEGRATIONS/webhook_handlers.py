"""
ОБРАБОТЧИКИ ВЕБХУКОВ ОТ ВНЕШНИХ СЕРВИСОВ
Согласно ТЗ: ИНТЕГРАЦИЯ UMNICO + PROTALK
"""

import hashlib
import hmac
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class WebhookHandler:
    """Базовый обработчик вебхуков от внешних сервисов"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Верификация подписи вебхука"""
        if not self.secret_key:
            logger.warning("No secret key configured for webhook verification")
            return True  # В разработке пропускаем проверку
        
        expected_signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def handle_protalk_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка вебхука от Protalk бота"""
        try:
            event_type = data.get('type', 'unknown')
            logger.info(f"Processing Protalk webhook: {event_type}")
            
            if event_type == 'message':
                return self._handle_protalk_message(data)
            elif event_type == 'command':
                return self._handle_protalk_command(data)
            elif event_type == 'callback_query':
                return self._handle_protalk_callback(data)
            else:
                logger.warning(f"Unhandled Protalk event type: {event_type}")
                return {'status': 'unhandled_event'}
                
        except Exception as e:
            logger.error(f"Error handling Protalk webhook: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _handle_protalk_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка сообщения от пользователя"""
        message = data.get('message', {})
        user_message = message.get('text', '').strip()
        user_id = data.get('user', {}).get('id')
        chat_id = message.get('chat', {}).get('id')
        
        # Определение типа пользователя
        user_type = self._detect_user_type(user_message)
        
        if user_type == 'potential_partner':
            return {
                'action': 'redirect_to_partner_bot',
                'message': 'Перевожу вас в бот регистрации партнеров...',
                'bot_url': 'https://t.me/partner_haus_price_bot',
                'user_id': user_id,
                'chat_id': chat_id
            }
        elif user_type == 'customer':
            # Анализ запроса заказчика
            return {
                'action': 'process_customer_request',
                'message': 'Начинаю анализ вашего запроса...',
                'user_message': user_message,
                'user_id': user_id,
                'chat_id': chat_id
            }
        else:
            # Неопределенный тип - просим уточнить
            return {
                'action': 'ask_user_type',
                'message': 'Пожалуйста, уточните, вы заказчик или партнер?',
                'options': ['Заказчик', 'Партнер'],
                'user_id': user_id
            }
    
    def _handle_protalk_command(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка команды от пользователя"""
        command = data.get('command', '').lower()
        user_id = data.get('user', {}).get('id')
        
        if command == '/start':
            return {
                'action': 'send_welcome',
                'message': '👋 Добро пожаловать в экосистему Дома-Цены.РФ!',
                'user_id': user_id
            }
        elif command == '/help':
            return {
                'action': 'send_help',
                'message': 'Я помогу вам найти исполнителя или зарегистрировать компанию как партнера.',
                'user_id': user_id
            }
        elif command == '/register':
            return {
                'action': 'start_partner_registration',
                'message': 'Начинаю процесс регистрации партнера...',
                'user_id': user_id
            }
        
        return {'status': 'unknown_command'}
    
    def _handle_protalk_callback(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка callback запроса (нажатия кнопок)"""
        callback_data = data.get('callback_query', {})
        callback_id = callback_data.get('id')
        data_text = callback_data.get('data', '')
        
        # Парсинг callback данных
        if data_text.startswith('action_'):
            action = data_text.replace('action_', '')
            return {
                'action': 'callback_processed',
                'callback_id': callback_id,
                'action_type': action,
                'message': f'Обработано действие: {action}'
            }
        
        return {'status': 'callback_processed'}
    
    def handle_umnico_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка вебхука от Umnico (чат на сайте)"""
        try:
            message = data.get('message', '').lower()
            user_id = data.get('userId')
            session_id = data.get('sessionId')
            
            logger.info(f"Processing Umnico webhook from user {user_id}")
            
            # Определение типа пользователя по сообщению
            if self._is_partner_message(message):
                return {
                    'action': 'redirect_to_partner_bot',
                    'messages': [
                        {
                            'text': '🏢 Отлично! Я вижу, вы хотите стать партнером нашей экосистемы.',
                            'type': 'text'
                        },
                        {
                            'text': 'Для регистрации компании перейдите в нашего бота:',
                            'type': 'text'
                        }
                    ],
                    'actions': [
                        {
                            'type': 'button',
                            'text': '📱 Перейти в бот регистрации',
                            'url': 'https://t.me/partner_haus_price_bot'
                        }
                    ],
                    'user_id': user_id,
                    'session_id': session_id
                }
            else:
                # Заказчик - начинаем диалог
                return {
                    'action': 'start_customer_conversation',
                    'messages': [
                        {
                            'text': '🔨 Привет! Я помогу вам найти исполнителя для вашего проекта.',
                            'type': 'text'
                        },
                        {
                            'text': 'Расскажите, что вы хотите построить или отремонтировать?',
                            'type': 'text'
                        }
                    ],
                    'user_id': user_id,
                    'session_id': session_id
                }
                
        except Exception as e:
            logger.error(f"Error handling Umnico webhook: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def handle_tilda_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка вебхука от Tilda (личный кабинет)"""
        try:
            form_id = data.get('formid')
            partner_code = data.get('partner_code')
            
            logger.info(f"Processing Tilda webhook: form={form_id}, partner={partner_code}")
            
            if form_id == 'partner_registration_complete':
                return {
                    'action': 'complete_partner_registration',
                    'partner_code': partner_code,
                    'message': 'Регистрация завершена успешно',
                    'next_steps': 'Ожидайте активации аккаунта в течение 24 часов'
                }
            elif form_id == 'document_upload':
                return {
                    'action': 'process_documents',
                    'partner_code': partner_code,
                    'documents': data.get('documents', []),
                    'message': 'Документы получены и отправлены на проверку'
                }
            elif form_id == 'profile_update':
                return {
                    'action': 'update_partner_profile',
                    'partner_code': partner_code,
                    'profile_data': data.get('data', {}),
                    'message': 'Профиль успешно обновлен'
                }
            
            return {'status': 'unhandled_form'}
            
        except Exception as e:
            logger.error(f"Error handling Tilda webhook: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def handle_payment_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка вебхука от платежной системы"""
        try:
            payment_id = data.get('payment_id')
            status = data.get('status')
            amount = data.get('amount')
            currency = data.get('currency')
            metadata = data.get('metadata', {})
            
            logger.info(f"Processing payment webhook: {payment_id}, status={status}")
            
            if status == 'succeeded':
                partner_code = metadata.get('partner_code')
                tariff_plan = metadata.get('tariff_plan')
                
                return {
                    'action': 'activate_subscription',
                    'payment_id': payment_id,
                    'partner_code': partner_code,
                    'tariff_plan': tariff_plan,
                    'amount': amount,
                    'currency': currency,
                    'message': 'Платеж успешно обработан, подписка активирована'
                }
            elif status == 'failed':
                return {
                    'action': 'payment_failed',
                    'payment_id': payment_id,
                    'error': data.get('error'),
                    'message': 'Ошибка при обработке платежа'
                }
            
            return {'status': 'payment_processed'}
            
        except Exception as e:
            logger.error(f"Error handling payment webhook: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _detect_user_type(self, message: str) -> str:
        """Определение типа пользователя по сообщению"""
        message_lower = message.lower()
        
        # Ключевые слова для партнера
        partner_keywords = [
            'партнер', 'компания', 'регистрация', 'сотрудничать',
            'юрлицо', 'ип', 'ооо', 'подрядчик', 'исполнитель',
            'предлагаю услуги', 'строительная компания', 'стать партнером'
        ]
        
        # Ключевые слова для заказчика
        customer_keywords = [
            'построить', 'ремонт', 'найти', 'ищу', 'нужен',
            'дом', 'коттедж', 'дача', 'смета', 'стоимость',
            'подрядчик', 'исполнитель', 'мастер'
        ]
        
        partner_match = any(keyword in message_lower for keyword in partner_keywords)
        customer_match = any(keyword in message_lower for keyword in customer_keywords)
        
        if partner_match and not customer_match:
            return 'potential_partner'
        elif customer_match and not partner_match:
            return 'customer'
        elif partner_match and customer_match:
            # Если есть оба типа ключевых слов, спрашиваем уточнение
            return 'ambiguous'
        else:
            return 'unknown'
    
    def _is_partner_message(self, message: str) -> bool:
        """Определение, является ли сообщение от партнера"""
        partner_keywords = [
            'партнер', 'компания', 'регистрация', 'сотрудничать',
            'юрлицо', 'ип', 'ооо', 'подрядчик', 'исполнитель'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in partner_keywords)
