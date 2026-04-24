from typing import List, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud import crud_dictionaries
from app.schemas.dictionaries import (
    RegionResponseSchema, 
    WeatherTypeSchema, 
    RoadConditionSchema, 
    AccidentTypeSchema,
    DistrictSchema,
)

router = APIRouter()

@router.get("/regions", response_model=List[RegionResponseSchema], summary="Список регионов")
async def read_regions(db: AsyncSession = Depends(get_db)):
    """Полный перечень субъектов РФ с привязкой к округам."""
    return await crud_dictionaries.get_regions(db)

@router.get("/districts", response_model=List[DistrictSchema], summary="Список округов")
async def read_districts(db: AsyncSession = Depends(get_db)):
    """Список федеральных округов Российской Федерации."""
    return await crud_dictionaries.get_districts(db)

@router.get("/indicators", response_model=List[Dict[str, str]], summary="Список индикаторов")
async def read_indicators():
    """Перечень доступных фильтров-индикаторов ДТП."""
    return crud_dictionaries.get_indicators()

@router.get("/weather", response_model=List[WeatherTypeSchema], summary="Справочник погоды")
async def read_weather(db: AsyncSession = Depends(get_db)):
    """Справочник типов погодных условий."""
    return await crud_dictionaries.get_weather_types(db)

@router.get("/road-conditions", response_model=List[RoadConditionSchema], summary="Состояние дорог")
async def read_road_conditions(db: AsyncSession = Depends(get_db)):
    """Справочник состояний дорожного покрытия."""
    return await crud_dictionaries.get_road_conditions(db)

@router.get("/accident-types", response_model=List[AccidentTypeSchema], summary="Виды ДТП")
async def read_accident_types(db: AsyncSession = Depends(get_db)):
    """Классификатор видов дорожно-транспортных происшествий."""
    return await crud_dictionaries.get_accident_types(db)
