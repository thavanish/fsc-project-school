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
STORAGE_BACKEND=local
STORAGE_FILE=data/faces.json
MATCH_THRESHOLD=0.55
AMBIGUITY_MARGIN=0.035
MAX_UPLOAD_BYTES=4300000
IMAGE_MAX_SIDE=960
REGISTER_JITTERS=2
QUERY_JITTERS=1
```

Free Render web services do not provide durable local file storage, so saved face registrations can disappear after restarts or redeploys. That is acceptable for a school demo, but not for a real face database. If you create the service manually instead, use `backend` as the root directory, `pip install -r requirements.txt` as the build command, and the `uvicorn` command above as the start command.

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
