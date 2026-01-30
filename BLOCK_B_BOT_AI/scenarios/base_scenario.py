touch BLOCK_B_BOT_AI/scenarios/base_scenario.py
cat > BLOCK_B_BOT_AI/scenarios/base_scenario.py << 'EOF'
class BaseScenario:
    def __init__(self, redis_manager):
        self.redis = redis_manager
    
    def process(self, user_id, message, state, metadata):
        raise NotImplementedError
    
    def save_to_context(self, state, key, value):
        if 'context' not in state:
            state['context'] = {}
        state['context'][key] = value
    
    def get_from_context(self, state, key, default=None):
        return state.get('context', {}).get(key, default)
EOF
