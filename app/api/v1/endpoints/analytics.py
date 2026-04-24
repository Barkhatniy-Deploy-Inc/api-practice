from typing import List, Optional, Tuple, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud.crud_analytics import crud_analytics
from app.services.analytics import analytics_service
from app.schemas.analytics import (
    MonthlyTrendResponse, YearlyTrendResponse, TrendPoint,
    PredictionResponse, RiskResponse, CorrelationResponse, CorrelationItem,
    SummaryStatsResponse, SeasonalityResponse, SeasonalityItem,
    DangerZonesResponse, DangerZoneItem,
    SafeRegionsResponse, SafeRegionItem,
    ParticipantProfileResponse,
    RegionComparisonResponse, ComparisonItem,
    PeriodComparisonResponse, PeriodComparisonItem,
    ChildrenTraumaResponse, HotspotsResponse, HotspotPoint,
    RegionalDashboardResponse
)

router = APIRouter()

# --- ГРУППА 2: Тренды и Динамика ---

@router.get("/trends/monthly", response_model=MonthlyTrendResponse, summary="Месячные тренды")
async def get_monthly_trends(
    region_code: Optional[str] = Query(None, description="Код региона"),
    db: AsyncSession = Depends(get_db)
):
    """Анализ темпов роста или снижения аварийности по месяцам"""
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
    """Математический прогноз на будущий период на основе МНК"""
    stats = await crud_analytics.get_monthly_stats(db, region_code)
    if not stats:
        raise HTTPException(status_code=404, detail="Нет данных для прогноза")
    
    data = [s.count for s in reversed(stats[:12])]
    prediction, confidence = analytics_service.linear_regression_prediction(data)
    next_period = analytics_service.get_next_period(stats[0].month)
        
    return PredictionResponse(
        next_period=next_period,
        predicted_count=round(prediction, 2),
        confidence_interval=round(confidence, 2)
    )

@router.get("/seasonality", response_model=SeasonalityResponse, summary="Сезонность ДТП")
async def get_seasonality(db: AsyncSession = Depends(get_db)):
    """Выявление влияния времен года на безопасность"""
    stats = await crud_analytics.get_monthly_stats(db)
    if not stats:
        raise HTTPException(status_code=404, detail="Нет данных для анализа")
    
    processed_stats = [type('SeasonStat', (), {'month': s.month.split('-')[1], 'count': s.count})() for s in stats]
    items = analytics_service.calculate_seasonality(processed_stats)
    return SeasonalityResponse(items=[SeasonalityItem(**item) for item in items])

# --- ГРУППА 3: Сравнения и Рейтинги ---

@router.get("/compare/regions", response_model=RegionComparisonResponse, summary="Сравнение регионов")
async def compare_regions(
    codes: str = Query(..., description="Коды регионов через запятую"),
    db: AsyncSession = Depends(get_db)
):
    """Сравнительный анализ показателей двух и более субъектов РФ"""
    region_codes = [c.strip() for c in codes.split(',')]
    stats = await crud_analytics.get_multi_region_stats(db, region_codes)
    
    items = []
    for s in stats:
        pop = s.population or 0
        items.append(ComparisonItem(
            label=s.name,
            accidents=s.accidents,
            fatalities=s.fatalities or 0,
            injured=s.injured or 0,
            accidents_per_100k=round((s.accidents / pop * 100000), 2) if pop > 0 else 0,
            severity_index=analytics_service.calculate_severity_index(s.fatalities or 0, s.injured or 0)
        ))
    return RegionComparisonResponse(items=items)

@router.get("/compare/periods", response_model=PeriodComparisonResponse, summary="Сравнение периодов (АППГ)")
async def compare_periods(
    date_from: str = Query(..., description="Начало периода (ГГГГ-ММ-ДД)"),
    date_to: str = Query(..., description="Конец периода (ГГГГ-ММ-ДД)"),
    db: AsyncSession = Depends(get_db)
):
    """Сравнение статистики с аналогичным периодом прошлого года"""
    from datetime import datetime, timedelta
    cur_stats = await crud_analytics.get_summary_stats(db, date_from, date_to)
    
    d1 = datetime.strptime(date_from, "%Y-%m-%d")
    d2 = datetime.strptime(date_to, "%Y-%m-%d")
    prev_from = (d1 - timedelta(days=365)).strftime("%Y-%m-%d")
    prev_to = (d2 - timedelta(days=365)).strftime("%Y-%m-%d")
    prev_stats = await crud_analytics.get_summary_stats(db, prev_from, prev_to)
    
    cur_data = {"total_accidents": cur_stats.total_accidents or 0, "total_fatalities": cur_stats.total_fatalities or 0, "total_injured": cur_stats.total_injured or 0}
    prev_data = {"total_accidents": prev_stats.total_accidents or 0, "total_fatalities": prev_stats.total_fatalities or 0, "total_injured": prev_stats.total_injured or 0}
    
    return PeriodComparisonResponse(
        current=PeriodComparisonItem(period=f"{date_from} : {date_to}", stats=SummaryStatsResponse(**cur_data)),
        previous=PeriodComparisonItem(period=f"{prev_from} : {prev_to}", stats=SummaryStatsResponse(**prev_data)),
        delta_percent=analytics_service.calculate_delta(cur_data, prev_data)
    )

@router.get("/rating/danger-zones", response_model=DangerZonesResponse, summary="Опасные участки")
async def get_danger_zones(limit: int = Query(10, ge=1, le=50), db: AsyncSession = Depends(get_db)):
    """Топ самых аварийных участков трасс и улиц"""
    zones = await crud_analytics.get_danger_zones(db, limit)
    return DangerZonesResponse(items=[DangerZoneItem(road_name=z.road_name or "Не указана", locality=z.locality or "Не указан", accidents_count=z.accidents_count) for z in zones])

@router.get("/rating/safe-regions", response_model=SafeRegionsResponse, summary="Рейтинг безопасности")
async def get_safe_regions(db: AsyncSession = Depends(get_db)):
    """Рейтинг регионов по интегральному индексу безопасности"""
    data = await crud_analytics.get_safe_regions_data(db)
    if not data: raise HTTPException(status_code=404, detail="Нет данных")
    
    results = []
    for r in data:
        score = analytics_service.calculate_safety_score(r.accidents, r.population or 0, r.fatalities or 0, r.injured or 0)
        results.append({"region_name": r.name, "region_code": r.code, "safety_score": round(score, 4)})
    
    results.sort(key=lambda x: x["safety_score"])
    return SafeRegionsResponse(items=[SafeRegionItem(region_name=r["region_name"], region_code=r["region_code"], safety_score=r["safety_score"], rank=i + 1) for i, r in enumerate(results)])

# --- ГРУППА 4: Специализированные метрики ---

@router.get("/metrics/risks", response_model=RiskResponse, summary="Показатели риска")
async def get_risks(region_code: str = Query(...), db: AsyncSession = Depends(get_db)):
    """Расчет социального и транспортного рисков для региона"""
    data = await crud_analytics.get_region_risk_data(db, region_code)
    if not data: raise HTTPException(status_code=404, detail="Данные не найдены")
    return RiskResponse(region_code=region_code, social_risk=round(analytics_service.calculate_social_risk(data.fatalities or 0, data.population or 0), 2), transport_risk=round(analytics_service.calculate_transport_risk(data.fatalities or 0, data.vehicles or 0), 2))

@router.get("/metrics/children-trauma-rate", response_model=ChildrenTraumaResponse, summary="Детский травматизм")
async def get_children_trauma(region_code: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)):
    """Процент ДТП с участием детей"""
    stats = await crud_analytics.get_children_trauma_stats(db, region_code)
    rate = (stats["children"] / stats["total"] * 100) if stats["total"] > 0 else 0
    return ChildrenTraumaResponse(total_accidents=stats["total"], with_children=stats["children"], trauma_rate=round(rate, 2))

# --- ГРУППА 5: Корреляции ---

@router.get("/correlations/weather", response_model=CorrelationResponse, summary="Корреляция с погодой")
async def get_weather_correlation(region_code: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)):
    """Влияние погоды на тяжесть ДТП"""
    stats = await crud_analytics.get_weather_correlation(db, region_code)
    return CorrelationResponse(type="weather", items=[CorrelationItem(label=s.name, count=s.count, severity_index=round(analytics_service.calculate_severity_index(s.fatalities or 0, s.injured or 0), 4)) for s in stats])

@router.get("/correlations/experience", response_model=CorrelationResponse, summary="Корреляция со стажем")
async def get_experience_correlation(region_code: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)):
    """Зависимость аварийности от стажа водителей"""
    stats = await crud_analytics.get_experience_correlation(db, region_code)
    categories = analytics_service.map_experience_categories(stats)
    return CorrelationResponse(type="experience", items=[CorrelationItem(label=label, count=data["count"], severity_index=round(analytics_service.calculate_severity_index(data["fatalities"], data["injured"]), 4)) for label, data in categories.items() if data["count"] > 0])

@router.get("/correlations/lighting", response_model=CorrelationResponse, summary="Корреляция с освещением")
async def get_lighting_correlation(region_code: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)):
    """Влияние освещенности на тяжесть ДТП"""
    stats = await crud_analytics.get_lighting_correlation(db, region_code)
    return CorrelationResponse(type="lighting", items=[CorrelationItem(label=s.lighting or "Не указано", count=s.count, severity_index=round(analytics_service.calculate_severity_index(s.fatalities or 0, s.injured or 0), 4)) for s in stats])

# --- ГРУППА 6: Сводные отчеты ---

@router.get("/reports/hotspots-map", response_model=HotspotsResponse, summary="Тепловая карта")
async def get_hotspots(region_code: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)):
    """Кластеризованные координаты ДТП для карт"""
    coords = await crud_analytics.get_all_coordinates(db, region_code)
    points = analytics_service.cluster_coordinates(coords)
    return HotspotsResponse(points=[HotspotPoint(**p) for p in points])

@router.get("/reports/participant-profile", response_model=ParticipantProfileResponse, summary="Портрет виновника")
async def get_participant_profile(db: AsyncSession = Depends(get_db)):
    """Типичный статистический портрет виновника ДТП"""
    data = await crud_analytics.get_participant_profile_data(db)
    profile = analytics_service.calculate_participant_profile(data["raw_data"], default_gender=data["gender"], total_count=data["total_culprits"])
    return ParticipantProfileResponse(**profile)

@router.get("/reports/regional-dashboard", response_model=RegionalDashboardResponse, summary="Дашборд региона")
async def get_regional_dashboard(region_code: str = Query(...), db: AsyncSession = Depends(get_db)):
    """Агрегатор ключевых метрик для региона"""
    summary = await crud_analytics.get_summary_stats(db, region_code=region_code)
    risk_data = await crud_analytics.get_region_risk_data(db, region_code)
    raw_stats = await crud_analytics.get_monthly_stats(db, region_code)
    processed_stats = [type('SeasonStat', (), {'month': s.month.split('-')[1], 'count': s.count})() for s in raw_stats]
    seasonality = analytics_service.calculate_seasonality(processed_stats)
    zones = await crud_analytics.get_danger_zones(db, limit=5)
    
    return RegionalDashboardResponse(
        summary=SummaryStatsResponse(total_accidents=summary.total_accidents or 0, total_fatalities=summary.total_fatalities or 0, total_injured=summary.total_injured or 0),
        risks=RiskResponse(region_code=region_code, social_risk=analytics_service.calculate_social_risk(risk_data.fatalities or 0, risk_data.population or 0) if risk_data else 0, transport_risk=analytics_service.calculate_transport_risk(risk_data.fatalities or 0, risk_data.vehicles or 0) if risk_data else 0),
        seasonality=[SeasonalityItem(**s) for s in seasonality],
        top_danger_zones=[DangerZoneItem(road_name=z.road_name or "Не указана", locality=z.locality or "Не указан", accidents_count=z.accidents_count) for z in zones]
    )
