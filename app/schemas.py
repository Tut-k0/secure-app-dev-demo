from pydantic import BaseModel, EmailStr


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


class ListingUpdate(BaseModel):
    title: str
    description: str
    price: float


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserData(BaseModel):
    user_id: int
    username: str
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
