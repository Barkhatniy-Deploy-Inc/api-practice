from typing import List, Tuple, Optional, Dict, Any
import math

class AnalyticsService:
    @staticmethod
    def calculate_growth_rate(current: int, previous: int) -> float:
        """Расчет темпа роста в %"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100.0

    @staticmethod
    def calculate_severity_index(fatalities: int, injured: int) -> float:
        """Расчет индекса тяжести: погибшие / (погибшие + раненые)"""
        total = fatalities + injured
        if total == 0:
            return 0.0
        return fatalities / total

    @staticmethod
    def calculate_social_risk(fatalities: int, population: int) -> float:
        """Социальный риск: (погибшие / население) * 100,000"""
        if population == 0:
            return 0.0
        return (fatalities / population) * 100000

    @staticmethod
    def calculate_transport_risk(fatalities: int, vehicles: int) -> float:
        """Транспортный риск: (погибшие / ТС) * 10,000"""
        if vehicles == 0:
            return 0.0
        return (fatalities / vehicles) * 10000

    @staticmethod
    def linear_regression_prediction(data: List[int]) -> Tuple[float, float]:
        """
        Линейная регрессия методом наименьших квадратов (МНК).
        Возвращает (прогноз на следующий шаг, доверительный интервал).
        y = ax + b
        """
        n = len(data)
        if n < 2:
            return float(data[0]) if n == 1 else 0.0, 0.0
        
        x = list(range(n))
        y = data
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xx = sum(xi * xi for xi in x)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        
        # a = (n*sum_xy - sum_x*sum_y) / (n*sum_xx - sum_x^2)
        denominator = (n * sum_xx - sum_x**2)
        if denominator == 0:
            return float(sum_y / n), 0.0
            
        a = (n * sum_xy - sum_x * sum_y) / denominator
        b = (sum_y - a * sum_x) / n
        
        # Прогноз на следующий шаг (x = n)
        prediction = a * n + b
        
        # Доверительный интервал (несмещенная оценка стандартного отклонения остатков)
        # Используем n - 2 степени свободы для парной линейной регрессии
        residuals_sum = sum((yi - (a * xi + b))**2 for xi, yi in zip(x, y))
        
        if n > 2:
            std_dev = math.sqrt(residuals_sum / (n - 2))
        else:
            # Если данных слишком мало для несмещенной оценки, используем смещенную
            std_dev = math.sqrt(residuals_sum / n) if n > 0 else 0.0
        
        return max(0.0, prediction), std_dev

    def get_next_period(self, last_period: str) -> str:
        """Определение следующего периода (месяца) на основе строки формата YYYY-MM"""
        try:
            year, month = map(int, last_period.split('-'))
            if month == 12:
                return f"{year + 1}-01"
            else:
                return f"{year}-{month + 1:02d}"
        except (ValueError, AttributeError):
            return "unknown"

    def map_experience_categories(self, stats: List[Any]) -> Dict[str, Dict[str, int]]:
        """Группировка статистики по категориям стажа вождения"""
        categories = {
            "0-2 года": {"count": 0, "fatalities": 0, "injured": 0},
            "2-5 лет": {"count": 0, "fatalities": 0, "injured": 0},
            "5-10 лет": {"count": 0, "fatalities": 0, "injured": 0},
            "10+ лет": {"count": 0, "fatalities": 0, "injured": 0}
        }
        
        for s in stats:
            exp = getattr(s, 'experience', None)
            if exp is None:
                continue
            
            if exp <= 2:
                cat = "0-2 года"
            elif exp <= 5:
                cat = "2-5 лет"
            elif exp <= 10:
                cat = "5-10 лет"
            else:
                cat = "10+ лет"
            
            categories[cat]["count"] += getattr(s, 'count', 0)
            categories[cat]["fatalities"] += getattr(s, 'fatalities', 0) or 0
            categories[cat]["injured"] += getattr(s, 'injured', 0) or 0
            
        return categories

analytics_service = AnalyticsService()
