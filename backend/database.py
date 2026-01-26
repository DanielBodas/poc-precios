import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Obtener URL de la base de datos de las variables de entorno (Render)
# O usar SQLite local como fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./precios.db")

# Ajuste para compatibilidad con PostgreSQL en Render (si empieza por postgres://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine_args = {}
# SQLite necesita este argumento específico, Postgres no
if DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
