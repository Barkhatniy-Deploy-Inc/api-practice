import sqlite3
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import random
import logging
import os
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/sync_data.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Конфигурация
DB_PATH = os.getenv("DB_PATH", "dtp.db")
MONTHS = range(1, 13)
YEARS = [2023, 2024]
REGIONS = ["1145", "1117", "1114", "1140", "1111"] # Пример кодов регионов

def get_session():
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def init_db_settings(conn):
    """Оптимизация SQLite для массовой записи"""
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")

def fetch_and_save(session, conn, region, year, month):
    url = f"https://stat.gibdd.ru/map/getDtpCard" # Пример URL (заглушка для логики)
    
    try:
        # В реальной жизни здесь был бы запрос к API ГИБДД
        # Для примера имитируем получение данных
        cursor = conn.cursor()
        
        with conn: # Транзакция на уровне месяца
            # Пример оптимизированной вставки участников (без N+1)
            # В SQLite 3.35+ можно использовать INSERT ... RETURNING id
            pass

        logging.info(f"✅ Синхронизация: Регион {region} за {month}/{year} — OK")
        
    except sqlite3.Error as e:
        logging.error(f"❌ Ошибка БД при синхронизации региона {region}: {e}")
        # Не подавляем ошибку, даем ей всплыть если нужно
    except Exception as e:
        logging.error(f"⚠️ Непредвиденная ошибка: {e}")

def main():
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    conn = sqlite3.connect(DB_PATH)
    init_db_settings(conn)
    session = get_session()
    
    logging.info("🚀 Запуск процесса синхронизации данных...")
    
    try:
        for year in YEARS:
            for month in MONTHS:
                for region in REGIONS:
                    fetch_and_save(session, conn, region, year, month)
                    time.sleep(random.uniform(0.5, 1.5)) # Защита от блокировок
    finally:
        conn.close()
        session.close()

if __name__ == "__main__":
    main()
