cat > services/notification_service.py << 'EOF'
"""
NotificationService - система уведомлений для блока D
Версия: 1.0.0
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class NotificationService:
    """Сервис уведомлений блока D"""
    
    def __init__(self, config):
        """
        Инициализация сервиса уведомлений блока D
        
        Args:
            config: Конфигурация блока D
        """
        self.config = config
        self.email_enabled = config.NOTIFICATIONS['email']['enabled']
        self.telegram_enabled = config.NOTIFICATIONS['telegram']['enabled']
        self.sms_enabled = config.NOTIFICATIONS['sms']['enabled']
        
        logger.info("NotificationService блока D инициализирован")
    
    def send_invoice_email(self, invoice: Dict[str, Any], 
                          recipient_email: str) -> bool:
        """
        Отправка счета по email (блок D)
        
        Args:
            invoice: Данные счета
            recipient_email: Email получателя
            
        Returns:
            bool: Успешность отправки
        """
        if not self.email_enabled:
            logger.warning("Блок D: Отправка email отключена в конфигурации")
            return False
        
        try:
            # Подготавливаем данные для письма
            subject = f"Счет на оплату №{invoice['invoice_number']}"
            body = self._generate_invoice_email_body(invoice)
            
            # Отправляем email
            success = self._send_email(
                to_email=recipient_email,
                subject=subject,
                body=body,
                attachments=[]
            )
            
            if success:
                logger.info(f"Блок D: Счет {invoice['invoice_number']} отправлен на {recipient_email}")
            else:
                logger.error(f"Блок D: Не удалось отправить счет {invoice['invoice_number']}")
            
            return success
            
        except Exception as e:
            logger.error(f"Блок D: Ошибка отправки счета: {e}")
            return False
    
    def send_payment_success_email(self, payment: Dict[str, Any],
                                  recipient_email: str) -> bool:
        """
        Отправка уведомления об успешной оплате (блок D)
        
        Args:
            payment: Данные платежа
            recipient_email: Email получателя
            
        Returns:
            bool: Успешность отправки
        """
        if not self.email_enabled:
            logger.warning("Блок D: Отправка email отключена в конфигурации")
            return False
        
        try:
            subject = f"Оплата прошла успешно"
            body = self._generate_payment_success_body(payment)
            
            success = self._send_email(
                to_email=recipient_email,
                subject=subject,
                body=body
            )
            
            if success:
                logger.info(f"Блок D: Уведомление об оплате {payment['payment_id']} отправлено на {recipient_email}")
            else:
                logger.error(f"Блок D: Не удалось отправить уведомление об оплате {payment['payment_id']}")
            
            return success
            
        except Exception as e:
            logger.error(f"Блок D: Ошибка отправки уведомления об оплате: {e}")
            return False
    
    def send_subscription_notification(self, subscription: Dict[str, Any],
                                      notification_type: str,
                                      days_before: int = None) -> bool:
        """
        Отправка уведомления о подписке (блок D)
        
        Args:
            subscription: Данные подписки
            notification_type: Тип уведомления (expiring, renewed, cancelled, upgraded)
            days_before: За сколько дней до истечения (для expiring)
            
        Returns:
            bool: Успешность отправки
        """
        if not self.email_enabled:
            logger.warning("Блок D: Отправка email отключена в конфигурации")
            return False
        
        try:
            # В реальной системе здесь бы получали email партнера из профиля
            # Сейчас используем заглушку
            
            if notification_type == 'expiring':
                subject = f"Ваша подписка истекает через {days_before} дней"
                body = self._generate_subscription_expiring_body(subscription, days_before)
            elif notification_type == 'renewed':
                subject = "Ваша подписка успешно продлена"
                body = self._generate_subscription_renewed_body(subscription)
            elif notification_type == 'cancelled':
                subject = "Ваша подписка отменена"
                body = self._generate_subscription_cancelled_body(subscription)
            else:
                subject = "Уведомление о подписке"
                body = self._generate_generic_subscription_body(subscription)
            
            # Заглушка для email партнера (в реальности брать из БД)
            partner_email = f"partner_{subscription['partner_id']}@example.com"
            
            success = self._send_email(
                to_email=partner_email,
                subject=subject,
                body=body
            )
            
            if success:
                logger.info(f"Блок D: Уведомление о подписке {subscription['subscription_id']} отправлено")
            else:
                logger.error(f"Блок D: Не удалось отправить уведомление о подписке")
            
            return success
            
        except Exception as e:
            logger.error(f"Блок D: Ошибка отправки уведомления о подписке: {e}")
            return False
    
    def send_admin_notification(self, message: str, 
                               notification_type: str = 'info') -> bool:
        """
        Отправка уведомления администратору (блок D)
        
        Args:
            message: Сообщение
            notification_type: Тип (info, warning, error)
            
        Returns:
            bool: Успешность отправки
        """
        if self.telegram_enabled:
            # Здесь должна быть отправка в Telegram
            try:
                # Заглушка для Telegram бота
                logger.info(f"Блок D: Отправлено Telegram уведомление администратору: {message}")
                return True
            except Exception as e:
                logger.error(f"Блок D: Ошибка отправки Telegram уведомления: {e}")
                return False
        else:
            logger.info(f"Блок D: Уведомление администратору ({notification_type}): {message}")
            return True
    
    def send_sms_notification(self, phone_number: str, 
                             message: str) -> bool:
        """
        Отправка SMS уведомления (блок D)
        
        Args:
            phone_number: Номер телефона
            message: Сообщение
            
        Returns:
            bool: Успешность отправки
        """
        if not self.sms_enabled:
            logger.warning("Блок D: Отправка SMS отключена в конфигурации")
            return False
        
        try:
            # Заглушка для SMS сервиса
            logger.info(f"Блок D: SMS отправлено на {phone_number}: {message[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Блок D: Ошибка отправки SMS: {e}")
            return False
    
    def _send_email(self, to_email: str, subject: str, 
                   body: str, attachments: List[str] = None) -> bool:
        """
        Отправка email (блок D)
        
        Args:
            to_email: Email получателя
            subject: Тема
            body: Тело письма (HTML)
            attachments: Список путей к файлам
            
        Returns:
            bool: Успешность отправки
        """
        try:
            email_config = self.config.NOTIFICATIONS['email']
            
            # Создаем сообщение
            msg = MIMEMultipart()
            msg['From'] = email_config['from_email']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Добавляем тело письма
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # TODO: Добавить обработку вложений
            
            # Отправляем (заглушка для тестового режима)
            if self.config.TEST_MODE:
                logger.info(f"Блок D: Тестовый режим - письмо НЕ отправлено. Детали:")
                logger.info(f"  Кому: {to_email}")
                logger.info(f"  Тема: {subject}")
                logger.info(f"  Контент: {body[:100]}...")
                return True
            
            # Реальная отправка
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['smtp_username'], email_config['smtp_password'])
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            logger.error(f"Блок D: Ошибка отправки email: {e}")
            return False
    
    def _generate_invoice_email_body(self, invoice: Dict[str, Any]) -> str:
        """Генерация тела письма для счета"""
        due_date = datetime.fromisoformat(invoice['due_date']).strftime('%d.%m.%Y')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
                .button {{ display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Счет на оплату</h1>
                </div>
                <div class="content">
                    <h2>Уважаемый клиент!</h2>
                    <p>Для вас был сформирован счет №<strong>{invoice['invoice_number']}</strong>.</p>
                    
                    <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3>Детали счета:</h3>
                        <p><strong>Сумма к оплате:</strong> {invoice['total_amount']} {invoice['currency']}</p>
                        <p><strong>Дата счета:</strong> {datetime.now().strftime('%d.%m.%Y')}</p>
                        <p><strong>Срок оплаты:</strong> {due_date}</p>
                    </div>
                    
                    <p>Для оплаты перейдите по ссылке:</p>
                    <p><a href="[ссылка_на_оплату]" class="button">Оплатить счет</a></p>
                    
                    <p>Если у вас есть вопросы, пожалуйста, свяжитесь с нашей поддержкой.</p>
                </div>
                <div class="footer">
                    <p>С уважением,<br>
                    <strong>Команда HAUS Price Ecosystem</strong></p>
                    <p>Это письмо отправлено автоматически. Пожалуйста, не отвечайте на него.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_payment_success_body(self, payment: Dict[str, Any]) -> str:
        """Генерация тела письма об успешной оплате"""
        paid_at = datetime.fromisoformat(payment.get('paid_at', datetime.utcnow().isoformat())).strftime('%d.%m.%Y %H:%M')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Оплата прошла успешно!</h1>
                </div>
                <div class="content">
                    <h2>Спасибо за ваш платеж!</h2>
                    <p>Ваш платеж был успешно обработан.</p>
                    
                    <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3>Детали платежа:</h3>
                        <p><strong>Номер платежа:</strong> {payment['payment_id']}</p>
                        <p><strong>Сумма:</strong> {payment['amount']} {payment['currency']}</p>
                        <p><strong>Дата оплаты:</strong> {paid_at}</p>
                        <p><strong>Описание:</strong> {payment.get('description', 'Оплата услуг')}</p>
                    </div>
                    
                    <p>Чек о платеже был отправлен на вашу электронную почту и доступен в личном кабинете.</p>
                    
                    <p>Если у вас есть вопросы, пожалуйста, свяжитесь с нашей поддержкой.</p>
                </div>
                <div class="footer">
                    <p>С уважением,<br>
                    <strong>Команда HAUS Price Ecosystem</strong></p>
                    <p>Это письмо отправлено автоматически. Пожалуйста, не отвечайте на него.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_subscription_expiring_body(self, subscription: Dict[str, Any], 
                                           days_before: int) -> str:
        """Генерация тела письма об истечении подписки"""
        expires_at = datetime.fromisoformat(subscription['expires_at']).strftime('%d.%m.%Y')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #ff9800; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
                .button {{ display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Ваша подписка скоро истекает</h1>
                </div>
                <div class="content">
                    <h2>Напоминание об истечении подписки</h2>
                    <p>Ваша подписка на тариф <strong>{subscription['tariff_name']}</strong> истекает через {days_before} дней.</p>
                    
                    <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3>Детали подписки:</h3>
                        <p><strong>Тариф:</strong> {subscription['tariff_name']}</p>
                        <p><strong>Дата истечения:</strong> {expires_at}</p>
                        <p><strong>Стоимость продления:</strong> {subscription['price']} {subscription['currency']}</p>
                    </div>
                    
                    <p>Чтобы продолжить пользоваться всеми преимуществами платформы, продлите подписку:</p>
                    <p><a href="[ссылка_на_продление]" class="button">Продлить подписку</a></p>
                    
                    <p>Если подписка не будет продлена, доступ к платным функциям будет ограничен.</p>
                </div>
                <div class="footer">
                    <p>С уважением,<br>
                    <strong>Команда HAUS Price Ecosystem</strong></p>
                    <p>Это письмо отправлено автоматически. Пожалуйста, не отвечайте на него.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_subscription_renewed_body(self, subscription: Dict[str, Any]) -> str:
        """Генерация тела письма о продлении подписки"""
        expires_at = datetime.fromisoformat(subscription['expires_at']).strftime('%d.%m.%Y')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Подписка успешно продлена!</h1>
                </div>
                <div class="content">
                    <h2>Спасибо за доверие!</h2>
                    <p>Ваша подписка на тариф <strong>{subscription['tariff_name']}</strong> была успешно продлена.</p>
                    
                    <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3>Детали продления:</h3>
                        <p><strong>Тариф:</strong> {subscription['tariff_name']}</p>
                        <p><strong>Новая дата истечения:</strong> {expires_at}</p>
                        <p><strong>Стоимость:</strong> {subscription['price']} {subscription['currency']}</p>
                    </div>
                    
                    <p>Теперь вы можете продолжать пользоваться всеми преимуществами платформы без ограничений.</p>
                    
                    <p>Если у вас есть вопросы, пожалуйста, свяжитесь с нашей поддержкой.</p>
                </div>
                <div class="footer">
                    <p>С уважением,<br>
                    <strong>Команда HAUS Price Ecosystem</strong></p>
                    <p>Это письмо отправлено автоматически. Пожалуйста, не отвечайте на него.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_subscription_cancelled_body(self, subscription: Dict[str, Any]) -> str:
        """Генерация тела письма об отмене подписки"""
        expires_at = datetime.fromisoformat(subscription['expires_at']).strftime('%d.%m.%Y') if subscription.get('expires_at') else 'Н/Д'
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f44336; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Подписка отменена</h1>
                </div>
                <div class="content">
                    <h2>Ваша подписка была отменена</h2>
                    <p>Мы получили запрос на отмену вашей подписки на тариф <strong>{subscription['tariff_name']}</strong>.</p>
                    
                    <div style="background-color: white; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3>Детали:</h3>
                        <p><strong>Тариф:</strong> {subscription['tariff_name']}</p>
                        <p><strong>Дата истечения доступа:</strong> {expires_at}</p>
                        <p><strong>Причина отмены:</strong> {subscription.get('cancellation_reason', 'Не указана')}</p>
                    </div>
                    
                    <p>После истечения срока действия подписки доступ к платным функциям будет ограничен.</p>
                    <p>Вы всегда можете возобновить подписку в любое время в личном кабинете.</p>
                    
                    <p>Если это была ошибка или у вас есть вопросы, пожалуйста, свяжитесь с нашей поддержкой.</p>
                </div>
                <div class="footer">
                    <p>С уважением,<br>
                    <strong>Команда HAUS Price Ecosystem</strong></p>
                    <p>Это письмо отправлено автоматически. Пожалуйста, не отвечайте на него.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _generate_generic_subscription_body(self, subscription: Dict[str, Any]) -> str:
        """Генерация общего тела письма о подписке"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body>
            <h2>Уведомление о подписке</h2>
            <p>Тариф: {subscription['tariff_name']}</p>
            <p>Статус: {subscription['status']}</p>
            <p>С уважением, команда HAUS Price Ecosystem</p>
        </body>
        </html>
        """

# Экспорт
__all__ = ['NotificationService']
EOF
