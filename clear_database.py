import os
from pymongo import MongoClient
from dotenv import load_dotenv

def clear_entire_database():
    load_dotenv()
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        print("MONGODB_URI not found in environment.")
        return

    client = MongoClient(mongo_uri)
    db_name = "aegis_db"
    
    # Confirming the database name from core/database.py
    print(f"Connecting to MongoDB and dropping database: {db_name}...")
    
    try:
        # Dropping the entire database will clear all collections including 'attacks', 'defense_memory', etc.
        client.drop_database(db_name)
        print(f"Successfully cleared the entire AEGIS database ('{db_name}').")
        print("All attack logs, defense memory, and simulation results have been reset.")
    except Exception as e:
        print(f"Error while clearing database: {e}")

if __name__ == "__main__":
    clear_entire_database()
