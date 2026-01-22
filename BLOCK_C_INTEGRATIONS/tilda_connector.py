"""
КОННЕКТОР ДЛЯ TILDA (ЛИЧНЫЙ КАБИНЕТ)
Интеграция с личным кабинетом партнера на Tilda
"""

import requests
import hashlib
import hmac
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TildaConnector:
    """Коннектор для работы с Tilda (личный кабинет партнера)"""
    
    def __init__(self, public_key: str, secret_key: str, base_url: str = "https://api.tildacdn.info"):
        self.public_key = public_key
        self.secret_key = secret_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HausPrice-Ecosystem/1.0'
        })
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Верификация подписи вебхука от Tilda"""
        expected_signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def create_partner_page(self, partner_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание страницы партнера в личном кабинете"""
        try:
            url = f"{self.base_url}/api/v1/createpage/"
            
            payload = {
                'publickey': self.public_key,
                'secretkey': self.secret_key,
                'title': f"Личный кабинет: {partner_data.get('company_name')}",
                'html': self._generate_partner_html(partner_data),
                'projectid': '000000',  # Нужно заменить на реальный ID проекта
                'pagefolderid': '000000'  # Нужно заменить на реальный ID папки
            }
            
            logger.info(f"Creating Tilda page for partner: {partner_data.get('partner_code')}")
            response = self.session.post(url, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                page_url = data.get('url', '')
                
                return {
                    'success': True,
                    'page_id': data.get('id'),
                    'page_url': page_url,
                    'partner_code': partner_data.get('partner_code'),
                    'message': 'Страница личного кабинета создана'
                }
            else:
                logger.error(f"Failed to create Tilda page: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'Ошибка создания страницы: {response.status_code}',
                    'details': response.text[:200]
                }
                
        except Exception as e:
            logger.error(f"Error creating Tilda page: {e}")
            return {
                'success': False,
                'error': f'Ошибка создания страницы: {str(e)}'
            }
    
    def update_partner_page(self, page_id: str, partner_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление страницы партнера"""
        try:
            url = f"{self.base_url}/api/v1/updatepage/"
            
            payload = {
                'publickey': self.public_key,
                'secretkey': self.secret_key,
                'pageid': page_id,
                'html': self._generate_partner_html(partner_data)
            }
            
            response = self.session.post(url, json=payload, timeout=15)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'page_id': page_id,
                    'partner_code': partner_data.get('partner_code'),
                    'message': 'Страница личного кабинета обновлена'
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка обновления страницы: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error updating Tilda page {page_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка обновления страницы: {str(e)}'
            }
    
    def get_page_stats(self, page_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Получение статистики посещений страницы"""
        try:
            url = f"{self.base_url}/api/v1/getpagestats/"
            
            payload = {
                'publickey': self.public_key,
                'secretkey': self.secret_key,
                'pageid': page_id,
                'startdate': start_date,
                'enddate': end_date
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'stats': data,
                    'page_id': page_id,
                    'period': f'{start_date} - {end_date}'
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка получения статистики: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error getting page stats {page_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка получения статистики: {str(e)}'
            }
    
    def create_registration_form(self, partner_code: str) -> Dict[str, Any]:
        """Создание формы регистрации для партнера"""
        try:
            # URL для создания формы в Tilda
            form_html = self._generate_registration_form_html(partner_code)
            
            # В реальности здесь будет вызов API Tilda для создания формы
            # Пока возвращаем заглушку
            
            form_url = f"https://партнер.дома-цены.рф/register/{partner_code}"
            
            return {
                'success': True,
                'form_url': form_url,
                'partner_code': partner_code,
                'message': 'Форма регистрации создана',
                'html_preview': form_html[:500] + '...'  # Для отладки
            }
            
        except Exception as e:
            logger.error(f"Error creating registration form for {partner_code}: {e}")
            return {
                'success': False,
                'error': f'Ошибка создания формы: {str(e)}'
            }
    
    def send_form_submission(self, form_id: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Отправка данных формы в Tilda"""
        try:
            url = f"{self.base_url}/api/v1/forms/{form_id}/submissions"
            
            payload = {
                'publickey': self.public_key,
                'secretkey': self.secret_key,
                'form': form_data
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'form_id': form_id,
                    'message': 'Данные формы отправлены'
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка отправки формы: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error sending form submission {form_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка отправки формы: {str(e)}'
            }
    
    def _generate_partner_html(self, partner_data: Dict[str, Any]) -> str:
        """Генерация HTML для страницы партнера"""
        company_name = partner_data.get('company_name', 'Компания')
        partner_code = partner_data.get('partner_code', '')
        status = partner_data.get('verification_status', 'pending')
        rating = partner_data.get('rating', 0)
        specializations = ', '.join(partner_data.get('specializations', []))
        
        status_text = {
            'verified': '✅ Верифицирован',
            'pending': '⏳ На проверке',
            'rejected': '❌ Отклонен'
        }.get(status, '⏳ На проверке')
        
        html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Личный кабинет - {company_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
        .logo {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
        .status {{ padding: 5px 15px; border-radius: 20px; font-weight: bold; }}
        .verified {{ background: #d4edda; color: #155724; }}
        .pending {{ background: #fff3cd; color: #856404; }}
        .rejected {{ background: #f8d7da; color: #721c24; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 32px; font-weight: bold; color: #2c3e50; }}
        .stat-label {{ color: #6c757d; margin-top: 10px; }}
        .rating {{ color: #ffc107; font-size: 24px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🏢 {company_name}</div>
            <div class="status {status}">{status_text}</div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{rating}/5</div>
                <div class="stat-label">Рейтинг</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{partner_data.get('completed_projects', 0)}</div>
                <div class="stat-label">Проектов</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{partner_data.get('response_rate', 0)}%</div>
                <div class="stat-label">Ответов</div>
            </div>
        </div>
        
        <h2>Специализации</h2>
        <p>{specializations}</p>
        
        <h2>Контакты</h2>
        <p>📞 {partner_data.get('phone', 'Не указан')}</p>
        <p>📧 {partner_data.get('email', 'Не указан')}</p>
        
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #6c757d;">
            Личный кабинет партнера Дома-Цены.РФ | Код: {partner_code}
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_registration_form_html(self, partner_code: str) -> str:
        """Генерация HTML формы регистрации"""
        return f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Регистрация партнера</title>
</head>
<body>
    <h1>Регистрация партнера</h1>
    <form id="partnerRegistrationForm">
        <input type="hidden" name="partner_code" value="{partner_code}">
        
        <div>
            <label>Название компании:</label>
            <input type="text" name="company_name" required>
        </div>
        
        <div>
            <label>ИНН:</label>
            <input type="text" name="inn" required pattern="\\d{{10,12}}">
        </div>
        
        <div>
            <label>Контактное лицо:</label>
            <input type="text" name="contact_person" required>
        </div>
        
        <div>
            <label>Телефон:</label>
            <input type="tel" name="phone" required>
        </div>
        
        <div>
            <label>Email:</label>
            <input type="email" name="email" required>
        </div>
        
        <button type="submit">Зарегистрироваться</button>
    </form>
    
    <script>
        document.getElementById('partnerRegistrationForm').addEventListener('submit', async (e) => {{
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            // Отправка данных на сервер
            const response = await fetch('/api/v1/partners/register', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(data)
            }});
            
            if (response.ok) {{
                alert('Регистрация начата успешно!');
            }} else {{
                alert('Ошибка регистрации');
            }}
        }});
    </script>
</body>
</html>
"""
