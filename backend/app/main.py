import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import analysis, faces
from app.services import storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()
logger.info("CORS origins: %s", settings.allowed_origin_list)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Face Lab API with %s storage", "blob" if settings.use_blob_storage else "local")
    yield
    logger.info("Stopping Face Lab API")


app = FastAPI(
    title="Face Lab API",
    description="Backend for Thavanish B's facial recognition capstone.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(faces.router, prefix="/api/faces", tags=["faces"])
app.include_router(analysis.router, prefix="/api", tags=["analysis"])


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    index = await storage.load()
    return {
        "status": "ok",
        "storage": "blob" if settings.use_blob_storage else "local",
        "faces": len(index.names),
        "threshold": settings.match_threshold,
    }
