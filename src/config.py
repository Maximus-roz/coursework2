import os
from pathlib import Path

from dotenv import load_dotenv

# Ищем .env в корне проекта (на уровень выше src/)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "aeroplanes_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),  # без дефолтного пароля
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "client_encoding": "utf8",
    "options": "-c client_encoding=UTF8 -c lc_messages=C",
}

TRACKED_COUNTRIES = ["italia", "germany", "france", "spain"]
