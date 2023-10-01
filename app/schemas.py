from pydantic import BaseModel, EmailStr


class ListingCreate(BaseModel):
    title: str
    description: str = None
    price: float


class Listing(BaseModel):
    listing_id: int
    title: str
    description: str
    price: float
    seller_id: int
    pictures: list[str] = []


class ListingUpdate(BaseModel):
    title: str
    description: str
    price: float


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserIdentifier(BaseModel):
    user_id: int


class UserOut(BaseModel):
    user_id: int
    email: EmailStr
    username: str
    profile_picture_url: str = None


class Token(BaseModel):
    access_token: str
    token_type: str
