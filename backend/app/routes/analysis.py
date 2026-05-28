from fastapi import APIRouter, File, UploadFile

from app.models.schemas import IdentifyResponse, VerifyResponse
from app.services import recognition, storage
from app.services.uploads import read_image_upload

router = APIRouter()


@router.post("/identify", response_model=IdentifyResponse)
async def identify_face(
    image: UploadFile = File(..., description="Image of the person to identify"),
) -> IdentifyResponse:
    image_data = await read_image_upload(image)
    result = recognition.get_face_encoding(image_data, purpose="query")

    if result.encoding is None:
        return IdentifyResponse(
            faces_detected=result.faces_detected,
            matched=False,
            name=None,
            confidence=None,
            distance=None,
        )

    known_faces = await storage.load()
    match = recognition.identify(result.encoding, known_faces.names, known_faces.matrix)

    return IdentifyResponse(
        faces_detected=result.faces_detected,
        matched=match.matched,
        name=match.name,
        confidence=match.confidence,
        distance=round(match.distance, 4) if match.distance is not None else None,
        second_distance=round(match.second_distance, 4) if match.second_distance is not None else None,
        margin=round(match.margin, 4) if match.margin is not None else None,
    )


@router.post("/verify", response_model=VerifyResponse)
async def verify_faces(
    image1: UploadFile = File(..., description="First face image"),
    image2: UploadFile = File(..., description="Second face image"),
) -> VerifyResponse:
    data1 = await read_image_upload(image1)
    data2 = await read_image_upload(image2)

    face1 = recognition.get_face_encoding(data1, purpose="query")
    face2 = recognition.get_face_encoding(data2, purpose="query")

    if face1.encoding is None or face2.encoding is None:
        return VerifyResponse(
            face1_detected=face1.encoding is not None,
            face2_detected=face2.encoding is not None,
            same_person=None,
            confidence=None,
            distance=None,
        )

    same, distance, confidence = recognition.verify(face1.encoding, face2.encoding)

    return VerifyResponse(
        face1_detected=True,
        face2_detected=True,
        same_person=same,
        confidence=confidence,
        distance=round(distance, 4),
    )
