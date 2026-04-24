import asyncio
import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    # Позволяет запускать скрипт как `python scripts/init_db.py` и как `python -m scripts.init_db`.
    sys.path.insert(0, project_root)

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
