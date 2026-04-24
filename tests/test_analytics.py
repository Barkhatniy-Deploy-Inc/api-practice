import pytest
from app.services.analytics import analytics_service

def test_calculate_growth_rate():
    assert analytics_service.calculate_growth_rate(120, 100) == 20.0
    assert analytics_service.calculate_growth_rate(80, 100) == -20.0
    assert analytics_service.calculate_growth_rate(100, 0) == 100.0
    assert analytics_service.calculate_growth_rate(0, 0) == 0.0

def test_calculate_severity_index():
    # fatalities / (fatalities + injured)
    assert analytics_service.calculate_severity_index(10, 90) == 0.1
    assert analytics_service.calculate_severity_index(0, 100) == 0.0
    assert analytics_service.calculate_severity_index(100, 0) == 1.0
    assert analytics_service.calculate_severity_index(0, 0) == 0.0

def test_calculate_social_risk():
    # (fatalities / population) * 100,000
    assert analytics_service.calculate_social_risk(10, 100000) == 10.0
    assert analytics_service.calculate_social_risk(0, 100000) == 0.0
    assert analytics_service.calculate_social_risk(10, 0) == 0.0

def test_calculate_transport_risk():
    # (fatalities / vehicles) * 10,000
    assert analytics_service.calculate_transport_risk(10, 10000) == 10.0
    assert analytics_service.calculate_transport_risk(0, 10000) == 0.0
    assert analytics_service.calculate_transport_risk(10, 0) == 0.0

def test_linear_regression_prediction():
    # y = x (a=1, b=0)
    data = [0, 1, 2, 3, 4]
    prediction, std_dev = analytics_service.linear_regression_prediction(data)
    # x = 5 -> y = 5
    assert prediction == 5.0
    assert std_dev == 0.0

    # y = 2x + 10
    data = [10, 12, 14, 16, 18]
    prediction, std_dev = analytics_service.linear_regression_prediction(data)
    # x = 5 -> y = 2*5 + 10 = 20
    assert prediction == 20.0
    assert std_dev == 0.0

    # Случайные данные
    data = [10, 15, 12, 18, 20]
    prediction, std_dev = analytics_service.linear_regression_prediction(data)
    assert prediction > 0
    assert std_dev > 0
