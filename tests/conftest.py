import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.db.session import Base, get_db
from app.main import app
from app.services import auth as auth_service
from app.crud import crud_auth
from app.core.config import settings

# Используем SQLite в памяти для тестов
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db(engine):
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture(autouse=True)
async def override_get_db(db):
    app.dependency_overrides[get_db] = lambda: db
    yield
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def valid_api_key(db: AsyncSession):
    raw_key = "test_student_secure_access_key_999"
    key_hash = auth_service.hash_key(raw_key)
    prefix = auth_service.get_key_prefix(raw_key)
    
    await crud_auth.create_key(
        db,
        owner_name="Test Runner",
        key_hash=key_hash,
        prefix=prefix
    )
    await db.commit()
    return raw_key

@pytest.fixture
def auth_headers(valid_api_key):
    return {"X-API-KEY": valid_api_key}

@pytest.fixture
def master_headers():
    return {"X-MASTER-KEY": settings.X_API_KEY.get_secret_value()}
