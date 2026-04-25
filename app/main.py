from fastapi import FastAPI, Request, HTTPException, Security, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.staticfiles import StaticFiles
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
import time
import secrets

from app.core.config import settings
from app.core.logging_config import logger
from app.db.session import get_db
from app.services import auth as auth_service
from app.crud import crud_auth

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
        "name": "Authentication",
        "description": "Управление API-ключами и аутентификация",
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
    docs_url=None,
    redoc_url=None,
    openapi_tags=tags_metadata,
)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Кастомный Swagger UI с локальной статикой"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger/swagger-ui.css",
        swagger_favicon_url="/static/favicon.png",
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """Кастомный ReDoc с локальной статикой"""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc/redoc.standalone.js",
        redoc_favicon_url="/static/favicon.png",
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
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
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

async def verify_api_key(
    x_api_key: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db)
):
    if not x_api_key:
        logger.warning("Попытка доступа без API-ключа")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ключ доступа не предоставлен"
        )
    
    # 1. Хешируем полученный ключ
    key_hash = auth_service.hash_key(x_api_key)
    
    # 2. Ищем его в БД через crud_auth.get_key_by_hash
    db_key = await crud_auth.get_key_by_hash(db, key_hash=key_hash)
    
    # 3. Если не найден или не активен — HTTP 403
    if not db_key:
        logger.error(f"Некорректный или неактивный API-ключ: {x_api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Некорректный или неактивный ключ доступа"
        )
    
    # 4. Если найден — пропускаем
    return x_api_key

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

@app.get("/robots.txt", include_in_schema=False)
async def robots_txt():
    """Отдача robots.txt для поисковых систем"""
    import os
    from fastapi.responses import FileResponse
    robots_path = os.path.join(os.getcwd(), "robots.txt")
    if os.path.exists(robots_path):
        return FileResponse(robots_path)
    return HTMLResponse(content="User-agent: *\nDisallow: /api/", media_type="text/plain")

@app.get("/", tags=["System"])
async def root():
    return {"message": "Welcome to Зебра-стат API. Visit /docs for documentation."}

# Импортируем api_router, который уже содержит auth_router
from app.api.v1.api import api_router

# Подключаем роутер. Зависимость verify_api_key теперь НЕ должна быть глобальной для всего роутера, 
# если мы хотим, чтобы /auth/keys работал. 
# Мы будем применять ее точечно в api.py или через инъекцию в main.
app.include_router(api_router, prefix=settings.API_V1_STR)
