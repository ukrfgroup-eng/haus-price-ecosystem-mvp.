cat > demo_scenario.py << 'EOF'
"""
Демонстрационный сценарий из ТЗ: Полный цикл оплаты
"""

import sys
import os
from datetime import datetime, timedelta
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_demo_scenario():
    """Запуск демонстрационного сценария из ТЗ"""
    
    print("🚀 ЗАПУСК ДЕМО-СЦЕНАРИЯ: ПОЛНЫЙ ЦИКЛ ОПЛАТЫ")
    print("=" * 70)
    
    try:
        # Импортируем необходимые компоненты
        from config import config
        from services import (
            TariffService,
            SubscriptionManager,
            PaymentProcessor,
            InvoiceGenerator,
            NotificationService
        )
        
        # Инициализируем сервисы
        tariff_service = TariffService(config)
        subscription_manager = SubscriptionManager(config, tariff_service)
        payment_processor = PaymentProcessor(config)
        invoice_generator = InvoiceGenerator(config)
        notification_service = NotificationService(config)
        
        print("✅ Сервисы инициализированы")
        
        # Шаг 1: Партнер выбирает тариф "Professional" (5,000₽/месяц)
        print("\n1. Партнер выбирает тариф 'Professional' (5,000₽/месяц)")
        tariff = tariff_service.get_tariff('professional')
        print(f"   ✓ Выбран тариф: {tariff['name']}")
        print(f"   ✓ Цена: {tariff['price_monthly']} руб/мес")
        print(f"   ✓ Включено лидов: {tariff['leads_included']}")
        
        # Шаг 2: Система генерирует счет №INV-20240115-PART001-0001
        print("\n2. Система генерирует счет")
        invoice = invoice_generator.create_invoice(
            partner_id='PART001',
            client_info={
                'name': 'ООО "Тестовый Партнер"',
                'email': 'partner@example.com',
                'inn': '1234567890'
            },
            items=[{
                'name': f"Подписка {tariff['name']}",
                'quantity': 1,
                'price': tariff['price_monthly'],
                'total': tariff['price_monthly']
            }],
            tariff_code='professional'
        )
        print(f"   ✓ Сгенерирован счет: {invoice['invoice_number']}")
        print(f"   ✓ Сумма: {invoice['total_amount']} {invoice['currency']}")
        print(f"   ✓ Срок оплаты: {invoice['due_date'][:10]}")
        
        # Шаг 3: Отправляет счет на email партнера
        print("\n3. Отправка счета на email партнера")
        email_sent = notification_service.send_invoice_email(
            invoice=invoice,
            recipient_email='partner@example.com'
        )
        print(f"   ✓ Счет отправлен: {'Да' if email_sent else 'Нет (тестовый режим)'}")
        
        # Шаг 4: Партнер оплачивает через ЮKassa
        print("\n4. Партнер оплачивает через платежную систему")
        payment = payment_processor.create_payment(
            amount=invoice['total_amount'],
            currency=invoice['currency'],
            description=f"Оплата счета {invoice['invoice_number']}",
            partner_id='PART001',
            tariff_code='professional'
        )
        print(f"   ✓ Создан платеж: {payment['payment_id']}")
        print(f"   ✓ Сумма: {payment['amount']} {payment['currency']}")
        print(f"   ✓ Ссылка для оплаты: {payment['payment_url'][:50]}...")
        
        # Шаг 5: Вебхук подтверждает оплату
        print("\n5. Обработка оплаты (имитация вебхука)")
        payment_processed = payment_processor.process_payment(payment['payment_id'])
        print(f"   ✓ Платеж обработан: {'Успешно' if payment_processed else 'Ошибка'}")
        
        # Шаг 6: Система активирует подписку на 30 дней
        print("\n6. Активация подписки на 30 дней")
        subscription = subscription_manager.create_subscription(
            partner_id='PART001',
            tariff_code='professional',
            billing_period='monthly',
            auto_renewal=True
        )
        print(f"   ✓ Подписка активирована: {subscription['subscription_id']}")
        print(f"   ✓ Статус: {subscription['status']}")
        print(f"   ✓ Действует до: {subscription['expires_at'][:10]}")
        print(f"   ✓ Автопродление: {'Включено' if subscription['auto_renewal'] else 'Выключено'}")
        
        # Шаг 7: Отправляет подтверждение на email
        print("\n7. Отправка подтверждения на email")
        confirmation_sent = notification_service.send_payment_success_email(
            payment=payment,
            recipient_email='partner@example.com'
        )
        print(f"   ✓ Подтверждение отправлено: {'Да' if confirmation_sent else 'Нет (тестовый режим)'}")
        
        # Дополнительно: Проверка подписки
        print("\n8. Проверка активной подписки партнера")
        active_subscription = subscription_manager.get_partner_subscription('PART001')
        if active_subscription:
            print(f"   ✓ Активная подписка найдена")
            print(f"   ✓ ID: {active_subscription['subscription_id']}")
            print(f"   ✓ Тариф: {active_subscription['tariff_name']}")
        else:
            print("   ✗ Активная подписка не найдена")
        
        print("\n" + "=" * 70)
        print("🎉 ДЕМО-СЦЕНАРИЙ УСПЕШНО ВЫПОЛНЕН!")
        print("=" * 70)
        print("\nСозданные объекты:")
        print(f"  • Счет: {invoice['invoice_number']}")
        print(f"  • Платеж: {payment['payment_id']}")
        print(f"  • Подписка: {subscription['subscription_id']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА В СЦЕНАРИИ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_demo_scenario()
    sys.exit(0 if success else 1)
EOF
