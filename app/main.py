from fastapi import FastAPI, Request, HTTPException, Security, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
import time
import secrets

from app.core.config import settings
from app.core.logging_config import logger

tags_metadata = [
    {
        "name": "Dictionaries",
        "description": "Работа со справочниками (типы ДТП, дорожные условия и т.д.)",
    },
    {
        "name": "Accidents",
        "description": "Управление данными о дорожно-транспортных происшествиях",
    },
    {
        "name": "Analytics",
        "description": "Аналитические отчеты, расчет рисков и прогнозирование",
    },
    {
        "name": "System",
        "description": "Системные эндпоинты и проверка работоспособности",
    },
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
)

# Локализация ошибок валидации Pydantic
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    
    # Маппинг типов ошибок на русский язык
    error_type_mapping = {
        "missing": "Поле обязательно для заполнения",
        "int_parsing": "Значение должно быть целым числом",
        "float_parsing": "Значение должно быть числом",
        "string_too_short": "Минимальное количество символов: {limit_value}",
        "string_too_long": "Максимальное количество символов: {limit_value}",
        "value_error.any_str.min_length": "Минимальное количество символов: {limit_value}",
        "value_error.any_str.max_length": "Максимальное количество символов: {limit_value}",
        "type_error.integer": "Значение должно быть целым числом",
        "type_error.float": "Значение должно быть числом",
    }

    for error in exc.errors():
        error_type = error.get("type", "")
        loc = " -> ".join([str(x) for x in error.get("loc", [])])
        ctx = error.get("ctx", {})
        
        translated_msg = error_type_mapping.get(error_type, error.get("msg", "Ошибка валидации"))
        
        # Подстановка параметров в сообщение, если они есть
        if "{" in translated_msg and ctx:
            try:
                translated_msg = translated_msg.format(**ctx)
            except KeyError:
                pass
        
        errors.append({
            "location": loc,
            "message": translated_msg,
            "type": error_type
        })
        
    logger.error(f"Ошибка валидации: {errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors, "message": "Ошибка валидации входных данных"}
    )

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Определение заголовка для API-ключа
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        logger.warning("Попытка доступа без API-ключа")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ключ доступа не предоставлен"
        )
    
    # Используем secrets.compare_digest для защиты от атак по времени
    if not secrets.compare_digest(api_key, settings.X_API_KEY.get_secret_value()):
        logger.error("Некорректный API-ключ")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Некорректный ключ доступа"
        )
    return api_key

# Middleware для логирования запросов
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    
    if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health"]:
        return await call_next(request)

    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Latency: {process_time:.4f}s"
    )
    return response

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "version": settings.VERSION}

@app.get("/", tags=["System"])
async def root():
    return {"message": "Welcome to DTP Analytics API. Visit /docs for documentation."}

from app.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)
