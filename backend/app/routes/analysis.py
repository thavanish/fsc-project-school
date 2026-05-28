from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.schemas import IdentifyResponse, VerifyResponse
from app.services import recognition, storage

router = APIRouter()


@router.post("/identify", response_model=IdentifyResponse)
async def identify_face(
    image: UploadFile = File(..., description="Image of the person to identify"),
) -> IdentifyResponse:
    """
    One-to-many lookup: compares the uploaded face against everyone in the database
    and returns the closest match (if one clears the threshold).
    """
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Upload must be an image file")

    image_data = await image.read()
    encoding = recognition.get_face_encoding(image_data)

    if encoding is None:
        return IdentifyResponse(
            faces_detected=0,
            matched=False,
            name=None,
            confidence=None,
            distance=None,
        )

    known_faces = storage.load()
    name, distance = recognition.identify(encoding, known_faces)

    return IdentifyResponse(
        faces_detected=1,
        matched=name is not None,
        name=name,
        confidence=round(1.0 - distance, 4),
        distance=round(distance, 4),
    )


@router.post("/verify", response_model=VerifyResponse)
async def verify_faces(
    image1: UploadFile = File(..., description="First face image"),
    image2: UploadFile = File(..., description="Second face image"),
) -> VerifyResponse:
    """
    One-to-one comparison: checks whether the two uploaded photos show the same person.
    Doesn't need any registered faces — it compares the two images directly.
    """
    for img in [image1, image2]:
        if not img.content_type or not img.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Both uploads must be image files")

    data1 = await image1.read()
    data2 = await image2.read()

    enc1 = recognition.get_face_encoding(data1)
    enc2 = recognition.get_face_encoding(data2)

    if enc1 is None or enc2 is None:
        return VerifyResponse(
            face1_detected=enc1 is not None,
            face2_detected=enc2 is not None,
            same_person=None,
            confidence=None,
            distance=None,
        )

    same, distance = recognition.verify(enc1, enc2)

    return VerifyResponse(
        face1_detected=True,
        face2_detected=True,
        same_person=same,
        confidence=round(1.0 - distance, 4),
        distance=round(distance, 4),
    )
