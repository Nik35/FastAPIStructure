from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

DATABASE_URL = settings.DATABASE_URL

# Create a SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a SessionLocal class to get a new session for each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a declarative base to be used by all our models
Base = declarative_base()

def get_db():
    """
    Dependency function to get a database session.
    It yields a session which is automatically closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Creates all tables defined in Base's metadata.
    This should be called at application startup.
    """
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created successfully.")
