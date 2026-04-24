from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class TrendPoint(BaseModel):
    """Точка тренда"""
    model_config = ConfigDict(from_attributes=True)

    period: str = Field(..., description="Период (ГГГГ-ММ или ГГГГ)")
    count: int = Field(..., description="Количество ДТП")
    fatalities: int = Field(..., description="Количество погибших")
    injured: int = Field(..., description="Количество раненых")

class MonthlyTrendResponse(BaseModel):
    """Ответ по месячным трендам"""
    current: TrendPoint
    previous: TrendPoint
    growth_rate: float = Field(..., description="Темп роста в %")

class YearlyTrendResponse(BaseModel):
    """Ответ по годовым трендам"""
    items: List[TrendPoint]

class PredictionResponse(BaseModel):
    """Ответ с прогнозом"""
    next_period: str = Field(..., description="Прогнозируемый период")
    predicted_count: float = Field(..., description="Прогнозируемое количество ДТП")
    confidence_interval: float = Field(..., description="Доверительный интервал")

class RiskResponse(BaseModel):
    """Ответ по показателям риска"""
    region_code: Optional[str] = Field(None, description="Код региона")
    social_risk: float = Field(..., description="Социальный риск (погибшие на 100к населения)")
    transport_risk: float = Field(..., description="Транспортный риск (погибшие на 10к ТС)")

class CorrelationItem(BaseModel):
    """Элемент корреляционного анализа"""
    label: str = Field(..., description="Категория (например, 'Дождь' или '0-2 года')")
    count: int = Field(..., description="Количество ДТП")
    severity_index: float = Field(..., description="Индекс тяжести")

class CorrelationResponse(BaseModel):
    """Ответ по корреляционному анализу"""
    type: str = Field(..., description="Тип корреляции (weather, experience, lighting)")
    items: List[CorrelationItem]

class SummaryStatsResponse(BaseModel):
    """Сводная статистика"""
    total_accidents: int = Field(..., description="Общее количество ДТП")
    total_fatalities: int = Field(..., description="Общее количество погибших")
    total_injured: int = Field(..., description="Общее количество раненых")

class RegionStatsItem(BaseModel):
    """Статистика по региону"""
    name: str = Field(..., description="Название региона")
    code: str = Field(..., description="Код региона")
    accidents: int = Field(..., description="Количество ДТП")
    fatalities: int = Field(..., description="Количество погибших")

class RegionStatsResponse(BaseModel):
    """Ответ со статистикой по регионам"""
    items: List[RegionStatsItem]

class TimelineStatsItem(BaseModel):
    """Элемент временной шкалы"""
    period: str = Field(..., description="Период (день, месяц или год)")
    accidents: int = Field(..., description="Количество ДТП")
    fatalities: int = Field(..., description="Количество погибших")
    injured: int = Field(..., description="Количество раненых")

class TimelineStatsResponse(BaseModel):
    """Ответ с временной шкалой"""
    items: List[TimelineStatsItem]

class SeasonalityItem(BaseModel):
    """Статистика по сезону"""
    season: str = Field(..., description="Название сезона (Зима, Весна, Лето, Осень)")
    average_accidents: float = Field(..., description="Среднее количество ДТП")

class SeasonalityResponse(BaseModel):
    """Ответ по сезонности"""
    items: List[SeasonalityItem]

class DangerZoneItem(BaseModel):
    """Опасный участок"""
    road_name: str = Field(..., description="Название дороги/улицы")
    locality: str = Field(..., description="Населенный пункт")
    accidents_count: int = Field(..., description="Количество ДТП")

class DangerZonesResponse(BaseModel):
    """Ответ по опасным участкам"""
    items: List[DangerZoneItem]

class SafeRegionItem(BaseModel):
    """Рейтинг безопасности региона"""
    region_name: str = Field(..., description="Название региона")
    region_code: str = Field(..., description="Код региона")
    safety_score: float = Field(..., description="Индекс безопасности (чем ниже, тем безопаснее)")
    rank: int = Field(..., description="Место в рейтинге")

class SafeRegionsResponse(BaseModel):
    """Ответ по рейтингу безопасности регионов"""
    items: List[SafeRegionItem]

class ParticipantProfileResponse(BaseModel):
    """Схема профиля виновника"""
    gender: str = Field(..., description="Преобладающая пол")
    age_group: str = Field(..., description="Преобладающая возрастная группа")
    experience_group: str = Field(..., description="Преобладающий стаж")
    total_culprits: int = Field(..., description="Общее количество проанализированных виновников")

class ComparisonItem(BaseModel):
    """Схема элемента сравнения"""
    label: str
    accidents: int
    fatalities: int
    injured: int
    accidents_per_100k: float
    severity_index: float

class RegionComparisonResponse(BaseModel):
    """Ответ для сравнения регионов"""
    items: List[ComparisonItem]

class PeriodComparisonItem(BaseModel):
    """Элемент сравнения периодов"""
    period: str
    stats: SummaryStatsResponse

class PeriodComparisonResponse(BaseModel):
    """Ответ для сравнения периодов (АППГ)"""
    current: PeriodComparisonItem
    previous: PeriodComparisonItem
    delta_percent: Dict[str, float]

class ChildrenTraumaResponse(BaseModel):
    """Схема показателя детского травматизма"""
    total_accidents: int
    with_children: int
    trauma_rate: float

class HotspotPoint(BaseModel):
    """Точка на тепловой карте"""
    lat: float
    lon: float
    intensity: int

class HotspotsResponse(BaseModel):
    """Ответ для тепловой карты"""
    points: List[HotspotPoint]

class RegionalDashboardResponse(BaseModel):
    """Сводный дашборд региона"""
    summary: SummaryStatsResponse
    risks: RiskResponse
    seasonality: List[SeasonalityItem]
    top_danger_zones: List[DangerZoneItem]
