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
    confidence: float | None
    distance: float | None
    second_distance: float | None = None
    margin: float | None = None


class VerifyResponse(BaseModel):
    face1_detected: bool
    face2_detected: bool
    same_person: bool | None
    confidence: float | None
    distance: float | None


class ModelStatusResponse(BaseModel):
    status: str
    storage: str
    faces: int
    threshold: float
