from pydantic import BaseModel,Field
import datetime

class Listing(BaseModel):
    platform: str
    timestamp: datetime.datetime
    search_term: str
    location: str
    mrp: int
    price: int
    unit: int
    brand: str
    name: str
    cat: str
    ad: bool
    rank: int

class Location(BaseModel):
    store_id: str
    locality: str
    longitude: float
    latitude: float
