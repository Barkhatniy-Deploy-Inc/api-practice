from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud.crud_analytics import crud_analytics
from app.schemas.analytics import (
    SummaryStatsResponse, RegionStatsResponse, RegionStatsItem,
    TimelineStatsResponse, TimelineStatsItem
)

router = APIRouter()

@router.get("/summary", response_model=SummaryStatsResponse, summary="Сводная статистика")
async def get_summary(
    date_from: Optional[str] = Query(None, description="Дата начала (ГГГГ-ММ-ДД)"),
    date_to: Optional[str] = Query(None, description="Дата окончания (ГГГГ-ММ-ДД)"),
    region_code: Optional[str] = Query(None, description="Код региона"),
    db: AsyncSession = Depends(get_db)
):
    """Общая статистика ДТП, погибших и раненых за период"""
    stats = await crud_analytics.get_summary_stats(db, date_from, date_to, region_code)
    return SummaryStatsResponse(
        total_accidents=stats.total_accidents or 0,
        total_fatalities=stats.total_fatalities or 0,
        total_injured=stats.total_injured or 0
    )

@router.get("/regions", response_model=RegionStatsResponse, summary="Статистика по регионам")
async def get_regions(
    sort_by: str = Query("accidents", pattern="^(accidents|fatalities)$", description="Поле для сортировки"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="Порядок сортировки"),
    db: AsyncSession = Depends(get_db)
):
    """Рейтинг регионов по количеству ДТП или погибших"""
    stats = await crud_analytics.get_regional_stats(db, sort_by, order)
    items = [
        RegionStatsItem(
            name=s.name,
            code=s.code,
            accidents=s.accidents,
            fatalities=s.fatalities or 0
        )
        for s in stats
    ]
    return RegionStatsResponse(items=items)

@router.get("/timeline", response_model=TimelineStatsResponse, summary="Временная шкала")
async def get_timeline(
    interval: str = Query("month", pattern="^(day|month|year)$", description="Интервал группировки"),
    db: AsyncSession = Depends(get_db)
):
    """Динамика ДТП по дням, месяцам или годам"""
    stats = await crud_analytics.get_timeline_stats(db, interval)
    items = [
        TimelineStatsItem(
            period=s.period,
            accidents=s.accidents,
            fatalities=s.fatalities or 0,
            injured=s.injured or 0
        )
        for s in stats
    ]
    return TimelineStatsResponse(items=items)
