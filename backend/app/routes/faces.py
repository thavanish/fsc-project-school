from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.schemas import DeleteResponse, FaceListResponse, RegisterResponse
from app.services import recognition, storage

router = APIRouter()


@router.post("/register", response_model=RegisterResponse)
async def register_face(
    name: str = Form(..., description="Name to associate with this face"),
    image: UploadFile = File(..., description="Photo containing the face to register"),
) -> RegisterResponse:
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Upload must be an image file")

    image_data = await image.read()
    encoding = recognition.get_face_encoding(image_data)

    if encoding is None:
        raise HTTPException(
            status_code=422,
            detail=(
                "No face detected in the image. "
                "Make sure the face is clearly visible, well-lit, and not too small."
            ),
        )

    clean_name = name.strip()
    storage.add(clean_name, encoding)

    return RegisterResponse(
        success=True,
        name=clean_name,
        message=f"'{clean_name}' has been registered.",
    )


@router.get("/", response_model=FaceListResponse)
def list_faces() -> FaceListResponse:
    face_names = storage.names()
    return FaceListResponse(faces=face_names, count=len(face_names))


@router.delete("/{name}", response_model=DeleteResponse)
def delete_face(name: str) -> DeleteResponse:
    removed = storage.remove(name)
    if not removed:
        raise HTTPException(
            status_code=404,
            detail=f"No face found with the name '{name}'",
        )
    return DeleteResponse(success=True, message=f"'{name}' removed from the database.")
