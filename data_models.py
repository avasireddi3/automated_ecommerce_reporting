from pydantic import BaseModel,Field

class Listing(BaseModel):
    mrp: int
    price: int
    unit: str
    brand: str
    name: str
    cat: str
