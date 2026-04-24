from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.crud import crud_accidents
from app.schemas.accidents import (
    AccidentDetailSchema,
    AccidentsResponse,
    AccidentShortSchema
)

router = APIRouter()

@router.get("/", response_model=AccidentsResponse, summary="Реестр ДТП")
async def read_accidents(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=100, description="Количество записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    region_code: Optional[str] = Query(None, description="Код региона"),
    date_from: Optional[date] = Query(None, description="Дата С (ГГГГ-ММ-ДД)"),
    date_to: Optional[date] = Query(None, description="Дата ПО (ГГГГ-ММ-ДД)"),
    has_children: Optional[bool] = Query(None, description="Только с детьми"),
    has_drunk: Optional[bool] = Query(None, description="Только с нетрезвыми"),
):
    """
    Основной реестр происшествий с системой фильтрации и пагинации.
    """
    total = await crud_accidents.get_accidents_count(
        db,
        region_code=region_code,
        date_from=date_from,
        date_to=date_to,
        has_children=has_children,
        has_drunk=has_drunk
    )
    items = await crud_accidents.get_accidents(
        db,
        limit=limit,
        offset=offset,
        region_code=region_code,
        date_from=date_from,
        date_to=date_to,
        has_children=has_children,
        has_drunk=has_drunk
    )
    
    # Использование model_validate для преобразования объектов БД в схемы
    return {
        "total": total, 
        "items": [AccidentShortSchema.model_validate(item) for item in items]
    }

@router.get("/{id}", response_model=AccidentDetailSchema, summary="Детальная информация о ДТП")
async def read_accident(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Максимально полная информация по конкретному инциденту.
    Сбор данных из таблиц: accidents, vehicles (марки, модели), participants (роль, стаж, здоровье).
    """
    accident = await crud_accidents.get_accident_by_id(db, id)
    if not accident:
        raise HTTPException(status_code=404, detail="ДТП не найдено")
    
    # Подготовка данных для вложенных схем
    main_info = {
        "coords": (accident.coord_lat, accident.coord_lon),
        "weather": accident.weather.name if accident.weather else None,
        "road_condition": accident.road_condition.name if accident.road_condition else None,
        "locality": accident.locality,
        "road_name": accident.road_name,
        "road_km": accident.road_km
    }
    
    vehicles = [
        {
            "id": v.id,
            "car_type_name": v.car_type.name if v.car_type else None,
            "car_brand": v.car_model.brand if v.car_model else None,
            "car_model_name": v.car_model.name if v.car_model else None,
            "year_release": v.year_release,
            "is_defective": bool(v.is_defective)
        } for v in accident.vehicles
    ]
    
    participants = [
        {
            "id": p.id,
            "role": p.role,
            "gender": p.gender,
            "age": p.age,
            "health_status": p.health_status,
            "experience": p.experience,
            "is_drunk": p.is_drunk,
            "is_culprit": p.is_culprit
        } for p in accident.participants
    ]
    
    # Использование model_validate для формирования итогового ответа
    return AccidentDetailSchema.model_validate({
        "id": accident.id,
        "empt_number": accident.empt_number,
        "main_info": main_info,
        "vehicles": vehicles,
        "participants": participants
    })
