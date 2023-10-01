from fastapi import APIRouter, Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from pyodbc import Cursor

from app.schemas import Token
from app.database import get_db
from app.jwt import create_access_token
from app.utils import verify_password

router = APIRouter(prefix="/login", tags=["Authentication"])


@router.post("/", response_model=Token)
def login(credentials: OAuth2PasswordRequestForm = Depends(), db: Cursor = Depends(get_db)):
    user = db.execute("SELECT * FROM users WHERE username = ?", credentials.username).fetchone()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid credentials")

    if not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=403, detail="Invalid credentials")

    token = create_access_token(
        data={
            "user_id": user.user_id,
        }
    )
    return {"access_token": token, "token_type": "bearer"}
