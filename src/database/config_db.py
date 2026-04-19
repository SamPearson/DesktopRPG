import os
from sqlalchemy import inspect
from src.database.db import db
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database-specific configuration"""
    
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    INSTANCE_DIR = BASE_DIR / "instance"
    DB_PATH = INSTANCE_DIR / "desktop_rpg.db"
    
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        f"sqlite:///{DB_PATH}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def initialize_database(app):
    """Initialize the database with all tables if they don't exist"""
    with app.app_context():
        logging.info("Starting Database Initialization")

        # Print tables before creation
        logging.debug("Tables in metadata before creation:")
        for table in db.metadata.tables:
            logging.debug("- %s", table)

        # Check if database is being created for the first time
        inspector = inspect(db.engine)
        tables_before = inspector.get_table_names()
        is_new_database = len(tables_before) == 0

        logging.info("Creating tables...")
        db.create_all()

        # Verify tables were created
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        logging.debug("Actual tables in database: %s", tables)

        # Seed database if it was just created
        if is_new_database:
            logging.info("New database detected. Seeding initial data...")
            from src.scripts.db_seed.seed_db import seed_species
            try:
                seed_species()
                logging.info("Database seeding complete")
            except Exception as e:
                logging.error(f"Error seeding database: {str(e)}")
                raise

        logging.info("Database Initialization Complete")