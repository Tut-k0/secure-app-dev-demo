from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pyodbc import Cursor

from app.config import config
from app.database import get_db
from app.schemas import UserData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/")

SECRET_KEY = config.secret_key
ALGORITHM = config.algorithm
TOKEN_EXPIRE_MINUTES = config.token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return token


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)

        id: str = payload.get("user_id")

        if not id:
            raise credentials_exception
        token_data = UserData(id=id)
    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Cursor = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = verify_access_token(token, credentials_exception)
    user = db.execute("SELECT * FROM users WHERE user_id = ?", token.user_id).fetchone()

    return UserData(
        user_id=user.user_id, username=user.username, email=user.email, password=user.password
    )
