import io
import logging

import face_recognition
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# Slightly below the library default of 0.6.
# Catches more false positives without a noticeable hit to true matches.
DEFAULT_THRESHOLD = 0.55


def _bytes_to_rgb_array(data: bytes) -> np.ndarray:
    """Open image bytes and convert to an RGB numpy array face_recognition expects."""
    img = Image.open(io.BytesIO(data)).convert("RGB")
    return np.array(img)


def get_face_encoding(image_data: bytes) -> np.ndarray | None:
    """
    Detect a face in the image and return its 128-d encoding.

    Returns None if no face is found. If multiple faces show up,
    we take the largest bounding box — that's usually the subject.
    """
    img = _bytes_to_rgb_array(image_data)
    locations = face_recognition.face_locations(img, model="hog")

    if not locations:
        logger.info("No face detected in image")
        return None

    if len(locations) > 1:
        logger.info("Multiple faces found (%d), picking the largest", len(locations))
        # bounding box format is (top, right, bottom, left)
        locations = [max(locations, key=lambda loc: (loc[2] - loc[0]) * (loc[1] - loc[3]))]

    encodings = face_recognition.face_encodings(img, locations)
    return encodings[0] if encodings else None


def identify(
    unknown: np.ndarray,
    known_faces: dict[str, np.ndarray],
    threshold: float = DEFAULT_THRESHOLD,
) -> tuple[str | None, float]:
    """
    Compare an unknown encoding against every stored face.

    Returns the best match name and its distance. Name is None if the
    closest match still doesn't clear the threshold.
    """
    if not known_faces:
        return None, 1.0

    names = list(known_faces.keys())
    stored_encodings = list(known_faces.values())

    distances = face_recognition.face_distance(stored_encodings, unknown)
    best_idx = int(np.argmin(distances))
    best_distance = float(distances[best_idx])

    if best_distance < threshold:
        return names[best_idx], best_distance

    return None, best_distance


def verify(
    enc1: np.ndarray,
    enc2: np.ndarray,
    threshold: float = DEFAULT_THRESHOLD,
) -> tuple[bool, float]:
    """
    One-to-one comparison between two face encodings.

    Returns (same_person, distance). Lower distance = more similar faces.
    """
    distance = float(face_recognition.face_distance([enc1], enc2)[0])
    return distance < threshold, distance
