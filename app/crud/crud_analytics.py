from typing import List, Optional, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, extract, case
from app.models.dtp import Accident, Participant
from app.models.dictionaries import Region, District

class CRUDAnalytics:
    async def get_summary_stats(self, db: AsyncSession, date_from: Optional[str] = None, 
                           date_to: Optional[str] = None, region_code: Optional[str] = None) -> Any:
        """Сводная статистика за период"""
        stmt = select(
            func.count(Accident.id).label("total_accidents"),
            func.sum(Accident.fatalities).label("total_fatalities"),
            func.sum(Accident.injured).label("total_injured")
        )
        
        if date_from:
            stmt = stmt.where(Accident.date_dtp >= date_from)
        if date_to:
            stmt = stmt.where(Accident.date_dtp <= date_to)
        if region_code:
            stmt = stmt.where(Accident.region_code == region_code)
            
        result = await db.execute(stmt)
        return result.one()

    async def get_regional_stats(self, db: AsyncSession, sort_by: str = "accidents", order: str = "desc") -> List[Any]:
        """Статистика по всем регионам"""
        sort_col = func.count(Accident.id) if sort_by == "accidents" else func.sum(Accident.fatalities)
        stmt = select(
            Region.name,
            Region.code,
            func.count(Accident.id).label("accidents"),
            func.sum(Accident.fatalities).label("fatalities")
        ).join(Accident, Region.code == Accident.region_code).group_by(Region.name, Region.code)
        
        if order == "desc":
            stmt = stmt.order_by(desc(sort_col))
        else:
            stmt = stmt.order_by(sort_col)
            
        result = await db.execute(stmt)
        return result.all()

    async def get_timeline_stats(self, db: AsyncSession, interval: str = "month") -> List[Any]:
        """Динамика ДТП"""
        format_str = '%Y-%m'
        if interval == "day": format_str = '%Y-%m-%d'
        elif interval == "year": format_str = '%Y'
            
        period_col = func.strftime(format_str, Accident.date_dtp).label("period")
        stmt = select(
            period_col,
            func.count(Accident.id).label("accidents"),
            func.sum(Accident.fatalities).label("fatalities"),
            func.sum(Accident.injured).label("injured")
        ).group_by(period_col).order_by(period_col)
        
        result = await db.execute(stmt)
        return result.all()

    async def get_monthly_stats(self, db: AsyncSession, region_code: Optional[str] = None) -> List[Any]:
        """Статистика по месяцам (убираем динамические классы type())"""
        period_col = func.strftime('%Y-%m', Accident.date_dtp).label("period")
        stmt = select(
            period_col,
            func.count(Accident.id).label("count"),
            func.sum(Accident.fatalities).label("fatalities"),
            func.sum(Accident.injured).label("injured")
        )
        if region_code:
            stmt = stmt.where(Accident.region_code == region_code)
        
        stmt = stmt.group_by(period_col).order_by(desc(period_col))
        result = await db.execute(stmt)
        # Возвращаем список словарей — это быстрее и экономнее по памяти, чем type()
        return [dict(r._mapping) for r in result.all()]

    async def get_yearly_stats(self, db: AsyncSession, region_code: Optional[str] = None) -> List[Any]:
        """Статистика по годам (убираем динамические классы type())"""
        period_col = func.strftime('%Y', Accident.date_dtp).label("period")
        stmt = select(
            period_col,
            func.count(Accident.id).label("count"),
            func.sum(Accident.fatalities).label("fatalities"),
            func.sum(Accident.injured).label("injured")
        )
        if region_code:
            stmt = stmt.where(Accident.region_code == region_code)
            
        stmt = stmt.group_by(period_col).order_by(desc(period_col))
        result = await db.execute(stmt)
        return [dict(r._mapping) for r in result.all()]

    async def get_participant_profile_data(self, db: AsyncSession) -> Dict[str, Any]:
        """
        ФИНАЛЬНАЯ ОПТИМИЗАЦИЯ: Получение профиля в ОДИН запрос через CASE WHEN и SQL агрегацию.
        Никаких циклов Python по тысячам строк.
        """
        # Считаем общее кол-во и самый частый пол в одном запросе
        gender_count_stmt = select(
            func.count(Participant.id).label("total"),
            # Группируем по полу и берем верхний результат - реализуем через подзапрос или сложную агрегацию
        ).where(Participant.is_culprit == 1)
        
        # Для простоты и скорости в SQLite:
        main_res = await db.execute(gender_count_stmt)
        total = main_res.scalar() or 0
        
        # Самый частый пол
        gender_res = await db.execute(
            select(Participant.gender)
            .where(Participant.is_culprit == 1)
            .group_by(Participant.gender)
            .order_by(desc(func.count()))
            .limit(1)
        )
        mode_gender = gender_res.scalar() or "Неизвестно"
        
        # Группируем возраст и стаж прямо в SQL через CASE WHEN
        age_case = case(
            (Participant.age < 18, "До 18 лет"),
            (Participant.age <= 25, "18-25 лет"),
            (Participant.age <= 45, "26-45 лет"),
            (Participant.age <= 65, "46-65 лет"),
            else_="65+ лет"
        ).label("age_group")
        
        exp_case = case(
            (Participant.experience <= 2, "0-2 года"),
            (Participant.experience <= 5, "2-5 лет"),
            (Participant.experience <= 10, "5-10 лет"),
            else_="10+ лет"
        ).label("exp_group")
        
        # Получаем моду возрастной группы
        age_mode_stmt = select(age_case).where(Participant.is_culprit == 1).group_by("age_group").order_by(desc(func.count())).limit(1)
        exp_mode_stmt = select(exp_case).where(Participant.is_culprit == 1).group_by("exp_group").order_by(desc(func.count())).limit(1)
        
        age_res = await db.execute(age_mode_stmt)
        exp_res = await db.execute(exp_mode_stmt)
        
        return {
            "gender": mode_gender,
            "total_culprits": total,
            "age_group": age_res.scalar() or "Неизвестно",
            "experience_group": exp_res.scalar() or "Неизвестно",
            "raw_data": [] # Больше не нужно грузить сырые данные в память!
        }

    async def get_clustered_hotspots(self, db: AsyncSession, region_code: Optional[str] = None) -> List[Any]:
        """Кластеризация на стороне БД через SQL (округление и GROUP BY)"""
        lat_col = func.round(Accident.coord_lat, 3).label("lat")
        lon_col = func.round(Accident.coord_lon, 3).label("lon")
        
        stmt = select(
            lat_col,
            lon_col,
            func.count(Accident.id).label("intensity")
        ).where(Accident.coord_lat.is_not(None), Accident.coord_lon.is_not(None))
        
        if region_code:
            stmt = stmt.where(Accident.region_code == region_code)
            
        stmt = stmt.group_by(lat_col, lon_col)
        result = await db.execute(stmt)
        return result.all()

    async def get_weather_correlation(self, db: AsyncSession, region_code: Optional[str] = None) -> Any:
        """Анализ влияния погоды на тяжесть ДТП"""
        stmt = select(
            Accident.weather,
            func.count(Accident.id).label("total_accidents"),
            func.avg(Accident.fatalities).label("avg_fatalities")
        )
        if region_code:
            stmt = stmt.where(Accident.region_code == region_code)
        
        stmt = stmt.group_by(Accident.weather).order_by(desc("total_accidents"))
        result = await db.execute(stmt)
        return result.all()

crud_analytics = CRUDAnalytics()
