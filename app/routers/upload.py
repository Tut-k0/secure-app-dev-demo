from datetime import datetime
from uuid import uuid4
from os.path import splitext

from fastapi import HTTPException, Depends, APIRouter, UploadFile, File
from pyodbc import Cursor
from azure.storage.blob import BlobClient

from app.config import config
from app.database import get_db
from app.schemas import UserData
from app.jwt import get_current_user

router = APIRouter(prefix="/uploads", tags=["File Uploading"])


@router.post("/listing/{listing_id}")
async def upload_listing_image(
    listing_id: int,
    file: UploadFile = File(...),
    db: Cursor = Depends(get_db),
    current_user: UserData = Depends(get_current_user),
):
    listing = db.execute("SELECT * FROM listings WHERE listing_id = ?", listing_id).fetchone()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if current_user.user_id != listing.seller_id:
        raise HTTPException(
            status_code=403, detail="You cannot upload images to listings that are not yours!"
        )

    blob_name = f"{uuid4()}{splitext(file.filename)[1]}"
    blob_url = (
        f"{config.azure_blob_storage_name}.blob.core.windows.net/"
        f"{config.azure_blob_container_name}/{blob_name}?{config.azure_blob_sas_token}"
    )
    blob_client = BlobClient.from_blob_url(blob_url)

    with file.file as f:
        blob_client.upload_blob(f, overwrite=True)

    db.execute(
        "INSERT INTO media_files (filename, blob_url, listing_id, file_type, upload_date) VALUES (?, ?, ?, ?, ?)",
        (file.filename, f"https://{blob_url}", listing_id, "image", datetime.utcnow()),
    )
    db.commit()

    return {"message": "File uploaded successfully"}


@router.post("/users/{user_id}")
async def upload_profile_picture(
    user_id: int,
    file: UploadFile = File(...),
    db: Cursor = Depends(get_db),
    current_user: UserData = Depends(get_current_user),
):
    user = db.execute("SELECT * FROM users WHERE user_id=?", user_id).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.user_id != user.user_id:
        raise HTTPException(status_code=403)

    blob_name = f"{uuid4()}{splitext(file.filename)[1]}"
    blob_url = (
        f"{config.azure_blob_storage_name}.blob.core.windows.net/"
        f"{config.azure_blob_container_name}/{blob_name}?{config.azure_blob_sas_token}"
    )
    blob_client = BlobClient.from_blob_url(blob_url)

    with file.file as f:
        blob_client.upload_blob(f, overwrite=True)

    db.execute(
        "INSERT INTO media_files (filename, blob_url, user_id, file_type, upload_date) VALUES (?, ?, ?, ?, ?)",
        (file.filename, f"https://{blob_url}", current_user.user_id, "image", datetime.utcnow()),
    )
    db.commit()

    return {"message": "Profile picture uploaded successfully."}
