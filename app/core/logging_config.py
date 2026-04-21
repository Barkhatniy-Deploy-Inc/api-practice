import logging
import sys
from logging.handlers import RotatingFileHandler
from app.core.config import settings
import os

def setup_logging():
    # Создаем папку для логов, если её нет
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Форматтер для логов
    log_format = (
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
        '"logger": "%(name)s", "message": "%(message)s"}'
    )
    
    # Настройка корневого логгера
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler(
                "logs/api_access.log", 
                maxBytes=10485760, 
                backupCount=5,
                encoding="utf-8"
            )
        ]
    )
    
    # Отключаем лишний шум от uvicorn (необязательно, но полезно)
    # logging.getLogger("uvicorn.access").handlers = []
    
setup_logging()
logger = logging.getLogger("api.core")
