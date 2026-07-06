"""
database/reset_and_load.py
Drops all existing tables, recreates them, and populates them using the newly generated raw CSV files.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import SessionLocal, engine
from database.models import Base
from database.loader import load_csv_to_db
from utils.logger import logger

def main():
    logger.info("Starting database reset...")
    try:
        # Drop all tables
        logger.info("Dropping all existing database tables...")
        Base.metadata.drop_all(bind=engine)
        
        # Recreate tables
        logger.info("Recreating database tables from schema models...")
        Base.metadata.create_all(bind=engine)
        
        # Load CSVs
        logger.info("Loading new synthetic cosmetics data into PostgreSQL...")
        db = SessionLocal()
        results = load_csv_to_db(db)
        db.close()
        
        logger.info("Database reset and load complete!")
        for file, res in results.items():
            logger.info(f"  {file}: {res}")
            
    except Exception as e:
        logger.error(f"Error during database reset/load: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
