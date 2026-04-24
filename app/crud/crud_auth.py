from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.auth import APIKey

async def create_key(
    db: AsyncSession, 
    *, 
    owner_name: str, 
    key_hash: str, 
    prefix: str
) -> APIKey:
    """
    Создает новый API ключ в базе данных.
    """
    db_obj = APIKey(
        owner_name=owner_name,
        key_hash=key_hash,
        prefix=prefix,
        is_active=True
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_key_by_hash(db: AsyncSession, key_hash: str) -> Optional[APIKey]:
    """
    Ищет активный API ключ по его хешу.
    """
    result = await db.execute(
        select(APIKey).where(APIKey.key_hash == key_hash, APIKey.is_active == True)
    )
    return result.scalars().first()

async def get_all_keys(db: AsyncSession) -> List[APIKey]:
    """
    Возвращает список всех API ключей (для админки).
    """
    result = await db.execute(select(APIKey))
    return result.scalars().all()
