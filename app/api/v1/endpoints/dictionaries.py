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
    DictionaryResponse
)

router = APIRouter()

@router.get("/regions", response_model=DictionaryResponse[RegionResponseSchema], summary="Список регионов")
async def read_regions(db: AsyncSession = Depends(get_db)):
    """Полный перечень субъектов РФ с привязкой к округам."""
    data = await crud_dictionaries.get_regions(db)
    return DictionaryResponse(total=len(data), data=data)

@router.get("/districts", response_model=DictionaryResponse[DistrictSchema], summary="Список округов")
async def read_districts(db: AsyncSession = Depends(get_db)):
    """Список федеральных округов Российской Федерации."""
    data = await crud_dictionaries.get_districts(db)
    return DictionaryResponse(total=len(data), data=data)

@router.get("/indicators", response_model=DictionaryResponse[Dict[str, str]], summary="Список индикаторов")
async def read_indicators():
    """Перечень доступных фильтров-индикаторов ДТП."""
    data = crud_dictionaries.get_indicators()
    return DictionaryResponse(total=len(data), data=data)

@router.get("/weather", response_model=DictionaryResponse[WeatherTypeSchema], summary="Справочник погоды")
async def read_weather(db: AsyncSession = Depends(get_db)):
    """Справочник типов погодных условий."""
    data = await crud_dictionaries.get_weather_types(db)
    return DictionaryResponse(total=len(data), data=data)

@router.get("/road-conditions", response_model=DictionaryResponse[RoadConditionSchema], summary="Состояние дорог")
async def read_road_conditions(db: AsyncSession = Depends(get_db)):
    """Справочник состояний дорожного покрытия."""
    data = await crud_dictionaries.get_road_conditions(db)
    return DictionaryResponse(total=len(data), data=data)

@router.get("/accident-types", response_model=DictionaryResponse[AccidentTypeSchema], summary="Виды ДТП")
async def read_accident_types(db: AsyncSession = Depends(get_db)):
    """Классификатор видов дорожно-транспортных происшествий."""
    data = await crud_dictionaries.get_accident_types(db)
    return DictionaryResponse(total=len(data), data=data)
