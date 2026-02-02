#!/usr/bin/env python3
"""
Создание миграции базы данных
"""
import os
import sys

# Запускаем alembic команды
os.system("alembic revision --autogenerate -m 'Создание таблиц партнеров и логов верификации'")
os.system("alembic upgrade head")
