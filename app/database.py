import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
from .config import DATABASE_URL

logger = logging.getLogger(__name__)

def create_db_engine():
    retries = 5
    while retries:
        try:
            engine = create_engine(DATABASE_URL)
            engine.connect()
            logger.info("Successfully connected to database")
            return engine
        except OperationalError as e:
            retries-=1
            if retries==0:
                logger.error(f"Failed to connect to database after all retries: {e}")
                raise
            logger.warning(f"Database connection failed. Retrying in 5 seconds... ({retries} retries left)")
            time.sleep(5)

engine = create_db_engine()
SessionLocal = sessionmaker(autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise
