from typing import List, Optional
from pydantic import BaseModel, Field

class TrendPoint(BaseModel):
    """Точка тренда"""
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
