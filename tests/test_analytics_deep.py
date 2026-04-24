import pytest
from app.services.analytics import analytics_service
from app.schemas.analytics import TimelineStatsItem
from typing import List, Any

def test_deep_growth_rate():
    # Полное покрытие calculate_growth_rate
    assert analytics_service.calculate_growth_rate(100, 50) == 100.0
    assert analytics_service.calculate_growth_rate(50, 100) == -50.0
    assert analytics_service.calculate_growth_rate(100, 100) == 0.0
    assert analytics_service.calculate_growth_rate(100, 0) == 100.0
    assert analytics_service.calculate_growth_rate(0, 0) == 0.0

def test_deep_severity_index():
    # Полное покрытие calculate_severity_index
    assert analytics_service.calculate_severity_index(0, 0) == 0.0
    assert analytics_service.calculate_severity_index(10, 0) == 1.0
    assert analytics_service.calculate_severity_index(0, 10) == 0.0
    assert analytics_service.calculate_severity_index(5, 5) == 0.5

def test_deep_risks():
    # Социальный и транспортный
    assert analytics_service.calculate_social_risk(10, 100000) == 10.0
    assert analytics_service.calculate_social_risk(10, 0) == 0.0
    assert analytics_service.calculate_transport_risk(10, 1000) == 100.0
    assert analytics_service.calculate_transport_risk(10, 0) == 0.0

def test_deep_linear_regression():
    # Краевые случаи регрессии
    # Пустые данные
    p, s = analytics_service.linear_regression_prediction([])
    assert p == 0.0 and s == 0.0
    # Одна точка
    p, s = analytics_service.linear_regression_prediction([10])
    assert p == 10.0 and s == 0.0
    # Две точки (идеальная линия)
    p, s = analytics_service.linear_regression_prediction([10, 20])
    assert p == 30.0
    # Одинаковые значения
    p, s = analytics_service.linear_regression_prediction([10, 10, 10])
    assert p == 10.0 and s == 0.0

def test_deep_seasonality():
    class MockStat:
        def __init__(self, month, count, fatalities=0, injured=0):
            self.month = month
            self.count = count
            self.fatalities = fatalities
            self.injured = injured
            
    stats = [
        MockStat(1, 10), # Зима
        MockStat(4, 20), # Весна
        MockStat(7, 30), # Лето
        MockStat(10, 40) # Осень
    ]
    res = analytics_service.calculate_seasonality(stats)
    assert len(res) == 4
    # Среднее для Лета: 30 / 3 = 10.0
    assert any(r["season"] == "Лето" and r["average_accidents"] == 10.0 for r in res)

def test_deep_profile():
    class MockP:
        def __init__(self, age, experience):
            self.age = age
            self.experience = experience
            
    # Разные группы возраста и стажа
    parts = [
        MockP(20, 1), # 18-25, 0-2
        MockP(30, 4), # 26-45, 2-5
        MockP(50, 15), # 46-65, 10+
        MockP(70, 40), # 65+, 10+
        MockP(None, None) # Не указан
    ]
    res = analytics_service.calculate_participant_profile(parts, "Женский", 5)
    assert res["gender"] == "Женский"
    assert res["total_culprits"] == 5

def test_deep_safety_score():
    # Разные варианты населения
    assert analytics_service.calculate_safety_score(1, 1, 1, 1) > 0
    assert analytics_service.calculate_safety_score(0, 0, 0, 0) == 0.0
