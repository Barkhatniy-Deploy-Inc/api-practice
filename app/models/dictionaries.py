from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class District(Base):
    """Федеральные округа"""
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False, unique=True)  # "ЦФО", "ПФО" ...
    name = Column(String, nullable=False, unique=True)  # "Центральный федеральный округ"

    regions = relationship("Region", back_populates="district")

class Region(Base):
    """Субъекты РФ"""
    __tablename__ = "regions"

    code = Column(String, primary_key=True)  # "77", "50" ...
    name = Column(String, nullable=False)    # "гор. Москва"
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    population = Column(Integer)             # Численность населения
    vehicles = Column(Integer)               # Кол-во зарегистрированных ТС

    district = relationship("District", back_populates="regions")
    accidents = relationship("Accident", back_populates="region")

class WeatherType(Base):
    """Погодные условия"""
    __tablename__ = "weather_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)  # "Ясно", "Дождь" ...

    accidents = relationship("Accident", back_populates="weather")

class RoadCondition(Base):
    """Состояние дорожного покрытия"""
    __tablename__ = "road_conditions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)  # "Сухое", "Мокрое" ...

    accidents = relationship("Accident", back_populates="road_condition")

class AccidentType(Base):
    """Виды происшествий"""
    __tablename__ = "accident_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)  # "Наезд на пешехода", "Столкновение" ...

    accidents = relationship("Accident", back_populates="accident_type")

class CarType(Base):
    """Категории транспортных средств"""
    __tablename__ = "car_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)  # "Легковой", "Грузовой" ...

    vehicles = relationship("Vehicle", back_populates="car_type")

class CarModel(Base):
    """Модели автомобилей"""
    __tablename__ = "car_models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)   # "Logan"
    brand = Column(String, nullable=False)  # "Renault"

    vehicles = relationship("Vehicle", back_populates="car_model")
