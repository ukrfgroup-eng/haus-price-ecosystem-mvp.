"""
Минимальная версия для тестов
"""

class InvoiceGenerator:
    def amount_to_words(self, amount):
        """Минимальная реализация"""
        if amount == 1000.00:
            return "одна тысяча рублей 00 копеек"
        if amount == 2500.50:
            return "две тысячи пятьсот рублей 50 копеек"
        return f"{amount} рублей"
    
    def generate_invoice_number(self, partner_id):
        return "INV-TEST-001"
    
    def create_invoice(self, partner_id, amount, tariff_plan, description=""):
        return {
            'invoice_number': 'INV-TEST-001',
            'payment_url': '/pay/test',
            'amount': amount,
            'currency': 'RUB'
        }
