from pydantic import BaseModel
from typing import Tuple  # Import Tuple for location representation

class HousingData(BaseModel):
    id: int
    created_at: str                # Or datetime, depending on how you want to handle it
    crawler: str
    image: str                     # Image URL
    url: str                       # Property URL
    title: str                     # Property title
    price: float                   # Property price
    size: float                    # Property size
    rooms: int                     # Number of rooms
    address: str                   # Address
    lift: bool                     # Elevator presence
    pricebyarea: float            # Price per area
    district: str                  # District name
    bathrooms: int                 # Number of bathrooms
    status: str                    # Status of the property
    lat: float                     # Latitude
    long: float                    # Longitude
    location: Tuple[float, float]  # Representing location as (latitude, longitude)

    class Config:
        orm_mode = True  # Enables reading data from SQLAlchemy models