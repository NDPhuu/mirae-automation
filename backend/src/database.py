import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv(override=True)

# Require DATABASE_URL in .env (e.g. postgresql+psycopg2://user:pass@host:port/dbname)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("WARNING: DATABASE_URL is not set in .env. Database connection will fail.")

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_timeout=60,
    pool_recycle=1800
) if DATABASE_URL else None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None

Base = declarative_base()

def get_db():
    if not SessionLocal:
        raise RuntimeError("Database connection is not configured.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
