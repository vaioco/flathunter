# database.py - Set up the connection to PostgreSQL
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry





class DatabaseAlchemy:
    def __init__(self, dbname):
        self.SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://postgres:postgres@db:5432/{dbname}"
        self.engine = create_engine(self.SQLALCHEMY_DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = declarative_base()
