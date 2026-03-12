from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api import brands
from app.api import documents
from app.api import posts

BASE_DIR = Path(__file__).resolve().parent  # → /app

app = FastAPI(
    title="Brand AI Post Generator",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create outputs dir if it doesn't exist, then mount it
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")

app.include_router(brands.router)
app.include_router(documents.router)
app.include_router(posts.router)


@app.get("/")
def root():
    return {
        "message": "Brand Post Generator API running"
    }