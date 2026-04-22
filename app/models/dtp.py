from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, Float, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.db.session import Base

# Импортируем классы для отношений, чтобы SQLAlchemy их видела
from app.models.dictionaries import Region, District, WeatherType, RoadCondition, AccidentType, CarType, CarBrand, CarModel

class Accident(Base):
    """Центральный реестр ДТП"""
    __tablename__ = "accidents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    empt_number = Column(String, nullable=False, unique=True)
    accident_type_id = Column(Integer, ForeignKey("accident_types.id"))
    date_dtp = Column(Date, nullable=False)
    time_dtp = Column(Time, nullable=False)
    region_code = Column(String, ForeignKey("regions.code"), nullable=False)
    coord_lat = Column(Float)
    coord_lon = Column(Float)
    locality = Column(String)
    road_name = Column(String)
    road_km = Column(Integer)
    is_city = Column(Boolean, default=True)
    road_category = Column(String)
    is_railway = Column(Boolean, default=False)
    weather_id = Column(Integer, ForeignKey("weather_types.id"))
    road_cond_id = Column(Integer, ForeignKey("road_conditions.id"))
    lighting = Column(String)
    has_road_defect = Column(Boolean, default=False)
    road_type = Column(String)
    road_defect_desc = Column(String)
    fatalities = Column(Integer, nullable=False, default=0)
    injured = Column(Integer, nullable=False, default=0)
    vehicles_count = Column(Integer, nullable=False, default=1)
    participants_count = Column(Integer, nullable=False, default=1)
    driver_fled = Column(Boolean, default=False)
    has_children = Column(Boolean, default=False)
    has_drunk = Column(Boolean, default=False)
    rescue_time_min = Column(Integer)
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
    accident_id = Column(Integer, ForeignKey("accidents.id", ondelete="CASCADE"), nullable=False)
    car_type_id = Column(Integer, ForeignKey("car_types.id"))
    car_brand_id = Column(Integer, ForeignKey("car_brands.id"))
    car_model_id = Column(Integer, ForeignKey("car_models.id"))
    year_release = Column(Integer)
    is_defective = Column(Boolean, default=False)

    # Relationships
    accident = relationship("Accident", back_populates="vehicles")
    car_type = relationship("CarType", back_populates="vehicles")
    car_brand = relationship("CarBrand", back_populates="vehicles")
    car_model = relationship("CarModel", back_populates="vehicles")
    participants = relationship("Participant", back_populates="vehicle")

class Participant(Base):
    """Участники ДТП"""
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    accident_id = Column(Integer, ForeignKey("accidents.id", ondelete="CASCADE"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"))
    role = Column(String, nullable=False)
    is_culprit = Column(Boolean, default=False)
    gender = Column(String)
    age = Column(Integer)
    experience = Column(Integer)
    is_drunk = Column(Boolean, default=False)
    is_intoxication = Column(Boolean, default=False)
    alcohol_level = Column(Float)
    health_status = Column(String)
    first_aid = Column(Boolean, default=False)

    # Relationships
    accident = relationship("Accident", back_populates="participants")
    vehicle = relationship("Vehicle", back_populates="participants")
