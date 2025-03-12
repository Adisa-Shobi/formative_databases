import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pymongo
import motor.motor_asyncio

# Load environment variables
load_dotenv()

# PostgreSQL Configuration
POSTGRES_URI = os.getenv("DB_URI")
engine = create_engine(POSTGRES_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# PostgreSQL Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI")
mongo_client = pymongo.MongoClient(MONGODB_URI)
mongodb = mongo_client.coffee_quality_db
async_mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
async_mongodb = async_mongo_client.coffee_quality_db