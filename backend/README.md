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

The repo root includes `render.yaml` for a Render Blueprint. It creates a Python web service with `backend` as the root directory. The Blueprint uses Render's `starter` plan because saved face registrations need a persistent disk.

Manual Render settings:

- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Recommended environment variables:

```bash
ALLOWED_ORIGINS=https://face.thavanish.dedyn.io,http://localhost:4321
STORAGE_BACKEND=local
STORAGE_FILE=/var/data/faces.json
MATCH_THRESHOLD=0.55
AMBIGUITY_MARGIN=0.035
MAX_UPLOAD_BYTES=4300000
IMAGE_MAX_SIDE=960
REGISTER_JITTERS=2
QUERY_JITTERS=1
```

For persistent registrations, attach a Render disk at `/var/data`. The included Blueprint does this with a 1 GB disk. If you must use a free web service, remove the disk and expect local registrations to disappear after restarts.

## Free plan notes

Free web services can take a moment to wake after inactivity. The frontend waits for `GET /health` before it lets the user register, identify, or verify faces. The backend rejects images over 4.3 MB before running the model. The model uses HOG detection, resized input images, and one vectorized NumPy comparison pass for identify.
