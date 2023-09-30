from pydantic import BaseModel


class ListingCreate(BaseModel):
    title: str
    description: str = None
    price: float
    seller_id: int


class Listing(BaseModel):
    listing_id: int
    title: str
    description: str
    price: float
    seller_id: int
