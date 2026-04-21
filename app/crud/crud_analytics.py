from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.dtp import Accident, Participant
from app.models.dictionaries import Region, WeatherType

class CRUDAnalytics:
    async def get_monthly_stats(self, db: AsyncSession, region_code: Optional[str] = None) -> List[Any]:
        """Получить статистику по месяцам (ГГГГ-ММ, count, fatalities, injured)"""
        stmt = select(
            func.strftime('%Y-%m', Accident.date_dtp).label('month'),
            func.count(Accident.id).label('count'),
            func.sum(Accident.fatalities).label('fatalities'),
            func.sum(Accident.injured).label('injured')
        )
        if region_code:
            stmt = stmt.where(Accident.region_code == region_code)
        
        stmt = stmt.group_by('month').order_by(desc('month'))
        result = await db.execute(stmt)
        return result.all()

    async def get_yearly_stats(self, db: AsyncSession, region_code: Optional[str] = None) -> List[Any]:
        """Получить статистику по годам (ГГГГ, count, fatalities, injured)"""
        stmt = select(
            func.strftime('%Y', Accident.date_dtp).label('year'),
            func.count(Accident.id).label('count'),
            func.sum(Accident.fatalities).label('fatalities'),
            func.sum(Accident.injured).label('injured')
        )
        if region_code:
            stmt = stmt.where(Accident.region_code == region_code)
        
        stmt = stmt.group_by('year').order_by(desc('year'))
        result = await db.execute(stmt)
        return result.all()

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

crud_analytics = CRUDAnalytics()
