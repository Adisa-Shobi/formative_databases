#!/usr/bin/env python3
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
import pandas as pd
import certifi

def connect_to_mongodb(connection_str, ca_certs=None):
    """
    Connect to MongoDB and return client and database objects
    
    Args:
        connection_str (str): MongoDB connection string
        ca_certs (str, optional): Path to CA certificates file
    """
    try:
        # Connection options
        options = {
            # Use TLS/SSL for Atlas connections
            "tls": True if "mongodb+srv" in connection_str or ".mongodb.net" in connection_str else False,
            # Specify timeout
            "serverSelectionTimeoutMS": 5000,
            "connectTimeoutMS": 10000
        }
        
        # Add CA certificates if provided
        if ca_certs:
            options["tlsCAFile"] = ca_certs
        # Otherwise, disable certificate verification (less secure but works)
        elif options["tls"]:
            options["tlsAllowInvalidCertificates"] = True
        
        # Create a connection to MongoDB
        client = MongoClient(connection_str, **options)
        
        # Use the coffee_db database
        db = client.coffee_db
        
        # Test the connection
        server_info = client.server_info()
        print("Connected to MongoDB")
        print("MongoDB server information:")
        print(f"Version: {server_info['version']}")
        
        return client, db
        
    except Exception as error:
        print("Error while connecting to MongoDB:", error)
        return None, None

def close_connection(client):
    """
    Close the MongoDB connection
    """
    if client:
        client.close()
        print("MongoDB connection is closed")

def create_collections_and_validators(db):
    """
    Create MongoDB collections with schema validation
    """
    # Create certifier collection
    if "certifier" not in db.list_collection_names():
        db.create_collection("certifier", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name", "address", "contact"],
                "properties": {
                    "name": {"bsonType": "string"},
                    "address": {"bsonType": "string"},
                    "contact": {"bsonType": "string"}
                }
            }
        })
        print("Created certifier collection")

    # Create country collection
    if "country" not in db.list_collection_names():
        db.create_collection("country", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name"],
                "properties": {
                    "name": {"bsonType": "string"}
                }
            }
        })
        print("Created country collection")

    # Create region collection
    if "region" not in db.list_collection_names():
        db.create_collection("region", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name", "country_id"],
                "properties": {
                    "name": {"bsonType": "string"},
                    "country_id": {"bsonType": "objectId"}
                }
            }
        })
        print("Created region collection")

    # Create variety collection
    if "variety" not in db.list_collection_names():
        db.create_collection("variety", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name"],
                "properties": {
                    "name": {"bsonType": "string"}
                }
            }
        })
        print("Created variety collection")

    # Create processing collection
    if "processing" not in db.list_collection_names():
        db.create_collection("processing", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name"],
                "properties": {
                    "name": {"bsonType": "string"}
                }
            }
        })
        print("Created processing collection")

    # Create partner collection
    if "partner" not in db.list_collection_names():
        db.create_collection("partner", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name"],
                "properties": {
                    "name": {"bsonType": "string"}
                }
            }
        })
        print("Created partner collection")

    # Create owner collection
    if "owner" not in db.list_collection_names():
        db.create_collection("owner", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name"],
                "properties": {
                    "name": {"bsonType": "string"}
                }
            }
        })
        print("Created owner collection")

    # Create coffee collection
    if "coffee" not in db.list_collection_names():
        db.create_collection("coffee", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "farm_name", "lot_number", "mill", "ico_number", "company", 
                    "altitude", "region_id", "producer", "no_bags", "bag_weight", 
                    "partner_id", "harvest_year", "grading_date", "owner_id", 
                    "variety_id", "status", "processing_id", "aroma", "flavor", 
                    "aftertaste", "acidity", "body", "balance", "uniformity", 
                    "clean_cup", "sweetness", "overall", "defects", "total_cup_points", 
                    "moisture_percentage", "category_one_defects", "expiration_date", "certifier_id"
                ],
                "properties": {
                    "farm_name": {"bsonType": "string"},
                    "lot_number": {"bsonType": "string"},
                    "mill": {"bsonType": "string"},
                    "ico_number": {"bsonType": "string"},
                    "company": {"bsonType": "string"},
                    "altitude": {"bsonType": "string"},
                    "region_id": {"bsonType": "objectId"},
                    "producer": {"bsonType": "string"},
                    "no_bags": {"bsonType": "int"},
                    "bag_weight": {"bsonType": "int"},
                    "partner_id": {"bsonType": "objectId"},
                    "harvest_year": {"bsonType": "string"},
                    "grading_date": {"bsonType": "date"},
                    "owner_id": {"bsonType": "objectId"},
                    "variety_id": {"bsonType": "objectId"},
                    "status": {
                        "bsonType": "string",
                        "enum": ["Completed", "In Progress", "Pending"]
                    },
                    "processing_id": {"bsonType": "objectId"},
                    "aroma": {"bsonType": "int"},
                    "flavor": {"bsonType": "int"},
                    "aftertaste": {"bsonType": "int"},
                    "acidity": {"bsonType": "int"},
                    "body": {"bsonType": "int"},
                    "balance": {"bsonType": "int"},
                    "uniformity": {"bsonType": "int"},
                    "clean_cup": {"bsonType": "int"},
                    "sweetness": {"bsonType": "int"},
                    "overall": {"bsonType": "int"},
                    "defects": {"bsonType": "int"},
                    "total_cup_points": {"bsonType": "int"},
                    "moisture_percentage": {"bsonType": "int"},
                    "category_one_defects": {"bsonType": "int"},
                    "expiration_date": {"bsonType": "date"},
                    "certifier_id": {"bsonType": "objectId"}
                }
            }
        })
        print("Created coffee collection")

def create_indexes(db):
    """
    Create indexes for better query performance
    """
    # Create indexes for coffee collection
    db.coffee.create_index("farm_name")
    db.coffee.create_index("region_id")
    db.coffee.create_index("variety_id")
    db.coffee.create_index("processing_id")
    
    # Create indexes for region collection
    db.region.create_index("country_id")
    
    print("Created indexes for collections")

def get_unique_values(data, column):
    """
    Get unique values from a column
    """
    return data[column].unique()

if __name__ == "__main__":
    load_dotenv()

    # Get database connection details from environment variables
    conn = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    
    # Alternative connection methods (uncomment one if the default doesn't work)
    # Method 1: Using certifi's certificates
    # client, db = connect_to_mongodb(connection_str=conn, ca_certs=certifi.where())
    
    # Method 2: Using direct connection
    # conn += "?directConnection=true"

    # Connect to the database
    client, db = connect_to_mongodb(connection_str=conn)
    
    if client is not None and db is not None:
        # Create collections with validators (MongoDB's equivalent to tables with constraints)
        create_collections_and_validators(db)
        
        # Create indexes for better performance
        create_indexes(db)
        
        # Close the connection
        close_connection(client)
    else:
        print("Failed to connect to MongoDB. Please check your connection string and ensure MongoDB is running.")