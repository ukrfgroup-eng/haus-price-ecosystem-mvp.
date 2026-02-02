#!/usr/bin/env python3
"""
Инициализация базы данных: создание таблиц
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.base import create_tables

if __name__ == "__main__":
    create_tables()
