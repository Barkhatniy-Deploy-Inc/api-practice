from typing import List, Optional
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from app.models.dtp import Accident, Vehicle
from app.crud.base import CRUDBase

async def get_accidents(
    db: AsyncSession,
    *,
    limit: int = 50,
    offset: int = 0,
    region_code: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    has_children: Optional[bool] = None,
    has_drunk: Optional[bool] = None,
) -> List[Accident]:
    """
    Получение списка ДТП с фильтрацией и пагинацией.
    """
    query = select(Accident)
    query = CRUDBase._apply_accident_filters(
        query,
        region_code=region_code,
        date_from=date_from,
        date_to=date_to,
        has_children=has_children,
        has_drunk=has_drunk
    )
    
    query = query.limit(limit).offset(offset).order_by(Accident.date_dtp.desc(), Accident.time_dtp.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_accidents_count(
    db: AsyncSession,
    *,
    region_code: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    has_children: Optional[bool] = None,
    has_drunk: Optional[bool] = None,
) -> int:
    """
    Получение общего количества ДТП по фильтрам.
    """
    query = select(func.count(Accident.id))
    query = CRUDBase._apply_accident_filters(
        query,
        region_code=region_code,
        date_from=date_from,
        date_to=date_to,
        has_children=has_children,
        has_drunk=has_drunk
    )
    
    result = await db.execute(query)
    return result.scalar() or 0

async def get_accident_by_id(db: AsyncSession, accident_id: int) -> Optional[Accident]:
    """
    Получение детальной информации о ДТП по ID.
    """
    query = (
        select(Accident)
        .where(Accident.id == accident_id)
        .options(
            joinedload(Accident.weather),
            joinedload(Accident.road_condition),
            selectinload(Accident.vehicles).joinedload(Vehicle.car_type),
            selectinload(Accident.vehicles).joinedload(Vehicle.car_model),
            selectinload(Accident.participants)
        )
    )
    result = await db.execute(query)
    return result.scalars().first()
