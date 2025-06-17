import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# --- Database Configuration ---
# TODO: Replace with your actual database connection string.
# It's recommended to load this from environment variables or a config file for security.
# Example for local PostgreSQL: "postgresql+psycopg2://username:password@localhost:5432/mydatabase"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/db_name")

# Convert Neon's postgresql:// to SQLAlchemy's postgresql+psycopg2://
if DATABASE_URL.startswith("postgresql://"):
    SQLALCHEMY_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
else:
    SQLALCHEMY_DATABASE_URL = DATABASE_URL

# --- SQLAlchemy Engine ---
# The engine is the starting point for any SQLAlchemy application.
# It's configured with the database URL and can include options for connection pooling.
# For production, you might want to configure pool_size, max_overflow, etc.
# e.g., engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=5, max_overflow=10)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# --- SQLAlchemy Session ---
# SessionLocal is a factory for creating new database sessions.
# Each instance of SessionLocal will be a database session.
# autocommit=False and autoflush=False are common defaults.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Declarative Base ---
# Base is a class that all your SQLAlchemy models will inherit from.
# It allows SQLAlchemy to map your Python classes to database tables.
Base = declarative_base()

# --- Dependency for Database Session ---
# This function can be used as a dependency (e.g., in FastAPI)
# to provide a database session to your service functions/endpoints.
# It ensures the session is always closed after the request is handled.
def get_db():
    """
    Provides a database session and ensures it's closed afterwards.
    """
    db = SessionLocal()
    try:
        yield db  # Provides the session to the caller
    finally:
        db.close() # Closes the session

# You can add other database utility functions here if needed.
