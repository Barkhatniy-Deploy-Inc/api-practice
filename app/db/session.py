from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Создаем асинхронный движок для SQLite
engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=settings.DEBUG_MODE,
    future=True
)

# Создаем фабрику сессий
SessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Базовый класс для моделей
Base = declarative_base()

# Dependency для получения сессии в эндпоинтах
async def get_db():
    async with SessionLocal() as session:
        yield session
