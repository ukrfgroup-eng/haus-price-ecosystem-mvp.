"""
Invoice Generator - система генерации счетов для партнеров
"""

import os
import logging
from datetime import datetime, timedelta
from jinja2 import Template
from backend.models import db, Partner, Payment

logger = logging.getLogger(__name__)


class InvoiceGenerator:
    def __init__(self):
        self.templates_dir = os.path.join(os.path.dirname(__file__), '../templates/invoices')
        self.ensure_directories()
    
    def ensure_directories(self):
        """Создание необходимых директорий"""
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs('invoices', exist_ok=True)
    
    def generate_invoice_number(self, partner_id):
        """Генерация номера счета"""
        date_prefix = datetime.now().strftime('%y%m%d')
        count = Payment.query.filter(
            Payment.partner_id == partner_id,
            Payment.created_at >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count() + 1
        
        return f"INV-{date_prefix}-{partner_id[:6]}-{count:04d}"
    
    def create_invoice(self, partner_id, amount, tariff_plan, description="Оплата подписки"):
        """Создание нового счета"""
        try:
            partner = Partner.query.filter_by(partner_id=partner_id).first()
            if not partner:
                logger.error(f"Партнер {partner_id} не найден")
                return None
            
            # Создаем платеж
            payment = Payment(
                payment_number=self.generate_invoice_number(partner_id),
                partner_id=partner_id,
                amount=amount,
                currency='RUB',
                status='pending',
                payment_type='subscription',
                tariff_plan=tariff_plan,
                description=description,
                invoice_data={
                    'company_name': partner.company_name,
                    'inn': partner.inn,
                    'legal_address': partner.legal_address or partner.actual_address,
                    'contact_person': partner.contact_person,
                    'email': partner.email
                }
            )
            
            db.session.add(payment)
            db.session.commit()
            
            # Генерируем HTML счета
            invoice_html = self.generate_invoice_html(payment)
            
            # Сохраняем HTML в файл
            invoice_filename = f"invoices/{payment.payment_number}.html"
            with open(invoice_filename, 'w', encoding='utf-8') as f:
                f.write(invoice_html)
            
            payment.invoice_file = invoice_filename
            db.session.commit()
            
            logger.info(f"Создан счет {payment.payment_number} для партнера {partner_id}")
            
            return {
                'invoice_number': payment.payment_number,
                'invoice_file': invoice_filename,
                'payment_url': f"/api/v1/payments/{payment.id}/pay",
                'amount': amount,
                'currency': 'RUB',
                'due_date': (datetime.now() + timedelta(days=3)).strftime('%d.%m.%Y')
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания счета: {e}")
            db.session.rollback()
            return None
    
    def generate_invoice_html(self, payment):
        """Генерация HTML счета"""
        template_content = """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Счет № {{ invoice_number }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { text-align: center; margin-bottom: 40px; }
                .invoice-info { margin-bottom: 30px; }
                .table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                .table th, .table td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                .table th { background-color: #f4f4f4; }
                .total { font-size: 18px; font-weight: bold; text-align: right; }
                .footer { margin-top: 50px; font-size: 12px; color: #666; }
                .bank-details { margin-top: 30px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Счет на оплату № {{ invoice_number }}</h1>
                <p>Дата: {{ invoice_date }}</p>
            </div>
            
            <div class="invoice-info">
                <p><strong>Поставщик:</strong> ООО "Дома-Цены.РФ"</p>
                <p><strong>ИНН:</strong> 1234567890</p>
                <p><strong>КПП:</strong> 123456789</p>
                <p><strong>Банк:</strong> ПАО "Сбербанк"</p>
                <p><strong>Р/с:</strong> 40702810123456789012</p>
                <p><strong>К/с:</strong> 30101234500000000222</p>
                <p><strong>БИК:</strong> 044525222</p>
            </div>
            
            <div class="invoice-info">
                <p><strong>Покупатель:</strong> {{ company_name }}</p>
                <p><strong>ИНН:</strong> {{ inn }}</p>
                <p><strong>Адрес:</strong> {{ legal_address }}</p>
                <p><strong>Контактное лицо:</strong> {{ contact_person }}</p>
                <p><strong>Email:</strong> {{ email }}</p>
            </div>
            
            <table class="table">
                <thead>
                    <tr>
                        <th>№</th>
                        <th>Наименование</th>
                        <th>Количество</th>
                        <th>Цена</th>
                        <th>Сумма</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1</td>
                        <td>{{ description }}</td>
                        <td>1</td>
                        <td>{{ amount }} {{ currency }}</td>
                        <td>{{ amount }} {{ currency }}</td>
                    </tr>
                </tbody>
            </table>
            
            <div class="total">
                <p>Итого к оплате: {{ amount }} {{ currency }}</p>
                <p>Сумма прописью: {{ amount_words }}</p>
            </div>
            
            <div class="bank-details">
                <p><strong>Назначение платежа:</strong> Оплата по счету № {{ invoice_number }} от {{ invoice_date }}</p>
            </div>
            
            <div class="footer">
                <p>Счет действителен до: {{ due_date }}</p>
                <p>Данный документ является счетом на оплату и не содержит НДС (применяется УСН)</p>
            </div>
        </body>
        </html>
        """
        
        template = Template(template_content)
        
        # Конвертация суммы прописью
        amount_words = self.amount_to_words(payment.amount)
        
        html = template.render(
            invoice_number=payment.payment_number,
            invoice_date=payment.created_at.strftime('%d.%m.%Y'),
            company_name=payment.invoice_data.get('company_name', ''),
            inn=payment.invoice_data.get('inn', ''),
            legal_address=payment.invoice_data.get('legal_address', ''),
            contact_person=payment.invoice_data.get('contact_person', ''),
            email=payment.invoice_data.get('email', ''),
            description=payment.description,
            amount=payment.amount,
            currency=payment.currency,
            amount_words=amount_words,
            due_date=(payment.created_at + timedelta(days=3)).strftime('%d.%m.%Y')
        )
        
        return html
    
    def amount_to_words(self, amount):
        """Конвертация суммы прописью"""
        units = ['', 'один', 'два', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять']
        teens = ['десять', 'одиннадцать', 'двенадцать', 'тринадцать', 'четырнадцать', 
                'пятнадцать', 'шестнадцать', 'семнадцать', 'восемнадцать', 'девятнадцать']
        tens = ['', '', 'двадцать', 'тридцать', 'сорок', 'пятьдесят', 
               'шестьдесят', 'семьдесят', 'восемьдесят', 'девяносто']
        hundreds = ['', 'сто', 'двести', 'триста', 'четыреста', 'пятьсот', 
                   'шестьсот', 'семьсот', 'восемьсот', 'девятьсот']
        
        rubles = int(amount)
        kopecks = int((amount - rubles) * 100)
        
        def number_to_words(n):
            if n == 0:
                return 'ноль'
            
            words = []
            
            # Тысячи
            if n >= 1000:
                thousands = n // 1000
                if thousands == 1:
                    words.append('одна тысяча')
                elif thousands == 2:
                    words.append('две тысячи')
                elif thousands >= 3 and thousands <= 4:
                    words.append(units[thousands] + ' тысячи')
                else:
                    words.append(self.number_to_words_simple(thousands) + ' тысяч')
                n %= 1000
            
            # Сотни
            if n >= 100:
                words.append(hundreds[n // 100])
                n %= 100
            
            # Десятки и единицы
            if n >= 20:
                words.append(tens[n // 10])
                n %= 10
                if n > 0:
                    words.append(units[n])
            elif n >= 10:
                words.append(teens[n - 10])
            elif n > 0:
                words.append(units[n])
            
            return ' '.join(filter(None, words))
        
        ruble_words = number_to_words(rubles)
        if rubles % 10 == 1 and rubles % 100 != 11:
            ruble_text = 'рубль'
        elif rubles % 10 in [2, 3, 4] and rubles % 100 not in [12, 13, 14]:
            ruble_text = 'рубля'
        else:
            ruble_text = 'рублей'
        
        kopeck_words = number_to_words(kopecks)
        if kopecks % 10 == 1 and kopecks % 100 != 11:
            kopeck_text = 'копейка'
        elif kopecks % 10 in [2, 3, 4] and kopecks % 100 not in [12, 13, 14]:
            kopeck_text = 'копейки'
        else:
            kopeck_text = 'копеек'
        
        return f"{ruble_words} {ruble_text} {kopecks:02d} {kopeck_text}"
    
    def get_invoice(self, invoice_number):
        """Получение информации о счете"""
        payment = Payment.query.filter_by(payment_number=invoice_number).first()
        if not payment:
            return None
        
        return {
            'invoice_number': payment.payment_number,
            'partner_id': payment.partner_id,
            'amount': payment.amount,
            'currency': payment.currency,
            'status': payment.status,
            'created_at': payment.created_at,
            'paid_at': payment.paid_at,
            'description': payment.description,
            'invoice_file': payment.invoice_file
        }
