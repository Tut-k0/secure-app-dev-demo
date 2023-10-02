from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, Depends, APIRouter, UploadFile, File
from pyodbc import Cursor
from azure.storage.blob import BlobClient

from app.config import config
from app.database import get_db
from app.schemas import UserIdentifier
from app.jwt import get_current_user

router = APIRouter(prefix="/uploads", tags=["File Uploading"])


def is_valid_image(magic_bytes: bytes) -> bool:
    # Define magic byte signatures for JPEG and PNG
    jpeg_signature = b"\xFF\xD8\xFF"
    png_signature = b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"

    return (
        magic_bytes.startswith(jpeg_signature) or
        magic_bytes.startswith(png_signature)
    )


@router.post("/listing/{listing_id}")
async def upload_listing_image(
    listing_id: int,
    file: UploadFile = File(...),
    db: Cursor = Depends(get_db),
    current_user: UserIdentifier = Depends(get_current_user),
):
    listing = db.execute("SELECT * FROM listings WHERE listing_id = ?", listing_id).fetchone()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if current_user.user_id != listing.seller_id:
        raise HTTPException(
            status_code=403, detail="You cannot upload images to listings that are not yours!"
        )

    # Check file extension
    allowed_extensions = {"jpeg", "jpg", "png"}
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only JPEG and PNG files are allowed.",
        )

    # Check file size
    max_file_size_bytes = 10 * 1024 * 1024  # 10 MB
    if file.file.tell() > max_file_size_bytes:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds the allowed limit. Please upload a smaller file.",
        )

    # Read the first bytes of the file for magic byte validation
    max_magic_bytes_length = max(len(b"\xFF\xD8\xFF"), len(b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"))
    file_magic_bytes = await file.read(max_magic_bytes_length)

    # Check content type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid content type. Only image files are allowed.",
        )

    # Check magic bytes to validate image format
    if not is_valid_image(file_magic_bytes):
        raise HTTPException(
            status_code=400,
            detail="Invalid image format. Only JPEG and PNG images are allowed.",
        )

    # Continue with the upload process
    blob_name = f"{uuid4()}.{file_extension}"
    blob_url = (
        f"{config.azure_blob_storage_name}.blob.core.windows.net/"
        f"{config.azure_blob_container_name}/{blob_name}?{config.azure_blob_sas_token}"
    )
    blob_client = BlobClient.from_blob_url(blob_url)

    # Reset the file pointer before uploading
    await file.seek(0)

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
    current_user: UserIdentifier = Depends(get_current_user),
):
    user = db.execute("SELECT * FROM users WHERE user_id=?", user_id).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.user_id != user.user_id:
        raise HTTPException(status_code=403)

    # Check file extension
    allowed_extensions = {"jpeg", "jpg", "png"}
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only JPEG and PNG files are allowed.",
        )
    # Check file size
    max_file_size_bytes = 10 * 1024 * 1024  # 10 MB
    if file.file.tell() > max_file_size_bytes:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds the allowed limit. Please upload a smaller file.",
        )
    # Read the first bytes of the file for magic byte validation
    max_magic_bytes_length = max(len(b"\xFF\xD8\xFF"), len(b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"))
    file_magic_bytes = await file.read(max_magic_bytes_length)
    # Check content type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid content type. Only image files are allowed.",
        )
    # Check magic bytes to validate image format
    if not is_valid_image(file_magic_bytes):
        raise HTTPException(
            status_code=400,
            detail="Invalid image format. Only JPEG and PNG images are allowed.",
        )
    # Continue with the upload process
    blob_name = f"{uuid4()}.{file_extension}"
    blob_url = (
        f"{config.azure_blob_storage_name}.blob.core.windows.net/"
        f"{config.azure_blob_container_name}/{blob_name}?{config.azure_blob_sas_token}"
    )
    blob_client = BlobClient.from_blob_url(blob_url)

    # Reset the file pointer before uploading
    await file.seek(0)

    with file.file as f:
        blob_client.upload_blob(f, overwrite=True)

    db.execute(
        "INSERT INTO media_files (filename, blob_url, user_id, file_type, upload_date) VALUES (?, ?, ?, ?, ?)",
        (file.filename, f"https://{blob_url}", current_user.user_id, "image", datetime.utcnow()),
    )
    db.commit()

    return {"message": "Profile picture uploaded successfully."}
