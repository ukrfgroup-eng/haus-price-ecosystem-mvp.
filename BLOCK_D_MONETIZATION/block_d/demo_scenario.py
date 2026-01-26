cat > BLOCK_D_MONETIZATION/block_d/demo_scenario.py << 'EOF'
"""
Демонстрационный сценарий: Полный цикл оплаты
"""

import sys
import os
from datetime import datetime

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_demo_scenario():
    """Запуск демонстрационного сценария"""
    
    print("🚀 ЗАПУСК ДЕМО-СЦЕНАРИЯ: ПОЛНЫЙ ЦИКЛ ОПЛАТЫ")
    print("=" * 70)
    
    try:
        # Импортируем конфигурацию и сервисы
        from config import config
        from services.tariff_service import TariffService
        from services.subscription_manager import SubscriptionManager
        from services.payment_processor import PaymentProcessor
        from services.invoice_generator import InvoiceGenerator
        from services.notification_service import NotificationService
        
        # Инициализируем сервисы
        tariff_service = TariffService(config)
        subscription_manager = SubscriptionManager(config, tariff_service)
        payment_processor = PaymentProcessor(config)
        invoice_generator = InvoiceGenerator(config)
        notification_service = NotificationService(config)
        
        print("✅ Сервисы инициализированы")
        
        # Шаг 1: Партнер выбирает тариф
        print("\n1. Партнер выбирает тариф 'Professional' (5,000₽/месяц)")
        tariff = tariff_service.get_tariff('professional')
        print(f"   ✓ Выбран тариф: {tariff['name']}")
        print(f"   ✓ Цена: {tariff['price_monthly']} руб/мес")
        
        # Шаг 2: Генерация счета
        print("\n2. Система генерирует счет")
        invoice = invoice_generator.create_invoice(
            partner_id='PART001',
            client_info={
                'name': 'ООО "Тестовый Партнер"',
                'email': 'partner@example.com'
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
        
        # Шаг 3: Отправка счета
        print("\n3. Отправка счета на email партнера")
        email_sent = notification_service.send_invoice_email(
            invoice=invoice,
            recipient_email='partner@example.com'
        )
        print(f"   ✓ Счет отправлен: {'Да' if email_sent else 'Нет'}")
        
        # Шаг 4: Создание платежа
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
        
        # Шаг 5: Обработка платежа
        print("\n5. Обработка оплаты")
        payment_processed = payment_processor.process_payment(payment['payment_id'])
        print(f"   ✓ Платеж обработан: {'Успешно' if payment_processed else 'Ошибка'}")
        
        # Шаг 6: Активация подписки
        print("\n6. Активация подписки на 30 дней")
        subscription = subscription_manager.create_subscription(
            partner_id='PART001',
            tariff_code='professional',
            billing_period='monthly'
        )
        print(f"   ✓ Подписка активирована: {subscription['subscription_id']}")
        print(f"   ✓ Статус: {subscription['status']}")
        print(f"   ✓ Действует до: {subscription['expires_at'][:10]}")
        
        # Шаг 7: Отправка подтверждения
        print("\n7. Отправка подтверждения на email")
        confirmation_sent = notification_service.send_payment_success_email(
            payment=payment,
            recipient_email='partner@example.com'
        )
        print(f"   ✓ Подтверждение отправлено: {'Да' if confirmation_sent else 'Нет'}")
        
        # Итог
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
        return False

if __name__ == "__main__":
    success = run_demo_scenario()
    sys.exit(0 if success else 1)
EOF
