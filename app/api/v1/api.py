from fastapi import APIRouter, Depends
from app.api.v1.endpoints import dictionaries, accidents, analytics, auth, stats
from app.main import verify_api_key

api_router = APIRouter()

# --- ГРУППА 1: Публичные эндпоинты (только Master-Key для генерации) ---
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# --- ГРУППА 2: Защищенные эндпоинты (требуют X-API-KEY студента) ---
# Создаем отдельный роутер для защищенных ресурсов
protected_router = APIRouter(dependencies=[Depends(verify_api_key)])

protected_router.include_router(dictionaries.router, prefix="/dictionaries", tags=["Dictionaries"])
protected_router.include_router(accidents.router, prefix="/accidents", tags=["Accidents"])
protected_router.include_router(stats.router, prefix="/stats", tags=["Statistics"])
protected_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

api_router.include_router(protected_router)
