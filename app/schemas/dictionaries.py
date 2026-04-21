from typing import Optional, Union
from pydantic import BaseModel, ConfigDict

class DistrictSchema(BaseModel):
    """Схема федерального округа"""
    id: int
    code: str
    name: str
    model_config = ConfigDict(from_attributes=True)

class RegionSchema(BaseModel):
    """Схема региона"""
    code: str
    name: str
    district_id: int
    population: Optional[int] = None
    vehicles: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class RegionResponseSchema(BaseModel):
    """Схема ответа для региона с названием округа"""
    region_code: str
    region_name: str
    district_name: str
    population: Optional[int] = None
    vehicles_count: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class BaseDictionarySchema(BaseModel):
    """Универсальная схема для простых справочников"""
    id: Union[int, str]
    name: str
    model_config = ConfigDict(from_attributes=True)

class WeatherTypeSchema(BaseDictionarySchema):
    """Схема типа погоды"""
    pass

class RoadConditionSchema(BaseDictionarySchema):
    """Схема состояния дороги"""
    pass

class AccidentTypeSchema(BaseDictionarySchema):
    """Схема типа ДТП"""
    pass

class CarTypeSchema(BaseDictionarySchema):
    """Схема типа ТС"""
    pass

class CarModelSchema(BaseModel):
    """Схема модели ТС"""
    id: int
    name: str
    brand: str
    model_config = ConfigDict(from_attributes=True)
