# Facial Recognition Demo

Capstone project by Thavanish B, XII B1, Maharishi Vidya Mandir, 2025 to 2026.

The backend turns faces into 128-dimensional embeddings with `face_recognition` and compares them with a vectorized NumPy distance pass. The frontend is Astro. The backend is FastAPI and is intended to run as a Render web service.

## Features

- Register a named face from a clear photo.
- Identify the closest saved face for a new photo.
- Verify whether two photos show the same person.

## Project structure

```text
facial-recognition-capstone/
  render.yaml                 # Render backend Blueprint
  backend/
    api/index.py              # Vercel Python entrypoint
    app/
      config.py               # settings, thresholds, storage mode
      main.py                 # FastAPI app
      models/schemas.py       # response models
      services/
        recognition.py        # image prep, encoding, matching
        storage.py            # local JSON or Vercel Blob face index
        uploads.py            # upload validation
      routes/
        faces.py              # register, list, delete
        analysis.py           # identify, verify
    data/                     # local faces.json, git ignored
    requirements.txt
    requirements-render.txt   # lightweight Render free-tier install
  frontend/
    src/
      layouts/Base.astro
      components/Nav.astro
      pages/
      styles/global.css
```

## Running locally

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/docs` for the API docs.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `PUBLIC_API_URL=http://localhost:8000` in `frontend/.env` for local backend calls.

## Deploying

### Backend on Render

The repo includes `render.yaml` for a Render Blueprint. It deploys `backend/` as a free Python web service. It runs:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Create a Render Blueprint from this repository, then confirm these environment variables:

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

Free Render web services do not provide durable local file storage, so this deployment stores the face index in Vercel Blob instead. If you create the service manually, use `backend` as the root directory, `pip install -r requirements-render.txt` as the build command, and the `uvicorn` command above as the start command. Add `BLOB_READ_WRITE_TOKEN` manually in Render because `render.yaml` cannot contain the secret value.

`requirements-render.txt` skips `dlib` and `face_recognition` so the free Render build does not run out of memory. The backend stays online with its lightweight fallback embedding. For local development or a paid server with more build memory, use `requirements.txt` to install the real face recognition stack.

### Vercel Blob storage

1. In Vercel, open the project that owns the Blob store.
2. Go to Storage, create a Blob database, and choose Private access.
3. Open the Blob store settings and copy the read-write token.
4. In Render, set `BLOB_READ_WRITE_TOKEN` to that token and keep `STORAGE_BACKEND=blob`.
5. Redeploy Render, then register a face and restart the service. The saved name should still appear because `face-db/faces.json` is loaded from Blob.

### Frontend

Deploy the frontend separately and set `PUBLIC_API_URL` to the Render backend URL. The frontend waits on `GET /health` before enabling registration, identification, or verification.

## API reference

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/faces/register` | Register a face with `name` and `image` |
| `GET` | `/api/faces/` | List saved names |
| `DELETE` | `/api/faces/{name}` | Remove a saved face |
| `POST` | `/api/identify` | Identify one uploaded face |
| `POST` | `/api/verify` | Compare two uploaded faces |
| `GET` | `/health` | Health check with storage and face count |

## Model notes

The backend resizes large images before detection, applies EXIF orientation, picks the largest centered face when multiple faces are present, and uses extra jitter while registering to get a steadier embedding. Identify uses one NumPy matrix comparison instead of looping through saved faces one by one.

This is still a capstone demo. It is not a production biometric system.
