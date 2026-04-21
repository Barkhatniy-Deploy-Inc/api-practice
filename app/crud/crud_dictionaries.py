from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.models.dictionaries import Region, District, WeatherType, RoadCondition, AccidentType

async def get_regions(db: AsyncSession) -> List[Dict]:
    """
    Получает список регионов с названием федерального округа.
    """
    query = select(Region, District.name.label("district_name")).join(District, Region.district_id == District.id)
    result = await db.execute(query)
    
    regions_data = []
    for row in result:
        region, district_name = row
        regions_data.append({
            "region_code": region.code,
            "region_name": region.name,
            "district_name": district_name,
            "population": region.population,
            "vehicles_count": region.vehicles
        })
    return regions_data

async def get_weather_types(db: AsyncSession) -> List[WeatherType]:
    """
    Получает справочник погодных условий.
    """
    query = select(WeatherType)
    result = await db.execute(query)
    return result.scalars().all()

async def get_road_conditions(db: AsyncSession) -> List[RoadCondition]:
    """
    Получает справочник состояния дорожного полотна.
    """
    query = select(RoadCondition)
    result = await db.execute(query)
    return result.scalars().all()

async def get_accident_types(db: AsyncSession) -> List[AccidentType]:
    """
    Получает справочник видов ДТП.
    """
    query = select(AccidentType)
    result = await db.execute(query)
    return result.scalars().all()

def get_indicators() -> List[Dict[str, str]]:
    """
    Возвращает статический список индикаторов для фильтрации.
    """
    return [
        {"id": "has_drunk", "name": "С участием нетрезвых водителей"},
        {"id": "has_children", "name": "С участием детей"},
        {"id": "driver_fled", "name": "Водитель скрылся"},
        {"id": "fatalities", "name": "С погибшими"},
        {"id": "injured", "name": "С ранеными"}
    ]
