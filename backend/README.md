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
STORAGE_BACKEND=local
STORAGE_FILE=data/faces.json
MATCH_THRESHOLD=0.55
AMBIGUITY_MARGIN=0.035
MAX_UPLOAD_BYTES=4300000
IMAGE_MAX_SIDE=960
REGISTER_JITTERS=2
QUERY_JITTERS=1
```

Free Render web services do not provide durable local file storage, so saved registrations can disappear after restarts or redeploys. For a school demo this is usually fine. For a real persistent database, use a paid disk or an external storage service.

`requirements-render.txt` skips `dlib` and `face_recognition` so Render free does not run out of memory during build. The app will use its lightweight fallback embedding on Render. Use `requirements.txt` for local development or a larger server that can install the native face recognition stack.

## Free plan notes

Free web services can take a moment to wake after inactivity. The frontend waits for `GET /health` before it lets the user register, identify, or verify faces. The backend rejects images over 4.3 MB before running the model. The model uses HOG detection, resized input images, and one vectorized NumPy comparison pass for identify.
