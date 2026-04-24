from fastapi import APIRouter, Depends
from app.api.v1.endpoints import dictionaries, accidents, analytics, auth, stats
from app.main import verify_api_key

api_router = APIRouter()

# 1. Справочники (требуют ключ)
api_router.include_router(dictionaries.router, prefix="/dictionaries", tags=["Dictionaries"], dependencies=[Depends(verify_api_key)])

# 2. Реестр ДТП (требует ключ)
api_router.include_router(accidents.router, prefix="/accidents", tags=["Accidents"], dependencies=[Depends(verify_api_key)])

# 3. Базовая статистика (требует ключ)
api_router.include_router(stats.router, prefix="/stats", tags=["Statistics"], dependencies=[Depends(verify_api_key)])

# 4. Продвинутая аналитика (требует ключ)
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"], dependencies=[Depends(verify_api_key)])

# 5. Авторизация (свои зависимости внутри)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
