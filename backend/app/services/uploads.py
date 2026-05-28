from fastapi import HTTPException, UploadFile

from app.config import get_settings


async def read_image_upload(image: UploadFile) -> bytes:
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Upload must be an image file")

    limit = get_settings().max_upload_bytes
    data = await image.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(
            status_code=413,
            detail="Image is too large for the Vercel function. Use a file under 4.3 MB.",
        )

    return data
