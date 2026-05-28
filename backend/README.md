# Face Lab backend

FastAPI backend for the capstone face recognition demo.

## Local run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Vercel deploy

Create the Vercel project with `backend` as the project root. Vercel will use:

- `api/index.py` as the serverless FastAPI entrypoint
- `vercel.json` for routing, max duration, and bundle excludes
- `requirements.txt` for Python dependencies

For persistent registrations on Vercel, create a Vercel Blob store and connect it to the project. Vercel will provide `BLOB_READ_WRITE_TOKEN`. Without that token, serverless storage falls back to local files, which are not durable on Vercel.

Recommended environment variables:

```bash
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app,http://localhost:4321
STORAGE_BACKEND=auto
BLOB_READ_WRITE_TOKEN=your-vercel-blob-token
MATCH_THRESHOLD=0.55
AMBIGUITY_MARGIN=0.035
MAX_UPLOAD_BYTES=4300000
IMAGE_MAX_SIDE=960
REGISTER_JITTERS=2
QUERY_JITTERS=1
```

## Free plan notes

Vercel Functions accept request bodies up to 4.5 MB, so the backend rejects images over 4.3 MB before running the model. The function max duration is set to 60 seconds to avoid runaway requests on the free plan. The model uses HOG detection, resized input images, and one vectorized NumPy comparison pass for identify.
