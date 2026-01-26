import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Configuración de base de datos dinámica
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

# Si tenemos las variables individuales de Postgres, construimos la URI
if all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
else:
    # Fallback: intentar DATABASE_URL directo o finalmente SQLite local
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./precios.db")

# Ajuste para compatibilidad con PostgreSQL en Render (si empieza por postgres://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine_args = {}
# SQLite necesita este argumento específico para hilos, Postgres no
if DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
