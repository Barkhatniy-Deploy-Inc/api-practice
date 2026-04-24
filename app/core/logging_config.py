import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from app.core.config import settings

def setup_logging():
    log_dir = Path("logs")
    handlers = [logging.StreamHandler(sys.stdout)]

    # Форматтер для логов
    log_format = (
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
        '"logger": "%(name)s", "message": "%(message)s"}'
    )

    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        handlers.append(
            RotatingFileHandler(
                log_dir / "api_access.log",
                maxBytes=10485760,
                backupCount=5,
                encoding="utf-8",
            )
        )
    except OSError as exc:
        print(
            f"Logging fallback: file handler is unavailable ({exc}). Using stdout only.",
            file=sys.stderr,
        )
    
    # Настройка корневого логгера
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format=log_format,
        handlers=handlers
    )
    
    # Отключаем лишний шум от uvicorn (необязательно, но полезно)
    # logging.getLogger("uvicorn.access").handlers = []
    
setup_logging()
logger = logging.getLogger("api.core")
