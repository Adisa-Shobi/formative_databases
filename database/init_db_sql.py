#!/usr/bin/env python3
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
import os

def connect_to_postgresql(connection_str):
    try:
        # Connection parameters - replace with your actual database details
        connection = psycopg2.connect(connection_str)
        # Create a cursor object
        cursor = connection.cursor()
        
        # Print PostgreSQL details
        print("Connected to PostgreSQL")
        print("PostgreSQL server information:")
        print(connection.get_dsn_parameters())
        
        # Execute a simple query
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print("PostgreSQL database version:", db_version)
        
        return connection, cursor
        
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL:", error)
        return None, None

def close_connection(connection, cursor):
    if cursor:
        cursor.close()
    if connection:
        connection.close()
        print("PostgreSQL connection is closed")

def get_unique_values(df, column):
    return df[column].unique()

def create_dataset_tables(cursor):
    # Create certifier table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS certifier (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            address VARCHAR(100) NOT NULL,
            contact VARCHAR(100) NOT NULL
        )
        """
    )

    # Create country table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS country (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
        """
    )

    # Create region table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS region (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            country INTEGER REFERENCES country(id)
        )
        """
    )

    # Create variety table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS variety (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
        """
    )

    # Create processing table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS processing (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
        """
    )

    # Create partner table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS partner (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
        """
    )

    # Create owner table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS owner (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
        """
    )

    # Create coffee table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS coffee (
            id SERIAL PRIMARY KEY,
            farm_name VARCHAR(100) NOT NULL,
            lot_number VARCHAR(100) NOT NULL,
            mill VARCHAR(100) NOT NULL,
            ico_number VARCHAR(100) NOT NULL,
            company VARCHAR(100) NOT NULL,
            altitude VARCHAR(100) NOT NULL,
            region INTEGER REFERENCES region(id),
            producer VARCHAR(100) NOT NULL,
            no_bags INTEGER NOT NULL,
            bag_weight INTEGER NOT NULL,
            partner INTEGER REFERENCES partner(id),
            harvest_year VARCHAR(100) NOT NULL,
            grading_date DATE NOT NULL,
            owner INTEGER REFERENCES owner(id),
            variety INTEGER REFERENCES variety(id),
            status VARCHAR(20) NOT NULL CHECK (status IN ('Completed', 'In Progress', 'Pending')),
            processing INTEGER REFERENCES processing(id),
            aroma INTEGER NOT NULL,
            flavor INTEGER NOT NULL,
            aftertaste INTEGER NOT NULL,
            acidity INTEGER NOT NULL,
            body INTEGER NOT NULL,
            balance INTEGER NOT NULL,
            uniformity INTEGER NOT NULL,
            clean_cup INTEGER NOT NULL,
            sweetness INTEGER NOT NULL,
            overall INTEGER NOT NULL,
            defects INTEGER NOT NULL,
            total_cup_points INTEGER NOT NULL,
            moisture_percentage INTEGER NOT NULL,
            category_one_defects INTEGER NOT NULL,
            expiration_date DATE NOT NULL,
            certifier INTEGER REFERENCES certifier(id)
        )
        """
    )

def setup_coffee_audit_trigger(cursor):
    """
    Sets up an audit log table with a foreign key reference to the coffee table
    and creates a trigger to log all changes.
    
    :param cursor: psycopg2 database cursor
    """
    try:
        # Create audit log table with foreign key reference
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS coffee_audit_log (
            log_id SERIAL PRIMARY KEY,
            operation_type VARCHAR(10) NOT NULL,
            coffee_id INTEGER REFERENCES coffee(id) ON DELETE SET NULL,
            farm_name VARCHAR(100),
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Create trigger function
        cursor.execute("""
        CREATE OR REPLACE FUNCTION log_coffee_changes()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF (TG_OP = 'INSERT') THEN
                INSERT INTO coffee_audit_log (
                    operation_type, coffee_id, farm_name
                ) VALUES (
                    'INSERT', NEW.id, NEW.farm_name
                );
                RETURN NEW;
            
            ELSIF (TG_OP = 'UPDATE') THEN
                INSERT INTO coffee_audit_log (
                    operation_type, coffee_id, farm_name
                ) VALUES (
                    'UPDATE', NEW.id, NEW.farm_name
                );
                RETURN NEW;
            
            ELSIF (TG_OP = 'DELETE') THEN
                INSERT INTO coffee_audit_log (
                    operation_type, coffee_id, farm_name
                ) VALUES (
                    'DELETE', OLD.id, OLD.farm_name
                );
                RETURN OLD;
            END IF;
        END;
        $$
        """)

        # Create the trigger
        cursor.execute("""
        DROP TRIGGER IF EXISTS coffee_changes_trigger ON coffee;
        CREATE TRIGGER coffee_changes_trigger
        AFTER INSERT OR UPDATE OR DELETE ON coffee
            FOR EACH ROW EXECUTE FUNCTION log_coffee_changes()
        """)

        print("Audit trigger and log table set up successfully.")
    
    except Exception as e:
        print(f"Error setting up audit trigger: {e}")
        raise


if __name__ == "__main__":
    load_dotenv()

    # Get database connection details from environment variables
    conn = os.getenv("DB_URI", "")

    # Connect to the database
    connection, cursor = connect_to_postgresql(connection_str=conn)
    
    # Create dataset tables
    create_dataset_tables(cursor)

    # Create procedures and triggers]
    setup_coffee_audit_trigger(cursor)

    
    # Close the connection
    close_connection(connection, cursor)