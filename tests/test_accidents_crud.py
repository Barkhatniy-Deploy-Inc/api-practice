import pytest
from app.crud.crud_accidents import get_accidents, get_accident_by_id
from app.models.dtp import Accident
from datetime import date, time

@pytest.mark.asyncio
async def test_get_accidents_empty(db):
    accidents = await get_accidents(db)
    assert accidents == []

@pytest.mark.asyncio
async def test_get_accident_by_id_not_found(db):
    accident = await get_accident_by_id(db, 999)
    assert accident is None

@pytest.mark.asyncio
async def test_create_and_get_accident(db):
    # Используем объект time вместо строки
    new_accident = Accident(
        id=100,
        empt_number="TEST-001",
        region_code="1114",
        date_dtp=date(2026, 4, 20),
        time_dtp=time(12, 0, 0),
        locality="Тестовый город",
        road_name="Тестовое шоссе",
        coord_lat=55.0,
        coord_lon=37.0
    )
    db.add(new_accident)
    await db.commit()
    
    accidents = await get_accidents(db)
    assert len(accidents) > 0
    
    detail = await get_accident_by_id(db, 100)
    assert detail is not None
    assert detail.locality == "Тестовый город"
