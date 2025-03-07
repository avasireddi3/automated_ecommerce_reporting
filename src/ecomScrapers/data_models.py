from pydantic import BaseModel,Field
import datetime

class Listing(BaseModel):
    platform: str
    timestamp: datetime.datetime
    search_term: str
    location: str
    mrp: int
    price: int
    unit: str
    brand: str
    name: str
    cat: str
    ad: bool
    rank: int

