from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class District(Base):
    """Федеральные округа"""
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)

    regions = relationship("Region", back_populates="district")

class Region(Base):
    """Субъекты РФ"""
    __tablename__ = "regions"

    code = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    population = Column(Integer)
    vehicles = Column(Integer)

    district = relationship("District", back_populates="regions")
    accidents = relationship("Accident", back_populates="region")

class WeatherType(Base):
    """Погодные условия"""
    __tablename__ = "weather_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    accidents = relationship("Accident", back_populates="weather")

class RoadCondition(Base):
    """Состояние дорожного покрытия"""
    __tablename__ = "road_conditions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    accidents = relationship("Accident", back_populates="road_condition")

class AccidentType(Base):
    """Виды происшествий"""
    __tablename__ = "accident_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    accidents = relationship("Accident", back_populates="accident_type")

class CarType(Base):
    """Категории транспортных средств"""
    __tablename__ = "car_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    vehicles = relationship("Vehicle", back_populates="car_type")

class CarBrand(Base):
    """Марки автомобилей"""
    __tablename__ = "car_brands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    vehicles = relationship("Vehicle", back_populates="car_brand")

class CarModel(Base):
    """Модели автомобилей"""
    __tablename__ = "car_models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    brand_id = Column(Integer, ForeignKey("car_brands.id"), nullable=False)

    vehicles = relationship("Vehicle", back_populates="car_model")
