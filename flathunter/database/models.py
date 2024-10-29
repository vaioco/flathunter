from sqlalchemy import Column, Integer, Float, String, Numeric, Boolean, TIMESTAMP, Text
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class Housing(Base):
    __tablename__ = 'flats'  # Ensure this matches your table name

    id = Column(Integer, primary_key=True)
    created_at = Column(TIMESTAMP)  # to store the creation date
    crawler = Column(String(255))  # to store the crawler name
    json_data = Column(JSONB)  # to store the JSON data
    image = Column(String(255))  # to store image URL
    url = Column(String(255))  # to store the URL
    title = Column(Text)  # to store the title
    price = Column(Numeric)  # to store the price
    size = Column(Numeric)  # to store the size
    rooms = Column(Integer)  # to store the number of rooms
    address = Column(String(255))  # to store the address
    lift = Column(Boolean)  # to store elevator availability
    pricebyarea = Column(Numeric)  # to store the price per square meter
    district = Column(String(255))  # to store the district
    bathrooms = Column(Integer)  # to store the number of bathrooms
    status = Column(String(50))  # to store the status
    location = Column(Geometry(geometry_type='POINT', srid=4326))  # to store geographic coordinates
    lat = Column(Float)  # to store latitude
    long = Column(Float)  # to store longitude

    def __repr__(self):
        return f"<Housing(id={self.id}, title={self.title}, size={self.size}, price={self.price}, address={self.address})>"

# Define additional models for tables not covered by Housing
class Processed(Base):
    __tablename__ = 'processed'
    id = Column(Integer, primary_key=True, autoincrement=True)

class Execution(Base):
    __tablename__ = 'executions'
    timestamp = Column(TIMESTAMP, primary_key=True)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    settings = Column(JSONB)


