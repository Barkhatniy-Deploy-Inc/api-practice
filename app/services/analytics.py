from typing import List, Tuple, Optional, Dict, Any
import math

class AnalyticsService:
    @staticmethod
    def calculate_growth_rate(current: int, previous: int) -> float:
        """Расчет темпа роста в %"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 2)

    @staticmethod
    def calculate_severity_index(fatalities: int, injured: int) -> float:
        """Расчет индекса тяжести последствий (доля погибших)"""
        total = fatalities + injured
        if total == 0:
            return 0.0
        return round(fatalities / total, 4)

    @staticmethod
    def calculate_social_risk(fatalities: int, population: int) -> float:
        """Расчет социального риска (погибших на 100 тыс. населения)"""
        if population <= 0:
            return 0.0
        return round((fatalities / population) * 100000, 4)

    @staticmethod
    def calculate_transport_risk(fatalities: int, vehicles: int) -> float:
        """Расчет транспортного риска (погибших на 10 тыс. ТС)"""
        if vehicles <= 0:
            return 0.0
        return round((fatalities / vehicles) * 10000, 4)

    def calculate_safety_score(self, accidents: int, population: int, fatalities: int, injured: int) -> float:
        """Интегральный показатель безопасности региона"""
        if population <= 0:
            return 0.0
            
        accidents_per_100k = (accidents / population * 100000)
        severity = self.calculate_severity_index(fatalities, injured)
        
        # Примерная формула: 40% вес кол-ва ДТП, 60% вес тяжести
        score = (accidents_per_100k * 0.4) + (severity * 0.6)
        return round(score, 4)

    def linear_regression_prediction(self, data: List[int]) -> Tuple[float, float]:
        """
        Прогноз на следующий период методом линейной регрессии (МНК)
        Возвращает (прогноз, стандартное отклонение)
        """
        n = len(data)
        if n < 2:
            return (float(data[0]), 0.0) if n == 1 else (0.0, 0.0)

        x = list(range(n))
        y = data

        sum_x = sum(x)
        sum_y = sum(y)
        sum_xx = sum(i*i for i in x)
        sum_xy = sum(i*j for i, j in zip(x, y))

        denominator = (n * sum_xx - sum_x**2)
        if denominator == 0:
            return (float(sum_y / n), 0.0)

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n

        prediction = slope * n + intercept
        
        # Расчет стандартного отклонения (упрощенно)
        errors = [(slope * i + intercept - val)**2 for i, val in enumerate(y)]
        std_dev = math.sqrt(sum(errors) / n)

        return round(max(0, prediction), 2), round(std_dev, 2)

    def calculate_seasonality(self, stats: List[Any]) -> List[Dict[str, Any]]:
        """Расчет сезонности ДТП"""
        seasons = {
            "Зима": [12, 1, 2],
            "Весна": [3, 4, 5],
            "Лето": [6, 7, 8],
            "Осень": [9, 10, 11]
        }
        
        res = []
        for season_name, months in seasons.items():
            season_stats = [s for s in stats if s.month in months]
            count = sum(s.count for s in season_stats) if season_stats else 0
            res.append({
                "season": season_name,
                "count": count,
                "average_accidents": round(count / 3, 2)
            })
        return res

    def map_experience_categories(self, stats: List[Any]) -> Dict[str, Any]:
        """Группировка по стажу вождения"""
        categories = {
            "0-2 года": {"count": 0, "fatalities": 0, "injured": 0},
            "2-5 лет": {"count": 0, "fatalities": 0, "injured": 0},
            "5-10 лет": {"count": 0, "fatalities": 0, "injured": 0},
            "10+ лет": {"count": 0, "fatalities": 0, "injured": 0}
        }
        
        for s in stats:
            cat = s.experience_group or "10+ лет"
            if cat not in categories: continue
            categories[cat]["count"] += getattr(s, 'count', 0)
            categories[cat]["fatalities"] += getattr(s, 'fatalities', 0) or 0
            categories[cat]["injured"] += getattr(s, 'injured', 0) or 0
            
        return categories

    def calculate_participant_profile(self, participants: List[Any], default_gender: str = "Неизвестно", total_count: int = 0) -> Dict[str, Any]:
        """Определение типичного профиля виновника (мода)"""
        if not participants and total_count == 0:
            return {
                "gender": "Неизвестно",
                "age_group": "Неизвестно",
                "experience_group": "Неизвестно",
                "total_culprits": 0
            }
            
        ages = {}
        experiences = {}
        
        for p in participants:
            # Возрастная группа
            age = p.age
            if age is None:
                age_cat = "Не указан"
            elif age < 18:
                age_cat = "До 18 лет"
            elif age <= 25:
                age_cat = "18-25 лет"
            elif age <= 45:
                age_cat = "26-45 лет"
            elif age <= 65:
                age_cat = "46-65 лет"
            else:
                age_cat = "65+ лет"
            ages[age_cat] = ages.get(age_cat, 0) + 1
            
            # Группа стажа
            exp = p.experience
            if exp is None:
                exp_cat = "Не указан"
            elif exp <= 2:
                exp_cat = "0-2 года"
            elif exp <= 5:
                exp_cat = "2-5 лет"
            elif exp <= 10:
                exp_cat = "5-10 лет"
            else:
                exp_cat = "10+ лет"
            experiences[exp_cat] = experiences.get(exp_cat, 0) + 1
            
        def get_mode(d: Dict[str, int]) -> str:
            if not d: return "Не указан"
            return max(d, key=d.get)
            
        return {
            "gender": default_gender if total_count > 0 else "Неизвестно",
            "age_group": get_mode(ages),
            "experience_group": get_mode(experiences),
            "total_culprits": total_count
        }

    def calculate_delta(self, current: Dict[str, int], previous: Dict[str, int]) -> Dict[str, float]:
        """Расчет разницы в процентах между двумя наборами статистики"""
        deltas = {}
        for key in ["total_accidents", "total_fatalities", "total_injured"]:
            cur_val = current.get(key, 0)
            prev_val = previous.get(key, 0)
            deltas[key] = self.calculate_growth_rate(cur_val, prev_val)
        return deltas

    @staticmethod
    def get_next_period(last_month_str: str) -> str:
        """Определение следующего месяца для прогноза (формат YYYY-MM)"""
        try:
            year, month = map(int, last_month_str.split('-'))
            if month == 12:
                return f"{year + 1}-01"
            return f"{year}-{month + 1:02d}"
        except:
            return "Будущий период"

    def cluster_coordinates(self, coords: List[Tuple[float, float]]) -> List[Dict[str, Any]]:
        """Кластеризация координат для тепловой карты (округление до 3 знаков)"""
        clusters = {}
        for lat, lon in coords:
            if lat is None or lon is None: continue
            # Округляем до ~110 метров точности
            key = (round(lat, 3), round(lon, 3))
            clusters[key] = clusters.get(key, 0) + 1
            
        return [
            {"lat": k[0], "lon": k[1], "intensity": v}
            for k, v in clusters.items()
        ]

analytics_service = AnalyticsService()
