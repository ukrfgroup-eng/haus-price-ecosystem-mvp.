touch BLOCK_B_BOT_AI/scenarios/customer_scenario.py
cat > BLOCK_B_BOT_AI/scenarios/customer_scenario.py << 'EOF'
from .base_scenario import BaseScenario

class CustomerScenario(BaseScenario):
    def process(self, user_id, message, state, metadata):
        current_step = state.get('current_step', 'start')
        
        if current_step == 'start':
            return self._handle_start(user_id, message, state)
        elif current_step == 'collect_project_type':
            return self._handle_project_type(user_id, message, state)
        else:
            return {'text': 'Начните с команды /start', 'keyboard': None}
    
    def _handle_start(self, user_id, message, state):
        state['current_step'] = 'collect_project_type'
        return {
            'text': 'Какой тип работ вас интересует? (ремонт, строительство, дизайн)',
            'keyboard': None
        }
    
    def _handle_project_type(self, user_id, message, state):
        self.save_to_context(state, 'project_type', message)
        return {
            'text': f'Принято: {message}. Следующий шаг...',
            'keyboard': None
        }
EOF
