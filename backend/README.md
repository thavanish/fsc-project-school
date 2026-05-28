# Face Lab backend

FastAPI backend for the capstone face recognition demo.

## Local run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Render deploy

The repo root includes `render.yaml` for a Render Blueprint. It creates a free Python web service with `backend` as the root directory.

Manual Render settings:

- Root directory: `backend`
- Build command: `pip install -r requirements-render.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Recommended environment variables:

```bash
ALLOWED_ORIGINS=https://face.thavanish.dedyn.io,http://localhost:4321
STORAGE_BACKEND=blob
BLOB_PATH=face-db/faces.json
BLOB_READ_WRITE_TOKEN=your-vercel-blob-read-write-token
MATCH_THRESHOLD=0.55
AMBIGUITY_MARGIN=0.035
MAX_UPLOAD_BYTES=4300000
IMAGE_MAX_SIDE=960
REGISTER_JITTERS=2
QUERY_JITTERS=1
```

Free Render web services do not provide durable local file storage, so saved registrations are stored in Vercel Blob. Add `BLOB_READ_WRITE_TOKEN` manually in Render because the token is secret and is not stored in `render.yaml`.

`requirements-render.txt` skips `dlib` and `face_recognition` so Render free does not run out of memory during build. The app will use its lightweight fallback embedding on Render. Use `requirements.txt` for local development or a larger server that can install the native face recognition stack.

## Vercel Blob setup

1. In Vercel, open the project you want to use for storage.
2. Go to Storage and create a Blob database with Private access.
3. Open the Blob store settings and copy the read-write token.
4. In Render, add the token as `BLOB_READ_WRITE_TOKEN`.
5. Keep `STORAGE_BACKEND=blob` and `BLOB_PATH=face-db/faces.json`.
6. Redeploy Render.

## Free plan notes

Free web services can take a moment to wake after inactivity. The frontend waits for `GET /health` before it lets the user register, identify, or verify faces. The backend rejects images over 4.3 MB before running the model. The model uses HOG detection, resized input images, and one vectorized NumPy comparison pass for identify.
