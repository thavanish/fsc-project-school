# Facial Recognition Demo

Capstone project by **Thavanish. B** — XII B1, Maharishi Vidya Mandir, 2025–26.

The AI model converts faces into 128-dimensional embeddings using `face_recognition` (dlib under the hood) and compares them by Euclidean distance. The frontend is Astro, the backend is Python + FastAPI. Frontend deploys to Cloudflare Pages; backend deploys to Railway or Render.

---

## Features

- **Register** — add a named face to the database from any photo
- **Identify** — one-to-many lookup: search the database for the closest match
- **Verify** — one-to-one comparison: check whether two photos show the same person

---

## Project structure

```
facial-recognition-capstone/
├── backend/
│   ├── app/
│   │   ├── config.py            # settings (threshold, CORS origins)
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── models/schemas.py    # Pydantic response models
│   │   ├── services/
│   │   │   ├── recognition.py   # face detection + encoding + matching
│   │   │   └── storage.py       # pickle-based face database
│   │   └── routes/
│   │       ├── faces.py         # register / list / delete
│   │       └── analysis.py      # identify / verify
│   ├── data/                    # encodings.pkl lives here (git-ignored)
│   ├── Dockerfile
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── layouts/Base.astro
    │   ├── components/Nav.astro
    │   ├── pages/
    │   │   ├── index.astro
    │   │   ├── register.astro
    │   │   ├── identify.astro
    │   │   └── verify.astro
    │   └── styles/global.css
    ├── astro.config.mjs
    └── package.json
```

---

## Running locally

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# First install: dlib builds from source and takes ~10 minutes.
pip install dlib==19.24.2
pip install -r requirements.txt

cp .env.example .env             # edit ALLOWED_ORIGINS if needed
uvicorn app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs   (auto-generated API docs)
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env             # PUBLIC_API_URL=http://localhost:8000
npm run dev
# → http://localhost:4321
```

---

## Deploying

### Backend → Railway (or Render)

1. Push the `backend/` folder to a GitHub repo (or the whole repo and set root directory to `backend`).
2. Create a new project in [Railway](https://railway.app) and connect the repo.
3. Railway auto-detects the Dockerfile and builds it. The first build takes ~15 minutes because dlib compiles from source.
4. Add the `ALLOWED_ORIGINS` environment variable in Railway settings, pointing to your Cloudflare Pages URL.
5. Copy the Railway deployment URL — you'll need it for the frontend.

### Frontend → Cloudflare Pages

1. Push the `frontend/` folder to GitHub.
2. In the Cloudflare Pages dashboard, create a new project and connect the repo.
3. Build settings:
   - **Build command:** `npm run build`
   - **Output directory:** `dist`
4. Add an environment variable: `PUBLIC_API_URL` → your Railway backend URL.
5. Deploy.

---

## API reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/faces/register` | Register a face (form: `name`, `image`) |
| `GET`  | `/api/faces/` | List all registered names |
| `DELETE` | `/api/faces/{name}` | Remove a face by name |
| `POST` | `/api/identify` | Identify a face (form: `image`) |
| `POST` | `/api/verify` | Verify two faces (form: `image1`, `image2`) |
| `GET`  | `/health` | Health check |

Full interactive docs at `/docs` when the backend is running.

---

## How the model works

1. **Detection** — HOG-based face detector (fast enough for CPU, handles most real-world photos).
2. **Alignment** — key landmarks (eye corners, nose tip, mouth corners) are used to normalize orientation.
3. **Encoding** — a CNN produces a 128-dimensional embedding vector for the face.
4. **Matching** — Euclidean distance between embeddings. Threshold: 0.55 (slightly stricter than the `face_recognition` default of 0.6 to cut down false positives).

The same pipeline runs in Apple Face ID and most commercial systems — just at a much larger scale with more training data.

---

## Known limitations

- HOG detection struggles with non-frontal faces and low light. CNN mode (`model="cnn"`) is more robust but needs a GPU.
- The face database is stored as a single pickle file — fine for a demo, not for production.
- Accuracy varies across demographic groups (see the capstone report, Chapter 7) — the NIST FRVT studies documented gaps of 10–100x in false positive rates between demographic groups.

---

*Research support: Jai charan and Durgesh.*
