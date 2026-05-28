import logging
import pickle
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

STORAGE_FILE = Path("data/encodings.pkl")


def load() -> dict[str, np.ndarray]:
    """Read all stored face encodings from disk. Returns empty dict if none saved yet."""
    if not STORAGE_FILE.exists():
        return {}
    try:
        with open(STORAGE_FILE, "rb") as f:
            return pickle.load(f)
    except Exception:
        logger.exception("Could not read encodings file — returning empty")
        return {}


def _save(faces: dict[str, np.ndarray]) -> None:
    STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_FILE, "wb") as f:
        pickle.dump(faces, f)


def add(name: str, encoding: np.ndarray) -> None:
    """Add or overwrite a face encoding by name."""
    faces = load()
    faces[name] = encoding
    _save(faces)
    logger.info("Saved encoding for '%s' (%d total)", name, len(faces))


def remove(name: str) -> bool:
    """Delete a face by name. Returns False if the name wasn't in the database."""
    faces = load()
    if name not in faces:
        return False
    del faces[name]
    _save(faces)
    logger.info("Removed '%s'", name)
    return True


def names() -> list[str]:
    """Return the list of registered face names, sorted alphabetically."""
    return sorted(load().keys())
