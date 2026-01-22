"""
БЛОК B: БОТ-ПРОВОДНИК + AI-АНАЛИЗ
Интеллектуальный бот-проводник для взаимодействия с обеими группами пользователей
"""

__version__ = "1.0.0"
__description__ = "AI-проводник для заказчиков и партнеров"

from .bot_scenarios import BOT_SCENARIOS, get_scenario
from .ai_analyzer import AIAnalyzer
from .request_processor import RequestProcessor
from .response_formatter import ResponseFormatter

__all__ = [
    'BOT_SCENARIOS',
    'get_scenario',
    'AIAnalyzer', 
    'RequestProcessor',
    'ResponseFormatter'
]
