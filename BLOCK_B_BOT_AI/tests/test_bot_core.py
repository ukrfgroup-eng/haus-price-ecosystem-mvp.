touch BLOCK_B_BOT_AI/tests/test_bot_core.py
cat > BLOCK_B_BOT_AI/tests/test_bot_core.py << 'EOF'
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from bot_core import BotCore
from integrations.redis_manager import RedisManager

def test_detect_user_type():
    redis_mock = RedisManager('redis://localhost:6379/0')
    bot = BotCore(redis_mock)
    
    # Тест заказчика
    assert bot._detect_user_type('хочу построить дом').value == 'customer'
    
    # Тест партнера
    assert bot._detect_user_type('хочу стать партнером').value == 'partner'
    
    print("Все тесты прошли успешно!")

if __name__ == '__main__':
    test_detect_user_type()
EOF
