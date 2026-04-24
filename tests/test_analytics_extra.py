import pytest
from app.services.analytics import analytics_service

def test_extra_analytics_edge_cases():
    # Тест на расчет рисков с отрицательным населением (защита от дурака)
    assert analytics_service.calculate_social_risk(10, -100) == 0.0
    assert analytics_service.calculate_transport_risk(10, -50) == 0.0
    
    # Тест сезонности с некорректными номерами месяцев
    class BadStat:
        def __init__(self, month):
            self.month = month
            self.count = 10
            self.fatalities = 1
            self.injured = 1
            
    res = analytics_service.calculate_seasonality([BadStat(13), BadStat(-1), BadStat(0)])
    # Все должны попасть в категорию Зима (по умолчанию для 0/неизвестно в нашей логике) или быть проигнорированы
    # В текущей реализации 13/0/12 и тд мапятся через month % 12 или попадают в дефолт
    assert len(res) == 4

def test_profile_empty_results():
    # Если данных о виновниках нет вообще
    res = analytics_service.calculate_participant_profile([], "Мужской", 0)
    assert res["total_culprits"] == 0
    assert res["gender"] == "Неизвестно"

def test_safety_score_very_high_population():
    # Проверка устойчивости формулы при огромных числах
    score = analytics_service.calculate_safety_score(10, 100000000, 1, 1)
    assert score < 1.0 # Риск должен быть очень низким
