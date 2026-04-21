from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, Float, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.db.session import Base

class Accident(Base):
    """Центральный реестр ДТП"""
    __tablename__ = "accidents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    empt_number = Column(String, nullable=False, unique=True)  # Системный номер ГИБДД

    accident_type_id = Column(Integer, ForeignKey("accident_types.id"))
    date_dtp = Column(Date, nullable=False)  # ГГГГ-ММ-ДД
    time_dtp = Column(Time, nullable=False)  # ЧЧ:ММ

    region_code = Column(String, ForeignKey("regions.code"), nullable=False)
    coord_lat = Column(Float)  # Широта
    coord_lon = Column(Float)  # Долгота
    locality = Column(String)  # Населённый пункт
    road_name = Column(String) # Название дороги
    road_km = Column(Integer)  # Километр дороги
    is_city = Column(Boolean, default=True) # 1=в городе, 0=трасса
    road_category = Column(String) # "Федеральная", "Региональная", "Местная"
    is_railway = Column(Boolean, default=False) # ДТП на ж/д переезде

    weather_id = Column(Integer, ForeignKey("weather_types.id"))
    road_cond_id = Column(Integer, ForeignKey("road_conditions.id"))
    lighting = Column(String) # Освещение
    has_road_defect = Column(Integer, default=0) # Дефект дороги
    road_type = Column(String) # Тип дороги
    road_defect_desc = Column(String) # Описание дефекта

    fatalities = Column(Integer, nullable=False, default=0) # Кол-во погибших
    injured = Column(Integer, nullable=False, default=0)    # Кол-во раненых
    vehicles_count = Column(Integer, nullable=False, default=1) # Кол-во ТС
    participants_count = Column(Integer, nullable=False, default=1) # Кол-во участников

    driver_fled = Column(Boolean, default=False) # Водитель скрылся
    has_children = Column(Boolean, default=False) # Есть несовершеннолетние
    has_drunk = Column(Boolean, default=False) # Есть нетрезвые

    rescue_time_min = Column(Integer) # Время прибытия спецслужб
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    region = relationship("Region", back_populates="accidents")
    accident_type = relationship("AccidentType", back_populates="accidents")
    weather = relationship("WeatherType", back_populates="accidents")
    road_condition = relationship("RoadCondition", back_populates="accidents")
    vehicles = relationship("Vehicle", back_populates="accident")
    participants = relationship("Participant", back_populates="accident")

class Vehicle(Base):
    """Транспортные средства в ДТП"""
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    accident_id = Column(Integer, ForeignKey("accidents.id"), nullable=False)
    car_type_id = Column(Integer, ForeignKey("car_types.id"))
    car_model_id = Column(Integer, ForeignKey("car_models.id"))
    year_release = Column(Integer) # Год выпуска ТС
    is_defective = Column(Integer, nullable=False, default=0) # Техническая неисправность

    # Relationships
    accident = relationship("Accident", back_populates="vehicles")
    car_type = relationship("CarType", back_populates="vehicles")
    car_model = relationship("CarModel", back_populates="vehicles")
    participants = relationship("Participant", back_populates="vehicle")

class Participant(Base):
    """Участники ДТП"""
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    accident_id = Column(Integer, ForeignKey("accidents.id", ondelete="CASCADE"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id")) # NULL для пешеходов

    role = Column(String, nullable=False) # "Водитель", "Пешеход" ...
    is_culprit = Column(Integer, nullable=False, default=0) # Виновник ДТП

    gender = Column(Boolean) # 1=мужской, 0=женский
    age = Column(Integer) # Возраст
    experience = Column(Integer) # Стаж вождения

    is_drunk = Column(String) # Алкогольное опьянение
    is_intoxication = Column(String) # Наркотическое опьянение
    alcohol_level = Column(Float) # Промилле
    before_health = Column(String) # Состояние до аварии
    health_status = Column(String) # "Погиб", "Тяжкий вред" ...
    first_aid = Column(Integer, nullable=False, default=0) # Оказана первая помощь

    # Relationships
    accident = relationship("Accident", back_populates="participants")
    vehicle = relationship("Vehicle", back_populates="participants")
