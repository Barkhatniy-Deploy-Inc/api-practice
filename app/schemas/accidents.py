import datetime
from typing import List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

class ParticipantSchema(BaseModel):
    """Схема участника ДТП"""
    id: int
    role: str
    gender: Optional[str] = None
    age: Optional[int] = None
    health_status: Optional[str] = None
    experience: Optional[int] = None
    is_drunk: bool = False
    is_culprit: bool = False
    model_config = ConfigDict(from_attributes=True)

class VehicleSchema(BaseModel):
    """Схема транспортного средства"""
    id: int
    type: Optional[str] = Field(None, alias="car_type_name")
    brand: Optional[str] = Field(None, alias="car_brand")
    model: Optional[str] = Field(None, alias="car_model_name")
    year: Optional[int] = Field(None, alias="year_release")
    is_defective: bool = False
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class MainInfoSchema(BaseModel):
    """Вложенная схема основной информации ДТП"""
    coords: Tuple[Optional[float], Optional[float]]
    weather: Optional[str] = None
    road_condition: Optional[str] = None
    locality: Optional[str] = None
    road_name: Optional[str] = None
    road_km: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class AccidentShortSchema(BaseModel):
    """Краткая карточка ДТП для списков"""
    id: int
    empt_number: str
    date_dtp: datetime.date = Field(..., alias="date")
    time_dtp: datetime.time = Field(..., alias="time")
    region_code: str
    fatalities: int
    injured: int
    address: Optional[str] = Field(None, alias="road_name")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class AccidentDetailSchema(BaseModel):
    """Полная информация по конкретному случаю"""
    id: int
    empt_number: str
    main_info: MainInfoSchema
    vehicles: List[VehicleSchema]
    participants: List[ParticipantSchema]
    model_config = ConfigDict(from_attributes=True)

class AccidentsResponse(BaseModel):
    """Ответ со списком ДТП и общим количеством"""
    total: int
    items: List[AccidentShortSchema]
