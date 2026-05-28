import io
import logging
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

from app.config import get_settings

logger = logging.getLogger(__name__)


class RecognitionError(RuntimeError):
    pass


class ImageDecodeError(ValueError):
    pass


@dataclass(frozen=True)
class FaceEncodingResult:
    encoding: np.ndarray | None
    faces_detected: int


@dataclass(frozen=True)
class MatchResult:
    matched: bool
    name: str | None
    distance: float | None
    confidence: float | None
    second_distance: float | None
    margin: float | None


@lru_cache(maxsize=1)
def _face_recognition():
    try:
        import face_recognition
    except Exception as exc:
        raise RecognitionError(
            "The face_recognition stack is not installed. Install dlib-bin, "
            "face-recognition-models, and face-recognition in this environment."
        ) from exc
    return face_recognition


def _bytes_to_rgb_array(data: bytes) -> np.ndarray:
    try:
        image = Image.open(io.BytesIO(data))
        image = ImageOps.exif_transpose(image).convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise ImageDecodeError("Upload must be a readable image file") from exc

    max_side = get_settings().image_max_side
    longest_side = max(image.size)
    if longest_side > max_side:
        ratio = max_side / longest_side
        resized = (max(1, int(image.width * ratio)), max(1, int(image.height * ratio)))
        image = image.resize(resized, Image.Resampling.LANCZOS)

    return np.asarray(image)


def _primary_face(locations: list[tuple[int, int, int, int]], shape: tuple[int, ...]) -> tuple[int, int, int, int]:
    image_h, image_w = shape[:2]
    center_y = image_h / 2
    center_x = image_w / 2

    def score(location: tuple[int, int, int, int]) -> float:
        top, right, bottom, left = location
        area = max(1, bottom - top) * max(1, right - left)
        face_y = (top + bottom) / 2
        face_x = (left + right) / 2
        center_penalty = ((face_x - center_x) / image_w) ** 2 + ((face_y - center_y) / image_h) ** 2
        return area * (1.0 - min(center_penalty, 0.85))

    return max(locations, key=score)


def get_face_encoding(image_data: bytes, *, purpose: str = "query") -> FaceEncodingResult:
    settings = get_settings()
    face_recognition = _face_recognition()
    image = _bytes_to_rgb_array(image_data)

    locations = face_recognition.face_locations(
        image,
        number_of_times_to_upsample=settings.detection_upsample,
        model="hog",
    )
    if not locations:
        logger.info("No face detected")
        return FaceEncodingResult(encoding=None, faces_detected=0)

    primary = _primary_face(locations, image.shape)
    jitters = settings.register_jitters if purpose == "register" else settings.query_jitters
    encodings = face_recognition.face_encodings(
        image,
        known_face_locations=[primary],
        num_jitters=jitters,
        model=settings.face_model,
    )
    if not encodings:
        return FaceEncodingResult(encoding=None, faces_detected=len(locations))

    encoding = np.asarray(encodings[0], dtype=np.float32)
    return FaceEncodingResult(encoding=encoding, faces_detected=len(locations))


def confidence_from_distance(distance: float) -> float:
    return round(max(0.0, min(1.0, 1.0 - distance)), 4)


def identify(
    unknown: np.ndarray,
    names: list[str],
    matrix: np.ndarray,
    *,
    threshold: float | None = None,
    ambiguity_margin: float | None = None,
) -> MatchResult:
    settings = get_settings()
    threshold = settings.match_threshold if threshold is None else threshold
    ambiguity_margin = settings.ambiguity_margin if ambiguity_margin is None else ambiguity_margin

    if not names or matrix.size == 0:
        return MatchResult(False, None, None, None, None, None)

    distances = np.linalg.norm(matrix - unknown.astype(np.float32), axis=1)
    best_index = int(np.argmin(distances))
    best_distance = float(distances[best_index])

    if len(distances) > 1:
        partition = np.partition(distances, 1)
        second_distance = float(partition[1])
        margin = second_distance - best_distance
    else:
        second_distance = None
        margin = None

    clear_threshold = best_distance <= threshold
    clear_margin = margin is None or margin >= ambiguity_margin
    matched = clear_threshold and clear_margin

    return MatchResult(
        matched=matched,
        name=names[best_index] if matched else None,
        distance=best_distance,
        confidence=confidence_from_distance(best_distance),
        second_distance=second_distance,
        margin=margin,
    )


def verify(enc1: np.ndarray, enc2: np.ndarray, threshold: float | None = None) -> tuple[bool, float, float]:
    settings = get_settings()
    threshold = settings.match_threshold if threshold is None else threshold
    distance = float(np.linalg.norm(enc1.astype(np.float32) - enc2.astype(np.float32)))
    return distance <= threshold, distance, confidence_from_distance(distance)
