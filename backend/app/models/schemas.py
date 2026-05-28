from pydantic import BaseModel


class RegisterResponse(BaseModel):
    success: bool
    name: str
    message: str


class FaceListResponse(BaseModel):
    faces: list[str]
    count: int


class DeleteResponse(BaseModel):
    success: bool
    message: str


class IdentifyResponse(BaseModel):
    faces_detected: int
    matched: bool
    name: str | None
    # confidence is 1 - distance, so higher = more similar
    confidence: float | None
    distance: float | None


class VerifyResponse(BaseModel):
    face1_detected: bool
    face2_detected: bool
    # None when a face couldn't be detected in one of the images
    same_person: bool | None
    confidence: float | None
    distance: float | None
