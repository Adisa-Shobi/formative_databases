from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.config.database import get_db
from app.models.models import (
    Country, Producer, Coffee, CuppingScore,
    CountryCreate, CountryUpdate, CountryResponse,
    ProducerCreate, ProducerUpdate, ProducerResponse,
    CoffeeCreate, CoffeeUpdate, CoffeeResponse,
    CuppingScoreCreate, CuppingScoreUpdate, CuppingScoreResponse
)
from datetime import datetime

router = APIRouter()

# Country endpoints
@router.post("/countries/", response_model=CountryResponse, status_code=status.HTTP_201_CREATED)
def create_country(country: CountryCreate, db: Session = Depends(get_db)):
    """
    Create a new country entry
    """
    db_country = db.query(Country).filter(Country.country_name == country.country_name).first()
    if db_country:
        raise HTTPException(status_code=400, detail="Country already exists")
    
    new_country = Country(**country.dict())
    db.add(new_country)
    db.commit()
    db.refresh(new_country)
    return new_country

@router.get("/countries/", response_model=List[CountryResponse])
def read_countries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get a list of countries with pagination
    """
    countries = db.query(Country).offset(skip).limit(limit).all()
    return countries

@router.get("/countries/{country_id}", response_model=CountryResponse)
def read_country(country_id: int, db: Session = Depends(get_db)):
    """
    Get a specific country by ID
    """
    db_country = db.query(Country).filter(Country.country_id == country_id).first()
    if db_country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return db_country

@router.put("/countries/{country_id}", response_model=CountryResponse)
def update_country(country_id: int, country: CountryUpdate, db: Session = Depends(get_db)):
    """
    Update a country entry
    """
    db_country = db.query(Country).filter(Country.country_id == country_id).first()
    if db_country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    
    update_data = country.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_country, key, value)
    
    db.commit()
    db.refresh(db_country)
    return db_country

@router.delete("/countries/{country_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country(country_id: int, db: Session = Depends(get_db)):
    """
    Delete a country entry and all related data
    """
    db_country = db.query(Country).filter(Country.country_id == country_id).first()
    if db_country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    
    db.delete(db_country)
    db.commit()
    return None

# Producer endpoints
@router.post("/producers/", response_model=ProducerResponse, status_code=status.HTTP_201_CREATED)
def create_producer(producer: ProducerCreate, db: Session = Depends(get_db)):
    """
    Create a new producer entry
    """
    db_country = db.query(Country).filter(Country.country_id == producer.country_id).first()
    if db_country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    
    new_producer = Producer(**producer.dict())
    db.add(new_producer)
    db.commit()
    db.refresh(new_producer)
    return new_producer

@router.get("/producers/", response_model=List[ProducerResponse])
def read_producers(skip: int = 0, limit: int = 100, country_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Get a list of producers with optional country_id filter and pagination
    """
    query = db.query(Producer)
    if country_id:
        query = query.filter(Producer.country_id == country_id)
    producers = query.offset(skip).limit(limit).all()
    return producers

@router.get("/producers/{producer_id}", response_model=ProducerResponse)
def read_producer(producer_id: int, db: Session = Depends(get_db)):
    """
    Get a specific producer by ID
    """
    db_producer = db.query(Producer).filter(Producer.producer_id == producer_id).first()
    if db_producer is None:
        raise HTTPException(status_code=404, detail="Producer not found")
    return db_producer

@router.put("/producers/{producer_id}", response_model=ProducerResponse)
def update_producer(producer_id: int, producer: ProducerUpdate, db: Session = Depends(get_db)):
    """
    Update a producer entry
    """
    db_producer = db.query(Producer).filter(Producer.producer_id == producer_id).first()
    if db_producer is None:
        raise HTTPException(status_code=404, detail="Producer not found")
    
    update_data = producer.dict(exclude_unset=True)
    if "country_id" in update_data:
        db_country = db.query(Country).filter(Country.country_id == update_data["country_id"]).first()
        if db_country is None:
            raise HTTPException(status_code=404, detail="Country not found")
    
    for key, value in update_data.items():
        setattr(db_producer, key, value)
    
    db.commit()
    db.refresh(db_producer)
    return db_producer

