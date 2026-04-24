import pytest
from app.services.analytics import analytics_service
from app.crud import crud_dictionaries
from app.api.v1.endpoints import dictionaries
from fastapi import HTTPException
from typing import List, Any

# 1. Тесты для AnalyticsService (закрываем Miss в app/services/analytics.py)

def test_calculate_growth_rate_edge_cases():
    assert analytics_service.calculate_growth_rate(50, 0) == 100.0
    assert analytics_service.calculate_growth_rate(0, 0) == 0.0
    assert analytics_service.calculate_growth_rate(100, 100) == 0.0

def test_calculate_severity_index_logic():
    # 0 погибших, 0 раненых
    assert analytics_service.calculate_severity_index(0, 0) == 0.0
    # 1 погибший, 0 раненых (индекс 1.0, т.е. 100% тяжесть)
    assert analytics_service.calculate_severity_index(1, 0) == 1.0
    # 1 погибший, 1 раненый (индекс 0.5)
    assert analytics_service.calculate_severity_index(1, 1) == 0.5

def test_calculate_risks():
    # Социальный риск
    assert analytics_service.calculate_social_risk(1, 100000) == 1.0
    assert analytics_service.calculate_social_risk(1, 0) == 0.0
    
    # Транспортный риск
    assert analytics_service.calculate_transport_risk(1, 10000) == 1.0
    assert analytics_service.calculate_transport_risk(1, 0) == 0.0

def test_map_experience_categories_structure():
    # Метод всегда возвращает скелет словаря
    res = analytics_service.map_experience_categories([])
    assert "0-2 года" in res
    assert res["0-2 года"]["count"] == 0

def test_calculate_seasonality_logic():
    class MockStat:
        def __init__(self, month, count):
            self.month = month
            self.count = count
    
    # 1 ДТП в январе (Зима)
    stats = [MockStat(1, 10)]
    res = analytics_service.calculate_seasonality(stats)
    winter = next(item for item in res if item["season"] == "Зима")
    assert winter["average_accidents"] == 3.33
    summer = next(item for item in res if item["season"] == "Лето")
    assert summer["average_accidents"] == 0.0

def test_calculate_participant_profile_nulls():
    class MockParticipant:
        def __init__(self, age, experience):
            self.age = age
            self.experience = experience
    
    parts = [MockParticipant(None, None)]
    res = analytics_service.calculate_participant_profile(parts, default_gender="Мужской", total_count=1)
    assert res["age_group"] == "Не указан"
    assert res["experience_group"] == "Не указан"
    assert res["gender"] == "Мужской"

def test_calculate_safety_score_logic():
    # 100 ДТП на 1000 населения = 10000 на 100к.
    # 10 погибших, 90 раненых = Индекс тяжести 0.1 (10/100)
    score = analytics_service.calculate_safety_score(100, 1000, 10, 90)
    # (10000 * 0.4) + (0.1 * 0.6) = 4000 + 0.06 = 4000.06
    assert round(score, 2) == 4000.06

# 2. Тесты для CRUD и Эндпоинтов справочников

@pytest.mark.asyncio
async def test_crud_dictionaries_existence():
    assert callable(crud_dictionaries.get_regions)
    assert callable(crud_dictionaries.get_indicators)
    assert callable(crud_dictionaries.get_weather_types)
    assert callable(crud_dictionaries.get_road_conditions)
    assert callable(crud_dictionaries.get_accident_types)

def test_static_indicators():
    indicators = crud_dictionaries.get_indicators()
    assert isinstance(indicators, list)
    assert len(indicators) > 0
    assert indicators[0]["id"] == "has_drunk"
