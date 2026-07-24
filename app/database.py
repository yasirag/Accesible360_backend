"""
app/database.py
Configuración de la conexión a PostgreSQL con SQLAlchemy (SYNC con psycopg).
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

# Variables de entorno
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_NAME = os.getenv("DATABASE_NAME", "Accesible360")

# URL de conexión (SYNC con psycopg)
DATABASE_URL = f"postgresql+psycopg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# Engine SYNC (no async)
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

# Session factory SYNC (no async)
SessionLocal = sessionmaker(
    engine,
    autocommit=False,
    autoflush=False,
)

# Base para declarar modelos
Base = declarative_base()


def get_db():
    """Dependency para FastAPI - proporciona sesión de BD (SYNC)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def close_db():
    """Cierra el engine en shutdown de FastAPI."""
    engine.dispose()