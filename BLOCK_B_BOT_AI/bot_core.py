touch BLOCK_B_BOT_AI/bot_core.py
cat > BLOCK_B_BOT_AI/bot_core.py << 'EOF'
import time
from enum import Enum

class UserType(Enum):
    UNKNOWN = "unknown"
    CUSTOMER = "customer"
    PARTNER = "partner"

class BotCore:
    def __init__(self, redis_manager):
        self.redis = redis_manager
    
    def process_message(self, user_id, message, platform, metadata):
        state = self.redis.get_state(user_id, platform)
        
        if state.get('user_type') == UserType.UNKNOWN.value:
            user_type = self._detect_user_type(message)
            state['user_type'] = user_type.value
        
        if state['user_type'] == UserType.CUSTOMER.value:
            from scenarios.customer_scenario import CustomerScenario
            scenario = CustomerScenario(self.redis)
        elif state['user_type'] == UserType.PARTNER.value:
            from scenarios.partner_scenario import PartnerScenario
            scenario = PartnerScenario(self.redis)
        else:
            return self._ask_user_type()
        
        response = scenario.process(user_id, message, state, metadata)
        self.redis.save_state(user_id, state, platform)
        return response
    
    def _detect_user_type(self, message):
        message = message.lower()
        
        customer_words = ['хочу', 'найти', 'ремонт', 'построить', 'ищу', 'нужен']
        partner_words = ['партнер', 'компания', 'зарегистрироваться', 'исполнитель']
        
        customer_score = sum(1 for word in customer_words if word in message)
        partner_score = sum(1 for word in partner_words if word in message)
        
        if customer_score > partner_score:
            return UserType.CUSTOMER
        elif partner_score > customer_score:
            return UserType.PARTNER
        else:
            return UserType.UNKNOWN
    
    def _ask_user_type(self):
        return {
            'text': 'Вы заказчик или партнер?',
            'keyboard': [
                [{'text': 'Заказчик', 'callback': 'customer'}],
                [{'text': 'Партнер', 'callback': 'partner'}]
            ]
        }
EOF
