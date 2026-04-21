from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud.crud_analytics import crud_analytics
from app.services.analytics import analytics_service
from app.schemas.analytics import (
    MonthlyTrendResponse, YearlyTrendResponse, TrendPoint,
    PredictionResponse, RiskResponse, CorrelationResponse, CorrelationItem
)

router = APIRouter()

@router.get("/trends/monthly", response_model=MonthlyTrendResponse, summary="Месячные тренды")
async def get_monthly_trends(
    region_code: Optional[str] = Query(None, description="Код региона"),
    db: AsyncSession = Depends(get_db)
):
    """Анализ темпов роста или снижения аварийности по месяцацам"""
    stats = await crud_analytics.get_monthly_stats(db, region_code)
    if len(stats) < 2:
        raise HTTPException(status_code=404, detail="Недостаточно данных для анализа трендов")
    
    current = stats[0]
    previous = stats[1]
    
    growth_rate = analytics_service.calculate_growth_rate(current.count, previous.count)
    
    return MonthlyTrendResponse(
        current=TrendPoint.model_validate(current),
        previous=TrendPoint.model_validate(previous),
        growth_rate=growth_rate
    )

@router.get("/trends/yearly", response_model=YearlyTrendResponse, summary="Годовые тренды")
async def get_yearly_trends(
    region_code: Optional[str] = Query(None, description="Код региона"),
    db: AsyncSession = Depends(get_db)
):
    """Глобальный анализ изменений по годам"""
    stats = await crud_analytics.get_yearly_stats(db, region_code)
    items = [TrendPoint.model_validate(s) for s in stats]
    return YearlyTrendResponse(items=items)

@router.get("/trends/prediction", response_model=PredictionResponse, summary="Прогноз аварийности")
async def get_prediction(
    region_code: Optional[str] = Query(None, description="Код региона"),
    db: AsyncSession = Depends(get_db)
):
    """Математический прогноз на будущий период на основе последних 12 месяцев"""
    stats = await crud_analytics.get_monthly_stats(db, region_code)
    if not stats:
        raise HTTPException(status_code=404, detail="Нет данных для прогноза")
    
    # Берем последние 12 месяцев (или сколько есть) в хронологическом порядке
    data = [s.count for s in reversed(stats[:12])]
    prediction, confidence = analytics_service.linear_regression_prediction(data)
    
    # Определяем следующий период через сервис
    next_period = analytics_service.get_next_period(stats[0].month)
        
    return PredictionResponse(
        next_period=next_period,
        predicted_count=round(prediction, 2),
        confidence_interval=round(confidence, 2)
    )

@router.get("/risks", response_model=RiskResponse, summary="Показатели риска")
async def get_risks(
    region_code: str = Query(..., description="Код региона"),
    db: AsyncSession = Depends(get_db)
):
    """Расчет социального и транспортного рисков для региона"""
    data = await crud_analytics.get_region_risk_data(db, region_code)
    if not data:
        raise HTTPException(status_code=404, detail="Данные по региону не найдены")
    
    social_risk = analytics_service.calculate_social_risk(data.fatalities or 0, data.population or 0)
    transport_risk = analytics_service.calculate_transport_risk(data.fatalities or 0, data.vehicles or 0)
    
    return RiskResponse(
        region_code=region_code,
        social_risk=round(social_risk, 2),
        transport_risk=round(transport_risk, 2)
    )

@router.get("/correlations/weather", response_model=CorrelationResponse, summary="Корреляция с погодой")
async def get_weather_correlation(
    region_code: Optional[str] = Query(None, description="Код региона"),
    db: AsyncSession = Depends(get_db)
):
    """Влияние погоды на тяжесть ДТП"""
    stats = await crud_analytics.get_weather_correlation(db, region_code)
    items = [
        CorrelationItem(
            label=s.name,
            count=s.count,
            severity_index=round(analytics_service.calculate_severity_index(s.fatalities or 0, s.injured or 0), 4)
        )
        for s in stats
    ]
    return CorrelationResponse(type="weather", items=items)

@router.get("/correlations/experience", response_model=CorrelationResponse, summary="Корреляция со стажем")
async def get_experience_correlation(
    region_code: Optional[str] = Query(None, description="Код региона"),
    db: AsyncSession = Depends(get_db)
):
    """Зависимость аварийности от стажа виновников"""
    stats = await crud_analytics.get_experience_correlation(db, region_code)
    
    # Используем сервис для маппинга категорий
    categories = analytics_service.map_experience_categories(stats)
    
    items = [
        CorrelationItem(
            label=label,
            count=data["count"],
            severity_index=round(analytics_service.calculate_severity_index(data["fatalities"], data["injured"]), 4)
        )
        for label, data in categories.items() if data["count"] > 0
    ]
    return CorrelationResponse(type="experience", items=items)

@router.get("/correlations/lighting", response_model=CorrelationResponse, summary="Корреляция с освещением")
async def get_lighting_correlation(
    region_code: Optional[str] = Query(None, description="Код региона"),
    db: AsyncSession = Depends(get_db)
):
    """Анализ влияния освещенности на тяжесть ДТП"""
    stats = await crud_analytics.get_lighting_correlation(db, region_code)
    items = [
        CorrelationItem(
            label=s.lighting or "Не указано",
            count=s.count,
            severity_index=round(analytics_service.calculate_severity_index(s.fatalities or 0, s.injured or 0), 4)
        )
        for s in stats
    ]
    return CorrelationResponse(type="lighting", items=items)
