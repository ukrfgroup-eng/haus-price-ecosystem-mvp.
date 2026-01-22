"""
КОННЕКТОР ДЛЯ PROTALK БОТОВ
Интеграция с ботами-проводниками
"""

import requests
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ProtalkConnector:
    """Коннектор для работы с Protalk ботами"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.protalk.io"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'HausPrice-Ecosystem/1.0'
        })
    
    def send_message(self, chat_id: str, text: str, 
                    keyboard: Optional[List[List[Dict]]] = None,
                    parse_mode: str = 'HTML') -> Dict[str, Any]:
        """Отправка сообщения пользователю"""
        try:
            url = f"{self.base_url}/api/v1/messages/send"
            
            payload = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            
            if keyboard:
                payload['reply_markup'] = {
                    'keyboard': keyboard,
                    'resize_keyboard': True,
                    'one_time_keyboard': False
                }
            
            logger.info(f"Sending message to chat {chat_id}")
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'message_id': result.get('message_id'),
                    'chat_id': chat_id,
                    'sent_at': datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'Ошибка отправки сообщения: {response.status_code}',
                    'details': response.text[:200]
                }
                
        except requests.Timeout:
            logger.error(f"Timeout sending message to chat {chat_id}")
            return {
                'success': False,
                'error': 'Таймаут при отправке сообщения'
            }
        except Exception as e:
            logger.error(f"Error sending message to chat {chat_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка отправки сообщения: {str(e)}'
            }
    
    def send_photo(self, chat_id: str, photo_url: str, 
                  caption: Optional[str] = None) -> Dict[str, Any]:
        """Отправка фото пользователю"""
        try:
            url = f"{self.base_url}/api/v1/messages/sendPhoto"
            
            payload = {
                'chat_id': chat_id,
                'photo': photo_url
            }
            
            if caption:
                payload['caption'] = caption
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Фото успешно отправлено',
                    'chat_id': chat_id
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка отправки фото: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error sending photo to chat {chat_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка отправки фото: {str(e)}'
            }
    
    def send_document(self, chat_id: str, document_url: str,
                     caption: Optional[str] = None) -> Dict[str, Any]:
        """Отправка документа пользователю"""
        try:
            url = f"{self.base_url}/api/v1/messages/sendDocument"
            
            payload = {
                'chat_id': chat_id,
                'document': document_url
            }
            
            if caption:
                payload['caption'] = caption
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Документ успешно отправлен',
                    'chat_id': chat_id
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка отправки документа: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error sending document to chat {chat_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка отправки документа: {str(e)}'
            }
    
    def send_inline_keyboard(self, chat_id: str, text: str,
                           inline_keyboard: List[List[Dict]]) -> Dict[str, Any]:
        """Отправка сообщения с inline клавиатурой"""
        try:
            url = f"{self.base_url}/api/v1/messages/send"
            
            payload = {
                'chat_id': chat_id,
                'text': text,
                'reply_markup': {
                    'inline_keyboard': inline_keyboard
                }
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Сообщение с клавиатурой успешно отправлено',
                    'chat_id': chat_id
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка отправки сообщения: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error sending inline keyboard to chat {chat_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка отправки сообщения: {str(e)}'
            }
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Получение профиля пользователя"""
        try:
            url = f"{self.base_url}/api/v1/users/{user_id}"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'profile': data,
                    'user_id': user_id
                }
            elif response.status_code == 404:
                return {
                    'success': False,
                    'error': 'Пользователь не найден',
                    'user_id': user_id
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка получения профиля: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error getting user profile {user_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка получения профиля: {str(e)}'
            }
    
    def create_menu_button(self, text: str, callback_data: str) -> Dict[str, str]:
        """Создание кнопки меню"""
        return {
            'text': text,
            'callback_data': callback_data
        }
    
    def create_url_button(self, text: str, url: str) -> Dict[str, str]:
        """Создание кнопки с URL"""
        return {
            'text': text,
            'url': url
        }
    
    def format_partner_card(self, partner: Dict[str, Any]) -> str:
        """Форматирование карточки партнера для отправки в бот"""
        name = partner.get('company_name', 'Не указано')
        specializations = ', '.join(partner.get('specializations', [])[:3])
        rating = partner.get('rating', 0)
        completed = partner.get('completed_projects', 0)
        region = partner.get('regions', ['Не указано'])[0]
        
        card = f"""
🏢 <b>{name}</b>

⭐ Рейтинг: {rating}/5
📊 Завершено проектов: {completed}
🎯 Специализации: {specializations}
📍 Регион: {region}

📞 Контакт: {partner.get('phone', 'Не указан')}
📧 Email: {partner.get('email', 'Не указан')}
"""
        
        if partner.get('website'):
            card += f"🌐 Сайт: {partner.get('website')}\n"
        
        return card.strip()
    
    def format_partners_list(self, partners: List[Dict[str, Any]]) -> List[str]:
        """Форматирование списка партнеров для постраничного вывода"""
        cards = []
        
        for i, partner in enumerate(partners, 1):
            card = self.format_partner_card(partner)
            cards.append(f"<b>Партнер #{i}</b>\n{card}")
        
        return cards
    
    def send_partner_recommendations(self, chat_id: str, partners: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Отправка рекомендаций партнеров пользователю"""
        try:
            if not partners:
                return self.send_message(
                    chat_id=chat_id,
                    text="😕 К сожалению, по вашим критериям не найдено подходящих партнеров.\n\nПопробуйте изменить параметры поиска."
                )
            
            # Отправляем первого партнера с подробной информацией
            first_partner = partners[0]
            first_card = self.format_partner_card(first_partner)
            
            # Создаем клавиатуру для навигации
            keyboard = [
                [self.create_menu_button("✅ Принять заявку", "accept_lead")],
                [self.create_menu_button("❓ Задать вопрос", "ask_question")],
                [self.create_menu_button("📞 Позвонить", "call_partner")],
                [self.create_menu_button("➡️ Следующий партнер", "next_partner")]
            ]
            
            # Отправляем сообщение с клавиатурой
            result = self.send_inline_keyboard(
                chat_id=chat_id,
                text=first_card,
                inline_keyboard=keyboard
            )
            
            if result['success']:
                # Сохраняем информацию о показе
                result['partners_shown'] = 1
                result['total_partners'] = len(partners)
                result['current_index'] = 0
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending partner recommendations to chat {chat_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка отправки рекомендаций: {str(e)}'
            }
    
    def update_webhook_url(self, webhook_url: str) -> Dict[str, Any]:
        """Обновление URL вебхука для бота"""
        try:
            url = f"{self.base_url}/api/v1/bot/webhook"
            
            payload = {
                'url': webhook_url
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Webhook URL updated: {webhook_url}")
                return {
                    'success': True,
                    'message': 'Webhook URL успешно обновлен',
                    'url': webhook_url
                }
            else:
                logger.error(f"Failed to update webhook: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'Ошибка обновления webhook: {response.status_code}',
                    'details': response.text[:200]
                }
                
        except Exception as e:
            logger.error(f"Error updating webhook URL: {e}")
            return {
                'success': False,
                'error': f'Ошибка обновления webhook: {str(e)}'
            }
