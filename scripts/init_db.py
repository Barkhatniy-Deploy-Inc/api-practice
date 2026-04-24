import asyncio
from app.db.session import engine, Base
# Импортируем все модели, чтобы Base их увидел
from app.models.dtp import Accident, Vehicle, Participant
from app.models.dictionaries import Region, District, WeatherType, RoadCondition, AccidentType, CarType, CarBrand, CarModel
from app.models.auth import APIKey

async def init_db():
    print("🚀 Начинаю инициализацию базы данных Зебра-стат...")
    async with engine.begin() as conn:
        # Создаем все таблицы
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Все таблицы успешно созданы.")

if __name__ == "__main__":
    asyncio.run(init_db())
