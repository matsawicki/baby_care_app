from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
import urllib.parse


load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = urllib.parse.quote_plus(os.getenv("POSTGRES_PASSWORD"))
DB_HOST = os.getenv("DATABASE_URL")
DB_PORT = os.getenv("DATABASE_PORT")
DB_NAME = os.getenv("POSTGRES_DB")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal is configured with the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for ORM models
Base = declarative_base()


# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
