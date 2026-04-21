from fastapi import APIRouter
from app.api.v1.endpoints import dictionaries, accidents, analytics

api_router = APIRouter()
api_router.include_router(dictionaries.router, prefix="/dictionaries", tags=["Dictionaries"])
api_router.include_router(accidents.router, prefix="/accidents", tags=["Accidents"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
