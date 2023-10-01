from fastapi import HTTPException, Depends, APIRouter, Response
from pyodbc import Cursor

from app.database import get_db
from app.schemas import UserCreate, UserIdentifier, UserOut
from app.jwt import get_current_user
from app.utils import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=201)
def create_user(user: UserCreate, db: Cursor = Depends(get_db)):
    existing_user = db.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?", (user.username, user.email)
    ).fetchone()
    if existing_user and existing_user.username == user.username:
        raise HTTPException(
            status_code=409, detail=f"A user already has the username {existing_user.username}!"
        )
    if existing_user and existing_user.email == user.email:
        raise HTTPException(
            status_code=409, detail=f"A user already has the email {existing_user.email}!"
        )
    # Add password hashing with bcrypt
    user.password = hash_password(user.password)

    db.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        (user.username, user.email, user.password),
    )
    db.commit()

    return Response(status_code=201)


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Cursor = Depends(get_db),
    current_user: UserIdentifier = Depends(get_current_user),
):
    user = db.execute(
        "SELECT user_id, username, email FROM users WHERE user_id = ?", user_id
    ).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist!")

    # Retrieve the profile picture URL associated with the user
    profile_picture_url = db.execute(
        "SELECT blob_url FROM media_files WHERE user_id = ? AND file_type = 'image'",
        user_id,
    ).fetchone()

    # Include the profile picture URL in the response
    return UserOut(
        user_id=user.user_id,
        email=user.email,
        username=user.username,
        profile_picture_url=profile_picture_url.blob_url,
    )
