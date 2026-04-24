from typing import List
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.crud import crud_auth
from app.services import auth as auth_service
from app.schemas.auth import APIKeyCreate, APIKeyGenerated, APIKeyResponse
from app.models.auth import APIKey

router = APIRouter()

async def verify_master_key(x_master_key: str = Header(...)):
    """
    Проверка Master-Key (X-MASTER-KEY).
    Сравнивается со значением settings.X_API_KEY.
    """
    if x_master_key != settings.X_API_KEY.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный Master-Key"
        )
    return x_master_key

async def get_current_api_key(
    x_api_key: str = Header(...),
    db: AsyncSession = Depends(get_db)
) -> APIKey:
    """
    Проверка API-ключа и получение информации о владельце.
    """
    key_hash = auth_service.hash_key(x_api_key)
    db_key = await crud_auth.get_key_by_hash(db, key_hash=key_hash)
    
    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или неактивный API-ключ"
        )
    return db_key

@router.post("/keys", response_model=APIKeyGenerated, dependencies=[Depends(verify_master_key)])
async def create_new_api_key(
    key_in: APIKeyCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Создание нового API-ключа. Требует X-MASTER-KEY.
    """
    raw_key = auth_service.generate_new_key()
    key_hash = auth_service.hash_key(raw_key)
    prefix = auth_service.get_key_prefix(raw_key)
    
    db_key = await crud_auth.create_key(
        db,
        owner_name=key_in.owner_name,
        key_hash=key_hash,
        prefix=prefix
    )
    
    return APIKeyGenerated(
        id=db_key.id,
        owner_name=db_key.owner_name,
        prefix=db_key.prefix,
        is_active=db_key.is_active,
        created_at=db_key.created_at,
        access_key=raw_key
    )

@router.get("/keys", response_model=List[APIKeyResponse], dependencies=[Depends(verify_master_key)])
async def list_api_keys(
    db: AsyncSession = Depends(get_db)
):
    """
    Список всех API-ключей. Требует X-MASTER-KEY.
    """
    keys = await crud_auth.get_all_keys(db)
    return keys

@router.get("/me", response_model=APIKeyResponse)
async def get_my_info(
    current_key: APIKey = Depends(get_current_api_key)
):
    """
    Информация о текущем владельце API-ключа.
    """
    return current_key