@router.delete("/producers/{producer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producer(producer_id: int, db: Session = Depends(get_db)):
    """
    Delete a producer entry and all related data
    """
    db_producer = db.query(Producer).filter(Producer.producer_id == producer_id).first()
    if db_producer is None:
        raise HTTPException(status_code=404, detail="Producer not found")
    
    db.delete(db_producer)
    db.commit()
    return None

# Coffee endpoints
@router.post("/coffees/", response_model=CoffeeResponse, status_code=status.HTTP_201_CREATED)
def create_coffee(coffee: CoffeeCreate, db: Session = Depends(get_db)):
    """
    Create a new coffee entry
    """
    db_producer = db.query(Producer).filter(Producer.producer_id == coffee.producer_id).first()
    if db_producer is None:
        raise HTTPException(status_code=404, detail="Producer not found")
    
    new_coffee = Coffee(**coffee.dict())
    
    # Calculate total cup points if all score fields are provided
    score_fields = ['aroma', 'flavor', 'aftertaste', 'acidity', 'body', 'balance', 'uniformity', 'clean_cup', 'sweetness']
    if all(getattr(new_coffee, field) is not None for field in score_fields):
        total_points = (
            new_coffee.aroma + 
            new_coffee.flavor + 
            new_coffee.aftertaste + 
            new_coffee.acidity + 
            new_coffee.body + 
            new_coffee.balance + 
            new_coffee.uniformity + 
            new_coffee.clean_cup + 
            new_coffee.sweetness
        )
        
        new_coffee.total_cup_points = total_points
        
        if total_points >= 80:
            new_coffee.quality_classification = "Specialty"
        elif total_points >= 70:
            new_coffee.quality_classification = "Premium"
        else:
            new_coffee.quality_classification = "Standard"
    
    db.add(new_coffee)
    db.commit()
    db.refresh(new_coffee)
    return new_coffee

@router.get("/coffees/", response_model=List[CoffeeResponse])
def read_coffees(
    skip: int = 0, 
    limit: int = 100, 
    producer_id: Optional[int] = None,
    min_score: Optional[float] = None,
    quality_classification: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get a list of coffees with optional filters and pagination
    """
    query = db.query(Coffee)
    
    if producer_id:
        query = query.filter(Coffee.producer_id == producer_id)
    
    if min_score:
        query = query.filter(Coffee.total_cup_points >= min_score)
    
    if quality_classification:
        query = query.filter(Coffee.quality_classification == quality_classification)
    
    coffees = query.offset(skip).limit(limit).all()
    return coffees

@router.get("/coffees/{coffee_id}", response_model=CoffeeResponse)
def read_coffee(coffee_id: int, db: Session = Depends(get_db)):
    """
    Get a specific coffee by ID
    """
    db_coffee = db.query(Coffee).filter(Coffee.coffee_id == coffee_id).first()
    if db_coffee is None:
        raise HTTPException(status_code=404, detail="Coffee not found")
    return db_coffee

@router.put("/coffees/{coffee_id}", response_model=CoffeeResponse)
def update_coffee(coffee_id: int, coffee: CoffeeUpdate, db: Session = Depends(get_db)):
    """
    Update a coffee entry
    """
    db_coffee = db.query(Coffee).filter(Coffee.coffee_id == coffee_id).first()
    if db_coffee is None:
        raise HTTPException(status_code=404, detail="Coffee not found")
    
    update_data = coffee.dict(exclude_unset=True)
    if "producer_id" in update_data:
        db_producer = db.query(Producer).filter(Producer.producer_id == update_data["producer_id"]).first()
        if db_producer is None:
            raise HTTPException(status_code=404, detail="Producer not found")
    
    for key, value in update_data.items():
        setattr(db_coffee, key, value)
    
    # Recalculate total cup points if relevant fields were updated
    score_fields = ['aroma', 'flavor', 'aftertaste', 'acidity', 'body', 'balance', 'uniformity', 'clean_cup', 'sweetness']
    if any(field in update_data for field in score_fields) and all(getattr(db_coffee, field) is not None for field in score_fields):
        total_points = (
            db_coffee.aroma + 
            db_coffee.flavor + 
            db_coffee.aftertaste + 
            db_coffee.acidity + 
            db_coffee.body + 
            db_coffee.balance + 
            db_coffee.uniformity + 
            db_coffee.clean_cup + 
            db_coffee.sweetness
        )
        
        db_coffee.total_cup_points = total_points
        
        if total_points >= 80:
            db_coffee.quality_classification = "Specialty"
        elif total_points >= 70:
            db_coffee.quality_classification = "Premium"
        else:
            db_coffee.quality_classification = "Standard"
    
    db.commit()
    db.refresh(db_coffee)
    return db_coffee

@router.delete("/coffees/{coffee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_coffee(coffee_id: int, db: Session = Depends(get_db)):
    """
    Delete a coffee entry and all related data
    """
    db_coffee = db.query(Coffee).filter(Coffee.coffee_id == coffee_id).first()
    if db_coffee is None:
        raise HTTPException(status_code=404, detail="Coffee not found")
    
    db.delete(db_coffee)
    db.commit()
    return None

# Cupping Score endpoints
@router.post("/cupping-scores/", response_model=CuppingScoreResponse, status_code=status.HTTP_201_CREATED)
def create_cupping_score(cupping_score: CuppingScoreCreate, db: Session = Depends(get_db)):
    """
    Create a new cupping score entry
    """
    db_coffee = db.query(Coffee).filter(Coffee.coffee_id == cupping_score.coffee_id).first()
    if db_coffee is None:
        raise HTTPException(status_code=404, detail="Coffee not found")
    
    new_cupping_score = CuppingScore(**cupping_score.dict())
    
    # Calculate total score if all required fields are provided
    score_fields = [
        'fragrance_aroma', 'flavor', 'aftertaste', 'acidity', 
        'body', 'balance', 'uniformity', 'clean_cup', 
        'sweetness', 'overall'
    ]
    
    if all(getattr(new_cupping_score, field) is not None for field in score_fields):
        defects = new_cupping_score.defects or 0
        
        total_score = (
            new_cupping_score.fragrance_aroma + 
            new_cupping_score.flavor + 
            new_cupping_score.aftertaste + 
            new_cupping_score.acidity + 
            new_cupping_score.body + 
            new_cupping_score.balance + 
            new_cupping_score.uniformity + 
            new_cupping_score.clean_cup + 
            new_cupping_score.sweetness + 
            new_cupping_score.overall - 
            defects
        )
        
        new_cupping_score.total_score = total_score
    
    db.add(new_cupping_score)
    db.commit()
    db.refresh(new_cupping_score)
    return new_cupping_score

@router.get("/cupping-scores/", response_model=List[CuppingScoreResponse])
def read_cupping_scores(skip: int = 0, limit: int = 100, coffee_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Get a list of cupping scores with optional coffee_id filter and pagination
    """
    query = db.query(CuppingScore)
    
    if coffee_id:
        query = query.filter(CuppingScore.coffee_id == coffee_id)
    
    cupping_scores = query.offset(skip).limit(limit).all()
    return cupping_scores

@router.get("/cupping-scores/{score_id}", response_model=CuppingScoreResponse)
def read_cupping_score(score_id: int, db: Session = Depends(get_db)):
    """
    Get a specific cupping score by ID
    """
    db_cupping_score = db.query(CuppingScore).filter(CuppingScore.score_id == score_id).first()
    if db_cupping_score is None:
        raise HTTPException(status_code=404, detail="Cupping score not found")
    return db_cupping_score

@router.put("/cupping-scores/{score_id}", response_model=CuppingScoreResponse)
def update_cupping_score(score_id: int, cupping_score: CuppingScoreUpdate, db: Session = Depends(get_db)):
    """
    Update a cupping score entry
    """
    db_cupping_score = db.query(CuppingScore).filter(CuppingScore.score_id == score_id).first()
    if db_cupping_score is None:
        raise HTTPException(status_code=404, detail="Cupping score not found")
    
    update_data = cupping_score.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_cupping_score, key, value)
    
    # Recalculate total score if any score field was updated
    score_fields = [
        'fragrance_aroma', 'flavor', 'aftertaste', 'acidity', 
        'body', 'balance', 'uniformity', 'clean_cup', 
        'sweetness', 'overall'
    ]
    
    if any(field in update_data for field in score_fields) and all(getattr(db_cupping_score, field) is not None for field in score_fields):
        defects = db_cupping_score.defects or 0
        
        total_score = (
            db_cupping_score.fragrance_aroma + 
            db_cupping_score.flavor + 
            db_cupping_score.aftertaste + 
            db_cupping_score.acidity + 
            db_cupping_score.body + 
            db_cupping_score.balance + 
            db_cupping_score.uniformity + 
            db_cupping_score.clean_cup + 
            db_cupping_score.sweetness + 
            db_cupping_score.overall - 
            defects
        )
        
        db_cupping_score.total_score = total_score
    
    db.commit()
    db.refresh(db_cupping_score)
    return db_cupping_score

@router.delete("/cupping-scores/{score_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cupping_score(score_id: int, db: Session = Depends(get_db)):
    """
    Delete a cupping score entry
    """
    db_cupping_score = db.query(CuppingScore).filter(CuppingScore.score_id == score_id).first()
    if db_cupping_score is None:
        raise HTTPException(status_code=404, detail="Cupping score not found")
    
    db.delete(db_cupping_score)
    db.commit()
    return None

# Latest entry endpoints
@router.get("/coffees/latest/", response_model=CoffeeResponse)
def get_latest_coffee(db: Session = Depends(get_db)):
    print("Fetching latest coffee...")
    count = db.query(Coffee).count()
    print(f"Total coffee count: {count}")
    
    if count > 0:
        # Show a sample coffee to verify data
        sample = db.query(Coffee).first()
        print(f"Sample coffee: ID={sample.coffee_id}, Producer={sample.producer_id}")
    
    latest_coffee = db.query(Coffee).order_by(Coffee.created_at.desc()).first()
    
    if latest_coffee is None:
        print("No latest coffee found!")
        raise HTTPException(status_code=404, detail="No coffee entries found")
    
    print(f"Found latest coffee: ID={latest_coffee.coffee_id}")
    return latest_coffee

@router.get("/producers/latest/", response_model=ProducerResponse)
def get_latest_producer(db: Session = Depends(get_db)):
    """
    Get the most recently added producer
    """
    latest_producer = db.query(Producer).order_by(Producer.created_at.desc()).first()
    if latest_producer is None:
        raise HTTPException(status_code=404, detail="No producer entries found")
    return latest_producer

@router.get("/cupping-scores/latest/", response_model=CuppingScoreResponse)
def get_latest_cupping_score(db: Session = Depends(get_db)):
    """
    Get the most recently added cupping score
    """
    latest_score = db.query(CuppingScore).order_by(CuppingScore.created_at.desc()).first()
    if latest_score is None:
        raise HTTPException(status_code=404, detail="No cupping score entries found")
    return latest_score