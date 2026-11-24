"""
Database setup and session management supporting SQLite and PostgreSQL
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# Ensure sqlite data directory exists if using sqlite
if settings.DATABASE_URL.startswith("sqlite"):
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    if db_path and not db_path.startswith(":memory:"):
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

connect_args = {"check_same_thread": False, "timeout": 30.0} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> dict:
    """Verifies actual database connectivity and returns status metadata."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_type = "sqlite" if settings.DATABASE_URL.startswith("sqlite") else "postgresql"
        return {"connected": True, "type": db_type}
    except Exception as exc:
        return {"connected": False, "error": str(exc)}
