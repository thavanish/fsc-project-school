import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import analysis, faces

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)s  %(levelname)s  %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting — face encodings will load from disk on first request")
    yield
    logger.info("Shutting down")


settings = get_settings()

app = FastAPI(
    title="Facial Recognition API",
    description="Backend for Thavanish's facial recognition capstone (XII B1, MVM 2025–26).",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(faces.router, prefix="/api/faces", tags=["faces"])
app.include_router(analysis.router, prefix="/api", tags=["analysis"])


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok"}
