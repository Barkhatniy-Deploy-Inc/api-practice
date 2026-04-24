from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, extract
from app.models.dtp import Accident, Participant
from app.models.dictionaries import Region, WeatherType

class CRUDAnalytics:
    async def get_monthly_stats(self, db: AsyncSession, region_code: Optional[str] = None) -> List[Any]:
        """Получить статистику по месяцам (ГГГГ-ММ, count, fatalities, injured)"""
        stmt = select(
            extract('year', Accident.date_dtp).label('year'),
            extract('month', Accident.date_dtp).label('month'),
            func.count(Accident.id).label('count'),
            func.sum(Accident.fatalities).label('fatalities'),
            func.sum(Accident.injured).label('injured')
        )
        if region_code:
            stmt = stmt.where(Accident.region_code == region_code)
        
        stmt = stmt.group_by('year', 'month').order_by(desc('year'), desc('month'))
        result = await db.execute(stmt)
        rows = result.all()
        
        # Формируем результат в виде объектов с полем period для совместимости со схемами
        return [
            type('StatRow', (), {
                'period': f"{int(r.year)}-{int(r.month):02d}",
                'month': f"{int(r.year)}-{int(r.month):02d}", # Для совместимости с логикой прогноза
                'count': r.count,
                'fatalities': r.fatalities,
                'injured': r.injured
            })()
            for r in rows
        ]

    async def get_yearly_stats(self, db: AsyncSession, region_code: Optional[str] = None) -> List[Any]:
        """Получить статистику по годам (ГГГГ, count, fatalities, injured)"""
        stmt = select(
            extract('year', Accident.date_dtp).label('year'),
            func.count(Accident.id).label('count'),
            func.sum(Accident.fatalities).label('fatalities'),
            func.sum(Accident.injured).label('injured')
        )
        if region_code:
            stmt = stmt.where(Accident.region_code == region_code)
        
        stmt = stmt.group_by('year').order_by(desc('year'))
        result = await db.execute(stmt)
        rows = result.all()
        
        return [
            type('StatRow', (), {
                'period': str(int(r.year)),
                'year': str(int(r.year)), # Для обратной совместимости
                'count': r.count,
                'fatalities': r.fatalities,
                'injured': r.injured
            })()
            for r in rows
        ]

    async def get_region_risk_data(self, db: AsyncSession, region_code: str) -> Any:
        """Получить данные для расчета рисков региона (fatalities, population, vehicles)"""
        stmt = select(
            func.sum(Accident.fatalities).label('fatalities'),
            Region.population,
            Region.vehicles
        ).join(Region, Accident.region_code == Region.code).where(Region.code == region_code).group_by(Region.code, Region.population, Region.vehicles)
        
        result = await db.execute(stmt)
        return result.first()

    async def get_weather_correlation(self, db: AsyncSession, region_code: Optional[str] = None) -> List[Any]:
        """Статистика по погоде (weather_name, count, fatalities, injured)"""
        stmt = select(
            WeatherType.name,
            func.count(Accident.id).label('count'),
            func.sum(Accident.fatalities).label('fatalities'),
            func.sum(Accident.injured).label('injured')
        ).join(WeatherType, Accident.weather_id == WeatherType.id)
        
        if region_code:
            stmt = stmt.where(Accident.region_code == region_code)
            
        stmt = stmt.group_by(WeatherType.name)
        result = await db.execute(stmt)
        return result.all()

    async def get_experience_correlation(self, db: AsyncSession, region_code: Optional[str] = None) -> List[Any]:
        """Статистика по стажу (experience, count, fatalities, injured)"""
        stmt = select(
            Participant.experience,
            func.count(Accident.id).label('count'),
            func.sum(Accident.fatalities).label('fatalities'),
            func.sum(Accident.injured).label('injured')
        ).join(Accident, Participant.accident_id == Accident.id).where(Participant.is_culprit == 1)
        
        if region_code:
            stmt = stmt.where(Accident.region_code == region_code)
            
        stmt = stmt.group_by(Participant.experience)
        result = await db.execute(stmt)
        return result.all()

    async def get_lighting_correlation(self, db: AsyncSession, region_code: Optional[str] = None) -> List[Any]:
        """Статистика по освещению (lighting, count, fatalities, injured)"""
        stmt = select(
            Accident.lighting,
            func.count(Accident.id).label('count'),
            func.sum(Accident.fatalities).label('fatalities'),
            func.sum(Accident.injured).label('injured')
        )
        
        if region_code:
            stmt = stmt.where(Accident.region_code == region_code)
            
        stmt = stmt.group_by(Accident.lighting)
        result = await db.execute(stmt)
        return result.all()

    async def get_summary_stats(
        self, db: AsyncSession, date_from: Optional[Any] = None, date_to: Optional[Any] = None
    ) -> Any:
        """Получить сводную статистику за период"""
        stmt = select(
            func.count(Accident.id).label('total_accidents'),
            func.sum(Accident.fatalities).label('total_fatalities'),
            func.sum(Accident.injured).label('total_injured')
        )
        if date_from:
            stmt = stmt.where(Accident.date_dtp >= date_from)
        if date_to:
            stmt = stmt.where(Accident.date_dtp <= date_to)
        
        result = await db.execute(stmt)
        return result.first()

    async def get_regional_stats(
        self, db: AsyncSession, sort_by: str = "accidents", order: str = "desc"
    ) -> List[Any]:
        """Получить статистику по регионам"""
        stmt = select(
            Region.name,
            Region.code,
            func.count(Accident.id).label('accidents'),
            func.sum(Accident.fatalities).label('fatalities')
        ).join(Accident, Region.code == Accident.region_code).group_by(Region.name, Region.code)

        if sort_by == "fatalities":
            sort_col = func.sum(Accident.fatalities)
        else:
            sort_col = func.count(Accident.id)

        if order == "asc":
            stmt = stmt.order_by(sort_col)
        else:
            stmt = stmt.order_by(desc(sort_col))

        result = await db.execute(stmt)
        return result.all()

    async def get_timeline_stats(
        self, db: AsyncSession, interval: str = "month"
    ) -> List[Any]:
        """Получить временную шкалу статистики"""
        # Форматы для SQLite strftime
        formats = {
            "day": "%Y-%m-%d",
            "month": "%Y-%m",
            "year": "%Y"
        }
        fmt = formats.get(interval, "%Y-%m")
        
        # Используем func.strftime для SQLite
        period_col = func.strftime(fmt, Accident.date_dtp).label('period')
        
        stmt = select(
            period_col,
            func.count(Accident.id).label('accidents'),
            func.sum(Accident.fatalities).label('fatalities'),
            func.sum(Accident.injured).label('injured')
        ).group_by('period').order_by('period')
        
        result = await db.execute(stmt)
        return result.all()

    async def get_seasonality_data(self, db: AsyncSession) -> List[Any]:
        """Получить количество ДТП по месяцам для расчета сезонности"""
        stmt = select(
            extract('month', Accident.date_dtp).label('month'),
            func.count(Accident.id).label('count')
        ).group_by('month')
        
        result = await db.execute(stmt)
        return result.all()

    async def get_danger_zones(self, db: AsyncSession, limit: int = 10) -> List[Any]:
        """Получить топ опасных участков (улица + населенный пункт)"""
        stmt = select(
            Accident.road_name,
            Accident.locality,
            func.count(Accident.id).label('accidents_count')
        ).group_by(Accident.road_name, Accident.locality).order_by(desc('accidents_count')).limit(limit)
        
        result = await db.execute(stmt)
        return result.all()

    async def get_safe_regions_data(self, db: AsyncSession) -> List[Any]:
        """Получить данные для расчета рейтинга безопасности регионов"""
        stmt = select(
            Region.name,
            Region.code,
            Region.population,
            func.count(Accident.id).label('accidents'),
            func.sum(Accident.fatalities).label('fatalities'),
            func.sum(Accident.injured).label('injured')
        ).join(Accident, Region.code == Accident.region_code).group_by(Region.name, Region.code, Region.population)
        
        result = await db.execute(stmt)
        return result.all()

    async def get_participant_profile_data(self, db: AsyncSession) -> Dict[str, Any]:
        """Получить статистический профиль виновников (расчет моды на стороне БД)"""
        
        # 1. Самый частый пол
        gender_stmt = select(Participant.gender).where(Participant.is_culprit == 1).group_by(Participant.gender).order_by(desc(func.count())).limit(1)
        
        # 2. Общее количество
        count_stmt = select(func.count(Participant.id)).where(Participant.is_culprit == 1)
        
        # 3. Возрастные группы и стаж (выбираем сырые данные для сложной логики групп, 
        # но только необходимые колонки, чтобы не грузить лишнее)
        # Примечание: Для идеальной скорости здесь тоже лучше использовать CASE WHEN в SQL
        data_stmt = select(Participant.age, Participant.experience).where(Participant.is_culprit == 1)
        
        gender_res = await db.execute(gender_stmt)
        count_res = await db.execute(count_stmt)
        data_res = await db.execute(data_stmt)
        
        return {
            "gender": gender_res.scalar() or "Не указан",
            "total_culprits": count_res.scalar() or 0,
            "raw_data": data_res.all()
        }

    async def get_multi_region_stats(self, db: AsyncSession, region_codes: List[str]) -> List[Any]:
        """Получить статистику сразу для списка регионов"""
        stmt = select(
            Region.name,
            Region.code,
            Region.population,
            func.count(Accident.id).label("accidents"),
            func.sum(Accident.fatalities).label("fatalities"),
            func.sum(Accident.injured).label("injured")
        ).join(Accident, Region.code == Accident.region_code).where(Region.code.in_(region_codes)).group_by(Region.name, Region.code, Region.population)
        
        result = await db.execute(stmt)
        return result.all()

    async def get_children_trauma_stats(self, db: AsyncSession, region_code: Optional[str] = None) -> Dict[str, int]:
        """Статистика детского травматизма"""
        base_stmt = select(func.count(Accident.id))
        if region_code:
            base_stmt = base_stmt.where(Accident.region_code == region_code)
            
        total_stmt = base_stmt
        children_stmt = base_stmt.where(Accident.has_children == 1)
        
        total_res = await db.execute(total_stmt)
        children_res = await db.execute(children_stmt)
        
        return {
            "total": total_res.scalar() or 0,
            "children": children_res.scalar() or 0
        }

    async def get_all_coordinates(self, db: AsyncSession, region_code: Optional[str] = None) -> List[Any]:
        """Получить все координаты для тепловой карты"""
        stmt = select(Accident.coord_lat, Accident.coord_lon)
        if region_code:
            stmt = stmt.where(Accident.region_code == region_code)
        
        result = await db.execute(stmt)
        return result.all()

crud_analytics = CRUDAnalytics()
