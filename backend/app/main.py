from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api import brands
from app.api import documents
from app.api import posts
from app.vector.qdrant_manager import qdrant_manager
from app.core.config import settings

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create collection on startup only if it does not already exist
    # Using exists check so restarts do not wipe ingested data
    if not qdrant_manager.client.collection_exists(settings.QDRANT_COLLECTION):
        qdrant_manager.recreate_collection()
    yield


app = FastAPI(
    title="Brand AI Post Generator",
    version="1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount outputs dir — render_service saves here, frontend loads from here
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")

app.include_router(brands.router)
app.include_router(documents.router)
app.include_router(posts.router)


@app.get("/")
def root():
    return {"message": "Brand Post Generator API running"}