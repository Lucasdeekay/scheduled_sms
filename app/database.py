"""
This module sets up the SQLAlchemy database connection, session management,
and base model class used across the application.

It loads the database URL from the application's settings and initializes
an SQLAlchemy engine. A session factory (`SessionLocal`) is created for
managing database interactions, and the `get_db` function provides a safe,
clean dependency for obtaining a session (commonly used in FastAPI routes).
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

# Load application settings (database URL, etc.)
settings = get_settings()

# ---------------------------------------------------------
# Database Engine Configuration
# ---------------------------------------------------------
# The engine is responsible for connecting SQLAlchemy to the database.
# For SQLite, the `check_same_thread` argument must be disabled because
# SQLAlchemy creates connections in different threads.
#
# For production environments, replace SQLite with:
#   - PostgreSQL -> "postgresql://user:password@host:port/dbname"
#   - MySQL      -> "mysql+pymysql://user:password@host:port/dbname"
# ---------------------------------------------------------
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # Only needed for SQLite
)

# ---------------------------------------------------------
# Session Factory
# ---------------------------------------------------------
# `SessionLocal` is a configured session class. Each request gets its own
# database session to ensure safe, isolated database operations.
# ---------------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ---------------------------------------------------------
# Base Model Class
# ---------------------------------------------------------
# All SQLAlchemy ORM models must inherit from this base class.
# ---------------------------------------------------------
Base = declarative_base()


def get_db():
    """
    Provides a database session for request handling.

    This function is typically used as a dependency in FastAPI routes.
    It creates a new session, yields it to the route handler, and ensures
    the session is closed afterward, preventing connection leaks.

    Yields:
        Session: A SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
