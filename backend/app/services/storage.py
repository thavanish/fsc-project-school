import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from app.config import get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FaceIndex:
    names: list[str]
    matrix: np.ndarray


EMPTY_INDEX = FaceIndex(names=[], matrix=np.empty((0, 128), dtype=np.float32))


def _empty_payload() -> dict[str, Any]:
    return {"version": 2, "faces": []}


def _payload_to_index(payload: dict[str, Any]) -> FaceIndex:
    faces = payload.get("faces", [])
    rows: list[np.ndarray] = []
    names: list[str] = []

    for face in faces:
        name = str(face.get("name", "")).strip()
        embedding = face.get("embedding")
        if not name or not isinstance(embedding, list) or len(embedding) != 128:
            continue
        names.append(name)
        rows.append(np.asarray(embedding, dtype=np.float32))

    if not rows:
        return EMPTY_INDEX

    return FaceIndex(names=names, matrix=np.vstack(rows).astype(np.float32))


def _index_to_payload(index: FaceIndex) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    faces = [
        {
            "name": name,
            "embedding": index.matrix[pos].astype(float).round(7).tolist(),
            "updated_at": now,
        }
        for pos, name in enumerate(index.names)
    ]
    return {"version": 2, "updated_at": now, "faces": faces}


def _local_path() -> Path:
    if os.getenv("VERCEL"):
        return Path("/tmp/face-lab/faces.json")
    return Path(get_settings().storage_file)


async def _read_blob() -> dict[str, Any] | None:
    settings = get_settings()
    if not settings.blob_read_write_token:
        logger.error("BLOB_READ_WRITE_TOKEN is required when using Vercel Blob storage")
        return None

    try:
        from vercel.blob import AsyncBlobClient
    except Exception as exc:
        logger.warning("Vercel Blob SDK is not installed: %s", exc)
        return None

    try:
        client = AsyncBlobClient()
        result = await client.get(
            settings.blob_path,
            access="private",
            token=settings.blob_read_write_token,
        )
        if result is None or result.status_code != 200 or result.stream is None:
            return _empty_payload()

        chunks: list[bytes] = []
        async for chunk in result.stream:
            chunks.append(chunk)
        return json.loads(b"".join(chunks).decode("utf-8"))
    except Exception:
        logger.exception("Could not read Vercel Blob face index")
        return None


async def _write_blob(payload: dict[str, Any]) -> bool:
    settings = get_settings()
    if not settings.blob_read_write_token:
        logger.error("BLOB_READ_WRITE_TOKEN is required when using Vercel Blob storage")
        return False

    try:
        from vercel.blob import AsyncBlobClient
    except Exception as exc:
        logger.warning("Vercel Blob SDK is not installed: %s", exc)
        return False

    try:
        client = AsyncBlobClient()
        await client.put(
            settings.blob_path,
            json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            access="private",
            content_type="application/json",
            add_random_suffix=False,
            overwrite=True,
            cache_control_max_age=0,
            token=settings.blob_read_write_token,
        )
        return True
    except Exception:
        logger.exception("Could not write Vercel Blob face index")
        return False


def _read_local() -> dict[str, Any]:
    path = _local_path()
    if not path.exists():
        return _empty_payload()

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        logger.exception("Could not read local face index")
        return _empty_payload()


def _write_local(payload: dict[str, Any]) -> None:
    path = _local_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


async def load() -> FaceIndex:
    settings = get_settings()
    if settings.use_blob_storage:
        payload = await _read_blob()
        if payload is not None:
            return _payload_to_index(payload)
        if settings.require_blob_storage:
            raise RuntimeError("Blob storage is configured but the face index could not be read")
        logger.warning("Falling back to local storage after Blob read failure")

    return _payload_to_index(_read_local())


async def _save(index: FaceIndex) -> None:
    settings = get_settings()
    payload = _index_to_payload(index)
    if settings.use_blob_storage and await _write_blob(payload):
        return
    if settings.require_blob_storage:
        raise RuntimeError("Blob storage is configured but the face index could not be written")
    _write_local(payload)


async def add(name: str, encoding: np.ndarray) -> None:
    current = await load()
    clean_name = name.strip()
    rows = [current.matrix[pos] for pos, existing in enumerate(current.names) if existing != clean_name]
    names = [existing for existing in current.names if existing != clean_name]

    names.append(clean_name)
    rows.append(encoding.astype(np.float32))
    matrix = np.vstack(rows).astype(np.float32)
    await _save(FaceIndex(names=names, matrix=matrix))


async def remove(name: str) -> bool:
    current = await load()
    if name not in current.names:
        return False

    keep = [pos for pos, existing in enumerate(current.names) if existing != name]
    names = [current.names[pos] for pos in keep]
    matrix = current.matrix[keep] if keep else EMPTY_INDEX.matrix
    await _save(FaceIndex(names=names, matrix=matrix))
    return True


async def names() -> list[str]:
    return sorted((await load()).names)
