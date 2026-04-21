from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud import crud_dictionaries
from app.schemas.dictionaries import (
    RegionResponseSchema, 
    WeatherTypeSchema, 
    RoadConditionSchema, 
    AccidentTypeSchema,
    BaseDictionarySchema
)

router = APIRouter()

@router.get("/regions", response_model=List[RegionResponseSchema], summary="Список регионов")
async def read_regions(db: AsyncSession = Depends(get_db)):
    """
    Возвращает полный перечень субъектов Российской Федерации с их характеристиками и названием федерального округа.
    """
    regions = await crud_dictionaries.get_regions(db)
    return [RegionResponseSchema.model_validate(r) for r in regions]

@router.get("/indicators", response_model=List[BaseDictionarySchema], summary="Список индикаторов")
async def read_indicators():
    """
    Список классификаторов (индикаторов), по которым можно фильтровать статистику.
    """
    indicators = crud_dictionaries.get_indicators()
    return [BaseDictionarySchema.model_validate(i) for i in indicators]

@router.get("/weather", response_model=List[WeatherTypeSchema], summary="Справочник погоды")
async def read_weather(db: AsyncSession = Depends(get_db)):
    """
    Справочник погодных условий на момент ДТП.
    """
    weather_types = await crud_dictionaries.get_weather_types(db)
    return [WeatherTypeSchema.model_validate(w) for w in weather_types]

@router.get("/road-conditions", response_model=List[RoadConditionSchema], summary="Состояние дорог")
async def read_road_conditions(db: AsyncSession = Depends(get_db)):
    """
    Классификатор состояния дорожного полотна.
    """
    road_conditions = await crud_dictionaries.get_road_conditions(db)
    return [RoadConditionSchema.model_validate(rc) for rc in road_conditions]

@router.get("/accident-types", response_model=List[AccidentTypeSchema], summary="Виды ДТП")
async def read_accident_types(db: AsyncSession = Depends(get_db)):
    """
    Официальный перечень видов дорожно-транспортных происшествий.
    """
    accident_types = await crud_dictionaries.get_accident_types(db)
    return [AccidentTypeSchema.model_validate(at) for at in accident_types]
