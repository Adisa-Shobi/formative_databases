from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, Text
from sqlalchemy.orm import relationship
from app.config.database import Base
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

# SQLAlchemy Models
class Country(Base):
    __tablename__ = "countries"
    
    country_id = Column(Integer, primary_key=True, index=True)
    country_name = Column(String, unique=True, nullable=False)
    region = Column(String)
    continent = Column(String)
    
    producers = relationship("Producer", back_populates="country", cascade="all, delete-orphan")

class Producer(Base):
    __tablename__ = "producers"
    
    producer_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    country_id = Column(Integer, ForeignKey("countries.country_id", ondelete="CASCADE"))
    farm_name = Column(String)
    mill = Column(String)
    altitude_mean_meters = Column(Float)
    certification_body = Column(String)
    certification_address = Column(String)
    certification_contact = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    country = relationship("Country", back_populates="producers")
    coffees = relationship("Coffee", back_populates="producer", cascade="all, delete-orphan")

class Coffee(Base):
    __tablename__ = "coffees"
    
    coffee_id = Column(Integer, primary_key=True, index=True)
    producer_id = Column(Integer, ForeignKey("producers.producer_id", ondelete="CASCADE"))
    harvest_year = Column(Integer)
    grading_date = Column(Date)
    variety = Column(String)
    processing_method = Column(String)
    aroma = Column(Float)
    flavor = Column(Float)
    aftertaste = Column(Float)
    acidity = Column(Float)
    body = Column(Float)
    balance = Column(Float)
    uniformity = Column(Float)
    clean_cup = Column(Float)
    sweetness = Column(Float)
    moisture_percentage = Column(Float)
    category = Column(String)
    quakers = Column(Integer)
    color = Column(String)
    total_cup_points = Column(Float)
    quality_classification = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    producer = relationship("Producer", back_populates="coffees")
    cupping_scores = relationship("CuppingScore", back_populates="coffee", cascade="all, delete-orphan")

class CuppingScore(Base):
    __tablename__ = "cupping_scores"
    
    score_id = Column(Integer, primary_key=True, index=True)
    coffee_id = Column(Integer, ForeignKey("coffees.coffee_id", ondelete="CASCADE"))
    cupper_name = Column(String)
    tasting_date = Column(Date)
    fragrance_aroma = Column(Float)
    flavor = Column(Float)
    aftertaste = Column(Float)
    acidity = Column(Float)
    body = Column(Float)
    balance = Column(Float)
    uniformity = Column(Float)
    clean_cup = Column(Float)
    sweetness = Column(Float)
    overall = Column(Float)
    defects = Column(Float)
    total_score = Column(Float)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    coffee = relationship("Coffee", back_populates="cupping_scores")

# Pydantic Schemas
class CountryBase(BaseModel):
    country_name: str
    region: Optional[str] = None
    continent: Optional[str] = None

class CountryCreate(CountryBase):
    pass

class CountryUpdate(BaseModel):
    country_name: Optional[str] = None
    region: Optional[str] = None
    continent: Optional[str] = None

class CountryResponse(CountryBase):
    country_id: int
    
    class Config:
        from_attributes = True

class ProducerBase(BaseModel):
    company_name: str
    country_id: int
    farm_name: Optional[str] = None
    mill: Optional[str] = None
    altitude_mean_meters: Optional[float] = None
    certification_body: Optional[str] = None
    certification_address: Optional[str] = None
    certification_contact: Optional[str] = None

class ProducerCreate(ProducerBase):
    pass

class ProducerUpdate(BaseModel):
    company_name: Optional[str] = None
    country_id: Optional[int] = None
    farm_name: Optional[str] = None
    mill: Optional[str] = None
    altitude_mean_meters: Optional[float] = None
    certification_body: Optional[str] = None
    certification_address: Optional[str] = None
    certification_contact: Optional[str] = None

class ProducerResponse(ProducerBase):
    producer_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CoffeeBase(BaseModel):
    producer_id: int
    harvest_year: Optional[int] = None
    grading_date: Optional[date] = None
    variety: Optional[str] = None
    processing_method: Optional[str] = None
    aroma: Optional[float] = None
    flavor: Optional[float] = None
    aftertaste: Optional[float] = None
    acidity: Optional[float] = None
    body: Optional[float] = None
    balance: Optional[float] = None
    uniformity: Optional[float] = None
    clean_cup: Optional[float] = None
    sweetness: Optional[float] = None
    moisture_percentage: Optional[float] = None
    category: Optional[str] = None
    quakers: Optional[int] = None
    color: Optional[str] = None

class CoffeeCreate(CoffeeBase):
    pass

class CoffeeUpdate(BaseModel):
    producer_id: Optional[int] = None
    harvest_year: Optional[int] = None
    grading_date: Optional[date] = None
    variety: Optional[str] = None
    processing_method: Optional[str] = None
    aroma: Optional[float] = None
    flavor: Optional[float] = None
    aftertaste: Optional[float] = None
    acidity: Optional[float] = None
    body: Optional[float] = None
    balance: Optional[float] = None
    uniformity: Optional[float] = None
    clean_cup: Optional[float] = None
    sweetness: Optional[float] = None
    moisture_percentage: Optional[float] = None
    category: Optional[str] = None
    quakers: Optional[int] = None
    color: Optional[str] = None

class CoffeeResponse(CoffeeBase):
    coffee_id: int
    total_cup_points: Optional[float] = None
    quality_classification: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CuppingScoreBase(BaseModel):
    coffee_id: int
    cupper_name: Optional[str] = None
    tasting_date: Optional[date] = None
    fragrance_aroma: Optional[float] = None
    flavor: Optional[float] = None
    aftertaste: Optional[float] = None
    acidity: Optional[float] = None
    body: Optional[float] = None
    balance: Optional[float] = None
    uniformity: Optional[float] = None
    clean_cup: Optional[float] = None
    sweetness: Optional[float] = None
    overall: Optional[float] = None
    defects: Optional[float] = None
    notes: Optional[str] = None

class CuppingScoreCreate(CuppingScoreBase):
    pass

class CuppingScoreUpdate(BaseModel):
    cupper_name: Optional[str] = None
    tasting_date: Optional[date] = None
    fragrance_aroma: Optional[float] = None
    flavor: Optional[float] = None
    aftertaste: Optional[float] = None
    acidity: Optional[float] = None
    body: Optional[float] = None
    balance: Optional[float] = None
    uniformity: Optional[float] = None
    clean_cup: Optional[float] = None
    sweetness: Optional[float] = None
    overall: Optional[float] = None
    defects: Optional[float] = None
    notes: Optional[str] = None

class CuppingScoreResponse(CuppingScoreBase):
    score_id: int
    total_score: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True